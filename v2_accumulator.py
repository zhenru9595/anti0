import sys
import socket
import os
import collections
from datetime import datetime
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import QThread, Signal, Slot, QTimer
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'Malgun Gothic'

class DataReceiver(QThread):
    new_data = Signal(float, str) # value, timestamp
    def run(self):
        while True:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                # 서버가 준비될 때까지 1초마다 재연결 시도
                s.connect(('127.0.0.1', 9998))
                while True:
                    data = s.recv(1024)
                    if not data: break
                    now = datetime.now()
                    for line in data.decode('utf-8').split('\n'):
                        if line.strip():
                            self.new_data.emit(float(line.strip()), now.strftime('%Y-%m-%d %H:%M:%S'))
            except:
                import time
                time.sleep(1)
            finally: 
                s.close()

class AccumulatorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("데이터 축적기 (10분 그래프 + 파일 저장)")
        self.resize(800, 500)
        
        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QVBoxLayout(widget)
        
        self.lbl = QLabel("상태: 서버 연결 대기 중...")
        self.lbl.setStyleSheet("font-size: 14px; font-weight: bold; color: #555;")
        layout.addWidget(self.lbl)
        
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)
        
        self.ax = self.fig.add_subplot(111)
        self.ax.set_title("최근 10분간 온도 변화 (V2)")
        self.ax.set_ylim(48.5, 51.5)
        self.ax.set_xlim(0, 600)
        self.ax.grid(True, linestyle=':', alpha=0.7)
        
        # 10분 = 600초
        self.max_points = 600
        self.data_history = collections.deque(maxlen=self.max_points)
        self.line, = self.ax.plot([], [], 'b-', linewidth=1.5, label='실시간 온도')
        self.ax.legend(loc='upper right')
        
        self.canvas.draw() # 즉시 빈 그래프 그리기 (검은 화면 방지)
        
        self.current_minute = None
        self.current_filename = None
        
        self.receiver = DataReceiver()
        self.receiver.new_data.connect(self.process_data)
        self.receiver.start()

    @Slot(float, str)
    def process_data(self, val, timestamp):
        # 1. 그래프 업데이트
        self.data_history.append(val)
        self.line.set_data(range(len(self.data_history)), list(self.data_history))
        self.canvas.draw_idle()
        
        # 2. 파일 저장 로직 (분 단위 회전)
        dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        minute_str = dt.strftime('%Y%m%d_%H%M')
        
        # 분이 바뀌었는지 확인
        if self.current_minute != minute_str:
            # 기존 파일이 있다면 txt -> csv 변경
            if self.current_filename and os.path.exists(self.current_filename):
                csv_name = self.current_filename.replace('.txt', '.csv')
                # 이미 파일이 있으면 (중복 등) 이름 충돌 방지
                if os.path.exists(csv_name): os.remove(csv_name)
                os.rename(self.current_filename, csv_name)
                print(f"[변경 완료] {self.current_filename} -> {csv_name}")
            
            # 새 파일 생성
            self.current_minute = minute_str
            self.current_filename = f"{minute_str}.txt"
            self.lbl.setText(f"기록 중: {self.current_filename} (00초~59초 수집)")
        
        # 데이터 쓰기 (CSV 형식: 시간,온도)
        with open(self.current_filename, 'a') as f:
            f.write(f"{timestamp},{val:.2f}\n")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    AccumulatorGUI().show()
    sys.exit(app.exec())
