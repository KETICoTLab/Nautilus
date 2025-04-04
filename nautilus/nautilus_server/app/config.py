import os
import socket

def get_server_ip() -> str:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:keti123@localhost:5432/nautilus_db")
HOST = os.getenv("HOST", get_server_ip())  # 여기서 실행됨!
PORT = os.getenv("PORT", "8000")
BASE_URL = f"http://{HOST}:{PORT}/nautilus/v1"
