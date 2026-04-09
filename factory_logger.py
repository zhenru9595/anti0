import socket
import sqlite3
import time
from datetime import datetime

class DataLogger:
    def __init__(self, host='127.0.0.1', port=9999, db_name='factory_data.db'):
        self.host = host
        self.port = port
        self.db_name = db_name
        self.init_db()

    def init_db(self):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        # WAL 모드 활성화 (동시 읽기/쓰기 성능 향상)
        cursor.execute('PRAGMA journal_mode=WAL')
        
        # raw_data: 초단위 데이터
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS raw_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                temperature REAL
            )
        ''')
        # minute_summary: 분단위 데이터 (평균, 최소, 최대)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS minute_summary (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time DATETIME,
                avg_temp REAL,
                min_temp REAL,
                max_temp REAL
            )
        ''')
        conn.commit()
        conn.close()

    def save_raw(self, temp):
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('INSERT INTO raw_data (temperature) VALUES (?)', (temp,))
        conn.commit()
        conn.close()

    def save_summary(self, start_time, temps):
        if not temps:
            return
        avg_temp = sum(temps) / len(temps)
        min_temp = min(temps)
        max_temp = max(temps)
        
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO minute_summary (start_time, avg_temp, min_temp, max_temp)
            VALUES (?, ?, ?, ?)
        ''', (start_time, avg_temp, min_temp, max_temp))
        conn.commit()
        conn.close()
        print(f"[저장 완료] 1분 요약: {start_time} | 평균: {avg_temp:.2f}°C")

    def run(self):
        print(f"==========================================")
        print(f"공장 데이터 저장소 (Role: Storage) 시작")
        print(f"서버 연결 시도: {self.host}:{self.port}")
        print(f"==========================================")

        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            client_socket.connect((self.host, self.port))
            print("서버 연결 성공. 데이터를 수집합니다.")

            minute_temps = []
            minute_start = datetime.now().strftime('%Y-%m-%d %H:%M:00')

            while True:
                data = client_socket.recv(1024)
                if not data:
                    print("서버 연결이 종료되었습니다.")
                    break

                lines = data.decode('utf-8').strip().split('\n')
                for line in lines:
                    if not line.strip():
                        continue
                    try:
                        temp = float(line.strip())
                        self.save_raw(temp)
                        minute_temps.append(temp)
                        
                        # 화면 모니터링 출력
                        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        print(f"[{current_time}] 수신 온도: {temp:.2f}°C (수집 중: {len(minute_temps)}/60)")

                        # 1분(60개 데이터)이 모이면 요약 저장
                        if len(minute_temps) >= 60:
                            self.save_summary(minute_start, minute_temps)
                            minute_temps = []
                            minute_start = datetime.now().strftime('%Y-%m-%d %H:%M:00')

                    except ValueError:
                        continue

        except ConnectionRefusedError:
            print("에러: 서버가 실행 중이지 않습니다.")
        except KeyboardInterrupt:
            print("\n로그 기록을 중단합니다.")
        finally:
            client_socket.close()

if __name__ == "__main__":
    logger = DataLogger()
    logger.run()
