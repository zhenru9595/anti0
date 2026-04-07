import socket
import random
import time

def start_server():
    host = '0.0.0.0'
    port = 9999

    # TCP 소켓 생성
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 포트 재사용 옵션 설정
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # 서버 바인딩 및 리스닝
    server_socket.bind((host, port))
    server_socket.listen(1)

    print(f"공장 설비 온도 센서 서버가 시작되었습니다. 포트: {port}")

    while True:
        try:
            print("\n클라이언트의 접속을 기다리는 중...")
            client_socket, addr = server_socket.accept()
            print(f"클라이언트가 접속했습니다: {addr}")

            while True:
                # 49.0 ~ 51.0 사이의 랜덤한 소수 생성
                temperature = random.uniform(49.0, 51.0)
                
                # 문자열로 변환하여 전송 (소수점 둘째 자리까지 표시, 개행문자 추가)
                data = f"{temperature:.2f}\n"
                client_socket.sendall(data.encode('utf-8'))
                
                print(f"전송된 온도: {temperature:.2f}도")
                
                # 1초 대기
                time.sleep(1)
                
        except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
            print(f"클라이언트와의 연결이 끊어졌습니다: {addr}")
        except KeyboardInterrupt:
            print("\n서버를 종료합니다.")
            break
        except Exception as e:
            print(f"예기치 않은 에러 발생: {e}")
        finally:
            # 클라이언트 소켓 닫기
            if 'client_socket' in locals():
                client_socket.close()

if __name__ == "__main__":
    start_server()
