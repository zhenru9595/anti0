import sys
import sqlite3
import pandas as pd
from PySide6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QLabel, QPushButton, QMessageBox
from PySide6.QtCore import QTimer, Slot
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from datetime import datetime
import os
from factory_report_manager import ReportGenerator

# 한글 폰트 설정 (Windows: 맑은 고딕)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

class ManagerUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("공장 통합 관제 시스템 [Manager Dashboard]")
        self.resize(1100, 950)

        # 메인 위젯 레이아웃 설정
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # 상단 상태 대시보드
        self.status_label = QLabel("상태: 시스템 연결 중...")
        font = self.status_label.font()
        font.setPointSize(16)
        font.setBold(True)
        self.status_label.setFont(font)
        self.status_label.setContentsMargins(10, 5, 10, 5)
        layout.addWidget(self.status_label)

        # Matplotlib Figure 및 Canvas 생성
        self.figure = Figure(figsize=(10, 10), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # 차트(Ax) 설정
        self.ax_hist = self.figure.add_subplot(211) # 위쪽: 역사 기록(분단위)
        self.ax_live = self.figure.add_subplot(212) # 아래쪽: 실시간(초단위)
        self.figure.tight_layout(pad=4.0)
        
        # 하단 정보 및 버튼 레이아웃
        self.info_label = QLabel("최근 업데이트: --:--:--")
        self.info_label.setStyleSheet("color: #666; font-size: 11px;")
        layout.addWidget(self.info_label)

        btn_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("강제 새로고침")
        self.refresh_btn.setFixedHeight(45)
        self.refresh_btn.setStyleSheet("background-color: #f5f5f5; font-weight: bold; border-radius: 5px;")
        self.refresh_btn.clicked.connect(self.manual_refresh)
        btn_layout.addWidget(self.refresh_btn)
        
        self.report_btn = QPushButton("종합 PDF 리포트 추출 (그래프 포함)")
        self.report_btn.setFixedHeight(45)
        self.report_btn.setStyleSheet("background-color: #0d47a1; color: white; font-weight: bold; border-radius: 5px;")
        self.report_btn.clicked.connect(self.generate_pdf_report)
        btn_layout.addWidget(self.report_btn)
        
        layout.addLayout(btn_layout)

         # 5분 자동 엑셀 저장 타이머 (300,000 ms)
        self.excel_timer = QTimer()
        self.excel_timer.timeout.connect(self.auto_save_excel)
        self.excel_timer.start(300000)

        # 경로 설정 (절대 경로 사용으로 안정성 확보)
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.data_dir = os.path.join(self.base_dir, "data")
        
        # data 폴더 즉시 생성
        os.makedirs(self.data_dir, exist_ok=True)

        self.report_gen = ReportGenerator()
        self.update_plot()
        
        # 시작 시점에 즉시 1회 자동 저장 실행 (사용자 확인용)
        self.auto_save_excel()

    @Slot()
    def manual_refresh(self):
        """수동 새로고침 버튼 핸들러 (강력한 시각 피드백 추가)"""
        original_style = self.refresh_btn.styleSheet()
        self.refresh_btn.setText("새로고침 중...")
        self.refresh_btn.setStyleSheet("background-color: #bbdefb; font-weight: bold; border-radius: 5px;")
        
        # 업데이트 시점에 폴더 다시 확인 (강제 생성 보장)
        os.makedirs(self.data_dir, exist_ok=True)
        
        # 즉시 강제 업데이트 실행
        self.update_plot()
        
        # 0.5초 후 원래대로 복구 (시각적 피드백 제공)
        QTimer.singleShot(500, lambda: self.refresh_btn.setText("강제 새로고침"))
        QTimer.singleShot(500, lambda: self.refresh_btn.setStyleSheet(original_style))

    @Slot()
    def auto_save_excel(self):
        """5분마다 엑셀 자동 저장 (data 폴더 내 보관)"""
        print(f"[{datetime.now().strftime('%H:%M:%S')}] 엑셀 자동 저장 시도 중...")
        try:
            # data 폴더 재생성/확인
            os.makedirs(self.data_dir, exist_ok=True)
            
            # 타임아웃 10초 적용
            conn = sqlite3.connect(f"file:factory_data.db?mode=ro", uri=True, timeout=10)
            df = pd.read_sql_query("SELECT * FROM minute_summary ORDER BY start_time DESC", conn)
            conn.close()
            
            if not df.empty:
                filename = os.path.join(self.data_dir, "factory_data_log.xlsx")
                df.to_excel(filename, index=False)
                timestamp = datetime.now().strftime('%H:%M:%S')
                self.info_label.setText(f"엑셀 자동 저장 완료: {filename} ({timestamp})")
                print(f"[{timestamp}] 엑셀 자동 저장 성공: {filename}")
            else:
                self.info_label.setText("엑셀 저장 실패: 데이터가 없습니다.")
        except Exception as e:
            msg = f"엑셀 저장 오류: {str(e)}"
            self.info_label.setText(msg)
            self.info_label.setStyleSheet("color: red; font-size: 11px;")
            print(f"Excel Auto-save Error: {e}")

    @Slot()
    def generate_pdf_report(self):
        # 1. 현재 그래프를 임시 이미지로 저장
        temp_img = os.path.join(self.base_dir, "_dashboard_capture.png")
        try:
            self.figure.savefig(temp_img)
            # 2. 리포트 생성기 호출 (이미지 경로 전달)
            filename = self.report_gen.generate_report(graph_path=temp_img)
            
            if filename:
                QMessageBox.information(self, "리포트 완료", f"분석 리포트가 생성되었습니다:\n{filename}")
            else:
                QMessageBox.warning(self, "리포트 실패", "데이터 분석을 위한 정보가 부족합니다.")
        finally:
            # 3. 임시 파일 삭제
            if os.path.exists(temp_img):
                os.remove(temp_img)

    @Slot()
    def update_plot(self):
        try:
            # 타임아웃 10초 추가 및 WAL 모드 활성화를 위한 설정
            conn = sqlite3.connect(f"file:factory_data.db?mode=ro", uri=True, timeout=10)
            # WAL 모드 적용 확인용 (옵션)
            conn.execute("PRAGMA journal_mode=WAL")
            
            query_summary = "SELECT start_time, avg_temp, min_temp, max_temp FROM minute_summary ORDER BY start_time DESC LIMIT 30"
            df_summary = pd.read_sql_query(query_summary, conn)
            query_raw = "SELECT id, temperature FROM raw_data ORDER BY id DESC LIMIT 60"
            df_raw = pd.read_sql_query(query_raw, conn)
            conn.close()

            # --- 위쪽 그래프: 분 단위 히스토리 (요약) ---
            self.ax_hist.clear()
            if not df_summary.empty:
                df_summary = df_summary.sort_values(by='start_time')
                x = range(len(df_summary))
                self.ax_hist.plot(x, df_summary['avg_temp'], 'b-o', markersize=4, label='분단위 평균', linewidth=1.5)
                self.ax_hist.fill_between(x, df_summary['min_temp'], df_summary['max_temp'], color='blue', alpha=0.15, label='온도 변동폭(Min-Max)')
                self.ax_hist.set_xticks(list(x)[::5])
                self.ax_hist.set_xticklabels([t.split(' ')[1] for t in df_summary['start_time'].iloc[::5]], rotation=30)
            
            self.ax_hist.set_title("시스템 온도 히스토리 (분단위 추이)", fontsize=12, fontweight='bold')
            self.ax_hist.set_ylabel("온도 (°C)")
            self.ax_hist.grid(True, linestyle=':', alpha=0.6)
            self.ax_hist.legend(loc='upper right', fontsize=9)
            self.ax_hist.set_ylim(48.5, 51.5)

            # --- 아래쪽 그래프: 실시간 모니터링 (1초 단위) ---
            self.ax_live.clear()
            if not df_raw.empty:
                df_raw = df_raw.sort_values(by='id')
                x_live = range(len(df_raw))
                current_temp = df_raw['temperature'].iloc[-1]
                
                color = 'red' if (current_temp > self.safe_high or current_temp < self.safe_low) else 'green'
                self.ax_live.plot(x_live, df_raw['temperature'], color=color, linewidth=2, label='현재 온도(1s)')
                self.ax_live.axhline(y=self.safe_high, color='orange', linestyle='--', linewidth=1, label='안전 상한(50.5)')
                self.ax_live.axhline(y=self.safe_low, color='orange', linestyle='--', linewidth=1, label='안전 하한(49.5)')
                self.ax_live.fill_between(x_live, self.safe_low, self.safe_high, color='green', alpha=0.05)

                status_text = "정상 작동" if color == 'green' else "주의: 범위를 초과함"
                self.status_label.setText(f"시스템 상태: {status_text} | 현재 실시간 온도: {current_temp:.2f}°C")
                self.status_label.setStyleSheet(f"color: white; background-color: {'#2e7d32' if color == 'green' else '#c62828'};")
            
            self.ax_live.set_title("실시간 초단위 정밀 모니터링", fontsize=12, fontweight='bold')
            self.ax_live.set_ylabel("온도 (°C)")
            self.ax_live.set_xlabel("최근 60초 데이터 흐름")
            self.ax_live.grid(True, linestyle=':', alpha=0.6)
            self.ax_live.legend(loc='upper left', fontsize=9)
            self.ax_live.set_ylim(48.5, 51.5)

            self.canvas.draw()
            # 마지막 업데이트 시간 갱신
            self.info_label.setText(f"최근 업데이트: {datetime.now().strftime('%H:%M:%S')}")
            self.info_label.setStyleSheet("color: #666; font-size: 11px;")

        except Exception as e:
            self.info_label.setText(f"업데이트 오류: {e}")
            self.info_label.setStyleSheet("color: red; font-size: 11px;")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ManagerUI()
    window.show()
    sys.exit(app.exec())
