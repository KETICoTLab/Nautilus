import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:keti123@localhost:5432/nautilus_db")
HOST = os.getenv("HOST", "127.0.0.1")
PORT = os.getenv("PORT", "8000")
BASE_URL = f"http://{HOST}:{PORT}/nautilus/v1"
