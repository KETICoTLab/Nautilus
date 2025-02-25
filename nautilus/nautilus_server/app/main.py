import uvicorn
from fastapi import FastAPI
from app.database import init_db_pool, close_db_pool, pool
from app.config import HOST, PORT, BASE_URL
from app.routers import api_router
from app.logging import print_logo, setup_logging

app = FastAPI(title="Nautilus API", version="1.0.0", root_path="/nautilus/v1")
app.include_router(api_router)

Web_url = "http://127.0.0.1:8888"

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
