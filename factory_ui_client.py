import sys
import socket
import collections
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import QThread, Signal, Slot
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# 네트워크 통신을 담당할 백그라운드 스레드 (UI 멈춤 방지)
class SocketThread(QThread):
    # 외부로 데이터를 전달할 시그널 정의
    data_received = Signal(float)
    error_occurred = Signal(str)

    def __init__(self, host='127.0.0.1', port=9999):
        super().__init__()
        self.host = host
        self.port = port
        self.running = True

    def run(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((self.host, self.port))
            while self.running:
                data = client_socket.recv(1024)
                if not data:
                    self.error_occurred.emit("서버 원격 연결 종료")
                    break
                
                # 수신된 문자열 데이터 파싱 (버퍼에 여러 줄이 올 수 있으므로 split 사용)
                lines = data.decode('utf-8').strip().split('\n')
                for line in lines:
                    line = line.strip()
                    if line:
                        try:
                            temp = float(line)
                            self.data_received.emit(temp)
                        except ValueError:
                            pass # 변환 불가능한 값은 무시
        except ConnectionRefusedError:
            self.error_occurred.emit("연결 거부: 서버가 켜져 있는지 확인하세요.")
        except Exception as e:
            self.error_occurred.emit(f"네트워크 오류: {e}")
        finally:
            client_socket.close()

    def stop(self):
        self.running = False
        self.wait()

# 메인 UI 창
class RealTimePlotWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("공장 설비 실시간 온도 모니터링 (UI)")
        self.resize(800, 600)

        # 메인 위젯 레이아웃 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 상태 표시 라벨
        self.status_label = QLabel("상태: 모니터링 대기 중...")
        # 폰트 굵게 시각 효과
        font = self.status_label.font()
        font.setPointSize(12)
        font.setBold(True)
        self.status_label.setFont(font)
        layout.addWidget(self.status_label)

        # Matplotlib Figure 및 Canvas 생성 후 레이아웃에 추가
        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # 차트(Ax) 설정
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title("실시간 온도 변화")
        self.ax.set_xlabel("시간 (최근 데이터 포인트)")
        self.ax.set_ylabel("온도 (°C)")
        
        # 49.0 ~ 51.0 데이터 위주이므로 조금 더 여유있게 Y축 설정
        self.ax.set_ylim(48.5, 51.5) 
        self.ax.grid(True)

        # 차트 선 초기화 (빨간색 선, 동그라미 마커)
        self.line, = self.ax.plot([], [], 'r-', marker='o', markersize=4, linewidth=2)

        # 표출할 데이터 저장소 (과부하 방지를 위해 최대 60개(약 1분 어치)까지만 유지)
        self.max_points = 60
        self.x_data = collections.deque(maxlen=self.max_points)
        self.y_data = collections.deque(maxlen=self.max_points)
        self.count = 0

        # 백그라운드 소켓 스레드 세팅 및 시작
        self.socket_thread = SocketThread()
        self.socket_thread.data_received.connect(self.update_plot)
        self.socket_thread.error_occurred.connect(self.handle_error)
        self.socket_thread.start()

    # 스레드에서 시그널(데이터)이 넘어올 때마다 호출되는 함수
    @Slot(float)
    def update_plot(self, temperature):
        self.status_label.setText(f"상태: 정상 통신 중 | 현재 온도: {temperature:.2f} °C")
        self.status_label.setStyleSheet("color: green;")
        
        self.count += 1
        self.x_data.append(self.count)
        self.y_data.append(temperature)

        # 차트 선 업데이트
        self.line.set_data(self.x_data, self.y_data)
        
        # 데이터가 많아지면 X축 범위 동적 조절 (오른쪽으로 이동 효과)
        self.ax.set_xlim(max(0, self.count - self.max_points), self.count + 1)
        
        # 캔버스 갱신
        self.canvas.draw()

    # 오류 발생 시 UI 처리
    @Slot(str)
    def handle_error(self, error_msg):
        self.status_label.setText(f"상태: 오류 발생 - {error_msg}")
        self.status_label.setStyleSheet("color: red;")

    def closeEvent(self, event):
        # 창 우상단 X 버튼을 누를 때 스레드도 안전하게 종료
        self.socket_thread.stop()
        event.accept()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = RealTimePlotWindow()
    window.show()
    sys.exit(app.exec())


    


            

