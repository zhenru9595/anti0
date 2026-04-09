import socket
import random
import time
import threading

def handle_client(client_socket, addr):
    print(f"[연결] {addr}")
    try:
        while True:
            # 49.0 ~ 51.0 사이의 랜덤 온도
            temp = random.uniform(49.0, 51.0)
            client_socket.sendall(f"{temp:.2f}\n".encode('utf-8'))
            time.sleep(1)
    except:
        pass
    finally:
        client_socket.close()

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(('0.0.0.0', 9998))
    server.listen(5)
    print("V2 Sensor Server (Port 9998) Started...")
    
    try:
        while True:
            client, addr = server.accept()
            threading.Thread(target=handle_client, args=(client, addr), daemon=True).start()
    except KeyboardInterrupt:
        pass
    finally:
        server.close()

if __name__ == "__main__":
    start_server()
