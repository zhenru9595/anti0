import sqlite3
import pandas as pd
from fpdf import FPDF
from datetime import datetime
import os

class ReportGenerator:
    def __init__(self, db_name='factory_data.db'):
        self.db_name = db_name

    def generate_report(self, graph_path=None):
        print(f"==========================================")
        print(f"종합 분석 리포트 생성 (가시화 데이터 통합)")
        print(f"==========================================")
        
        if not os.path.exists(self.db_name):
            print("에러: 데이터베이스 파일이 존재하지 않습니다.")
            return None

        try:
            conn = sqlite3.connect(f"file:{self.db_name}?mode=ro", uri=True)
            df = pd.read_sql_query("SELECT * FROM minute_summary ORDER BY start_time DESC", conn)
            conn.close()

            if df.empty:
                print("에러: 리포트를 생성할 요약 데이터가 없습니다.")
                return None

            # PDF 생성 (A4 표준 규격 고정)
            pdf = FPDF(orientation='P', unit='mm', format='A4')
            pdf.add_page()
            
            # Title
            pdf.set_font("helvetica", "B", 20)
            pdf.cell(0, 20, "Factory Temperature Analytics Report", align='C', new_x="LMARGIN", new_y="NEXT")
            pdf.ln(5)
            
            # Graph Embedding (가시화 그래프 삽입)
            if graph_path and os.path.exists(graph_path):
                pdf.set_font("helvetica", "B", 12)
                pdf.cell(0, 10, "[ Monitoring Dashboard Capture ]", new_x="LMARGIN", new_y="NEXT")
                # A4 폭(210mm) 고려하여 적절한 크기로 삽입
                pdf.image(graph_path, x=10, y=None, w=190)
                pdf.ln(10)
            
            # Summary Section
            pdf.set_font("helvetica", "B", 14)
            pdf.cell(0, 10, "1. Executive Summary", new_x="LMARGIN", new_y="NEXT")
            pdf.set_font("helvetica", "", 11)
            pdf.cell(0, 10, f"- Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 10, f"- Total Monitoring Duration: {len(df)} minutes", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 10, f"- Global Average Temperature: {df['avg_temp'].mean():.2f} C", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(10)
            
            # Data Table Section
            pdf.set_font("helvetica", "B", 14)
            pdf.cell(0, 10, "2. Detailed Historical Data", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(2)
            
            # Table Header
            pdf.set_fill_color(230, 230, 230)
            pdf.set_font("helvetica", "B", 10)
            pdf.cell(50, 10, "Timestamp", border=1, fill=True)
            pdf.cell(40, 10, "Avg Temp (C)", border=1, fill=True)
            pdf.cell(40, 10, "Min Temp", border=1, fill=True)
            pdf.cell(40, 10, "Max Temp", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")
            
            # Table Data
            pdf.set_font("helvetica", "", 10)
            for index, row in df.iterrows():
                pdf.cell(50, 10, str(row['start_time']), border=1)
                pdf.cell(40, 10, f"{row['avg_temp']:.2f}", border=1)
                pdf.cell(40, 10, f"{row['min_temp']:.2f}", border=1)
                pdf.cell(40, 10, f"{row['max_temp']:.2f}", border=1, new_x="LMARGIN", new_y="NEXT")
                
                # 페이지 넘김 처리 (간단하게 40줄마다 새 페이지 - 여기서는 A4 이미지 때문에 첫 페이지는 적게)
                if index >= 30: 
                    pdf.cell(0, 10, "... historical records truncated for brevity", new_x="LMARGIN", new_y="NEXT")
                    break

            filename = f"factory_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            pdf.output(filename)
            
            print(f"리포트 생성 성공: {filename}")
            return filename

        except Exception as e:
            print(f"리포트 생성 중 에러 발생: {e}")
            return None

if __name__ == "__main__":
    generator = ReportGenerator()
    generator.generate_report()
