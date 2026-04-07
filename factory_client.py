import socket

def start_client():
    host = '127.0.0.1'  # 루프백 주소 (동일한 컴퓨터 내에서 통신)
    port = 9999         # 서버에서 설정한 동일한 포트 번호

    # 클라이언트용 TCP 소켓 생성
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        print(f"공장 온도 센서 서버({host}:{port})에 연결을 시도합니다...")
        client_socket.connect((host, port))
        print("연결 성공! 데이터를 수신하기 시작합니다.\n")

        while True:
            # 서버로부터 데이터를 수신 (최대 1024 바이트)
            data = client_socket.recv(1024)
            
            # 수신된 데이터가 없으면 서버가 연결을 끊은 것임
            if not data:
                print("서버 측에서 연결을 종료했습니다.")
                break
            
            # 전달받은 바이트 데이터를 문자열로 디코딩하고 공백 및 개행문자 제거
            temperature_str = data.decode('utf-8').strip()
            
            print(f"[수신 데이터] 현재 공장 설비 온도: {temperature_str} 도")

    except ConnectionRefusedError:
        print("연결 실패: 서버를 찾을 수 없습니다.")
        print("서버 프로그램(factory_sensor.py)이 먼저 실행되어 있는지 확인해주세요.")
    except KeyboardInterrupt:
        print("\n수신을 강제 종료합니다. (Ctrl+C)")
    except Exception as e:
        print(f"수신 중 에러 발생: {e}")
    finally:
        # 소켓 닫기
        client_socket.close()
        print("클라이언트 프로그램이 종료되었습니다.")

if __name__ == "__main__":
    start_client()
