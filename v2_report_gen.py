import pandas as pd
from fpdf import FPDF
from datetime import datetime
import os

class ExcelReportGen:
    def __init__(self, excel_file='sensor_history.xlsx'):
        self.excel_file = excel_file

    def generate(self):
        print(f"Generating report from {self.excel_file}...")
        if not os.path.exists(self.excel_file):
            print("Error: Excel file not found.")
            return

        try:
            df = pd.read_excel(self.excel_file)
            if df.empty:
                print("Error: No data in Excel to report.")
                return

            pdf = FPDF()
            pdf.add_page()
            
            # Title
            pdf.set_font("helvetica", "B", 16)
            pdf.cell(0, 10, "Factory Temperature Analysis Report (V2)", align='C', new_x="LMARGIN", new_y="NEXT")
            pdf.ln(10)
            
            # Stats
            pdf.set_font("helvetica", "", 12)
            pdf.cell(0, 10, f"Generated At: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 10, f"Total Data Points: {len(df)} minutes", new_x="LMARGIN", new_y="NEXT")
            pdf.cell(0, 10, f"Average of Averages: {df['Average Temperature'].mean():.2f} C", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(10)
            
            # Table
            pdf.set_font("helvetica", "B", 10)
            pdf.cell(60, 10, "Time Interval", border=1)
            pdf.cell(60, 10, "Average Temperature (C)", border=1, new_x="LMARGIN", new_y="NEXT")
            
            pdf.set_font("helvetica", "", 10)
            for i, row in df.iterrows():
                pdf.cell(60, 10, str(row['Time']), border=1)
                pdf.cell(60, 10, f"{row['Average Temperature']:.2f}", border=1, new_x="LMARGIN", new_y="NEXT")
                if i >= 40:
                    pdf.cell(0, 10, "... list truncated for report brevity", new_x="LMARGIN", new_y="NEXT")
                    break

            filename = f"V2_Report_{datetime.now().strftime('%H%M%S')}.pdf"
            pdf.output(filename)
            print(f"Report Created Successfully: {filename}")

        except Exception as e:
            print(f"Error during PDF generation: {e}")

if __name__ == "__main__":
    gen = ExcelReportGen()
    gen.generate()
