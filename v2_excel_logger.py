import os
import pandas as pd
import time
import shutil
from datetime import datetime

class ExcelLogger:
    def __init__(self, target_xlsx='sensor_history.xlsx', archive_dir='archive_data'):
        # data 폴더 설정
        self.data_dir = 'data'
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
            
        self.target_xlsx = os.path.join(self.data_dir, target_xlsx)
        self.archive_dir = archive_dir
        if not os.path.exists(self.archive_dir):
            os.makedirs(self.archive_dir)
        
        # 엑셀 파일 초기화
        if not os.path.exists(self.target_xlsx):
            df = pd.DataFrame(columns=['Time', 'Average Temperature'])
            df.to_excel(self.target_xlsx, index=False)
            print(f"[초기화] {self.target_xlsx} 파일을 생성했습니다.")

    def run(self):
        print("Excel Logger (Watcher) Started...")
        while True:
            # 현재 폴더의 .csv 파일 검색
            csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
            
            for csv_file in csv_files:
                try:
                    print(f"[감지] {csv_file} 처리 중...")
                    # 데이터 읽기
                    df = pd.read_csv(csv_file, names=['Time', 'Temp'])
                    avg_temp = df['Temp'].mean()
                    
                    # 파일명에서 시간 정보 추출 (YYYYMMDD_HHMM.csv)
                    time_key = csv_file.replace('.csv', '')
                    formatted_time = f"{time_key[:4]}-{time_key[4:6]}-{time_key[6:8]} {time_key[9:11]}:{time_key[11:13]}"
                    
                    # 엑셀에 추가
                    existing_df = pd.read_excel(self.target_xlsx)
                    new_row = pd.DataFrame([{'Time': formatted_time, 'Average Temperature': round(avg_temp, 2)}])
                    updated_df = pd.concat([existing_df, new_row], ignore_index=True)
                    updated_df.to_excel(self.target_xlsx, index=False)
                    
                    print(f"[기록] {formatted_time} | 평균 온도: {avg_temp:.2f}")
                    
                    # 아카이브로 이동 (중복 처리 방지)
                    shutil.move(csv_file, os.path.join(self.archive_dir, csv_file))
                    print(f"[이동] {csv_file} -> {self.archive_dir}/")
                    
                except Exception as e:
                    print(f"[에러] {csv_file} 처리 실패: {e}")
            
            time.sleep(5) # 5초마다 확인

if __name__ == "__main__":
    logger = ExcelLogger()
    logger.run()
