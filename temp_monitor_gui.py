import sys
import socket
import collections
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QLabel
from PySide6.QtCore import QThread, Signal, Slot
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

plt.rcParams['font.family'] = 'Malgun Gothic'

class SocketThread(QThread):
    data_received = Signal(float)
    def run(self):
        while True:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                # 연결 성공할 때까지 무한 재시도 (1초 간격)
                s.connect(('127.0.0.1', 9998))
                while True:
                    data = s.recv(1024)
                    if not data: break
                    for line in data.decode('utf-8').split('\n'):
                        if line.strip():
                            self.data_received.emit(float(line.strip()))
            except: 
                import time
                time.sleep(1)
            finally: 
                s.close()
                # 연결이 끊기면 다시 위로 올라가서 재연결 시도

class MonitorGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("실시간 온도 모니터 (1s)")
        self.resize(600, 400)
        
        widget = QWidget()
        self.setCentralWidget(widget)
        layout = QVBoxLayout(widget)
        
        self.lbl = QLabel("현재 온도: 수집 대기 중...")
        self.lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: #555;")
        layout.addWidget(self.lbl)
        
        self.fig = Figure()
        self.canvas = FigureCanvas(self.fig)
        layout.addWidget(self.canvas)
        
        self.ax = self.fig.add_subplot(111)
        self.ax.set_ylim(48.5, 51.5)
        self.ax.set_xlim(0, 60)
        self.data = collections.deque(maxlen=60)
        self.line, = self.ax.plot([], [], 'r-', linewidth=2)
        self.ax.grid(True, linestyle=':', alpha=0.7)
        self.ax.set_title("실시간 온도 스트림 (V2)")
        
        self.canvas.draw() # 즉시 빈 그래프 그리기 (검은 화면 방지)
        
        self.thread = SocketThread()
        self.thread.data_received.connect(self.update)
        self.thread.start()

    @Slot(float)
    def update(self, val):
        self.lbl.setText(f"현재 온도: {val:.2f}°C")
        self.lbl.setStyleSheet("font-size: 20px; font-weight: bold; color: green;")
        self.data.append(val)
        self.line.set_data(range(len(self.data)), list(self.data))
        self.canvas.draw_idle()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    MonitorGUI().show()
    sys.exit(app.exec())
