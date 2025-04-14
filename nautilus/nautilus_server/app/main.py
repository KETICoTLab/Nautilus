import uvicorn
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from app.database import init_db_pool, close_db_pool, pool
from app.config import HOST, PORT, BASE_URL
from app.routers import api_router
from app.logging import print_logo, setup_logging
from typing import List

app = FastAPI(title="Nautilus API", version="1.0.0", root_path="/nautilus/v1")
app.include_router(api_router)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 또는 ["*"]로 모든 origin 허용 (개발용)
    allow_credentials=True,
    allow_methods=["*"],  # GET, POST, etc
    allow_headers=["*"],
)

Web_url = "http://127.0.0.1:5173"

# ------------------------
# ✅ WebSocket 관련 설정
# ------------------------

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                self.disconnect(connection)

manager = ConnectionManager()

@app.websocket("/ws/notify")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)

# 🔔 외부에서 호출할 수 있도록 manager export
app.websocket_manager = manager

# ------------------------
# nautilus startup
# ------------------------

@app.on_event("startup")
async def startup():
    await init_db_pool()
    from app.database import pool
    setup_logging()
    print_logo()
    print(f"🚀 Nautilus web is running at: {Web_url}")
    print("✅ Nautilus is ready! Let's dive into the deep! 🌊\n")

@app.on_event("shutdown")
async def shutdown():
    await close_db_pool()

if __name__ == "__main__":
    uvicorn.run("app.main:app", host=HOST, port=int(PORT), reload=True)
