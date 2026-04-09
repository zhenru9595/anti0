import socket
import random
import time
import threading

def handle_client(client_socket, addr):
    print(f"[연결 성공] 클라이언트 주소: {addr}")
    try:
        while True:
            # 49.0 ~ 51.0 사이의 랜덤한 소수 생성
            temperature = random.uniform(49.0, 51.0)
            
            # 문자열로 변환하여 전송 (소수점 둘째 자리까지 표시, 개행문자 추가)
            data = f"{temperature:.2f}\n"
            client_socket.sendall(data.encode('utf-8'))
            
            # 1초 대기
            time.sleep(1)
    except (ConnectionResetError, ConnectionAbortedError, BrokenPipeError):
        print(f"[연결 종료] 클라이언트 주소: {addr}")
    except Exception as e:
        print(f"[에러 발생] {addr}: {e}")
    finally:
        client_socket.close()

def start_server():
    host = '0.0.0.0'
    port = 9999

    # TCP 소켓 생성
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # 포트 재사용 옵션 설정
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    # 서버 바인딩 및 리스닝
    server_socket.bind((host, port))
    server_socket.listen(5) # 최대 5개 대기 큐

    print(f"==========================================")
    print(f"공장 설비 온도 센서 서버 (Role: Server) 시작")
    print(f"포트: {port}")
    print(f"==========================================")

    try:
        while True:
            client_socket, addr = server_socket.accept()
            # 각 클라이언트 마다 새로운 스레드 생성
            client_thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            client_thread.daemon = True
            client_thread.start()
    except KeyboardInterrupt:
        print("\n[서버 종료] 사용자에 의해 종료되었습니다.")
    finally:
        server_socket.close()

if __name__ == "__main__":
    start_server()
