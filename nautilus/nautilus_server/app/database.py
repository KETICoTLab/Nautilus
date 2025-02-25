import asyncpg
from app.config import DATABASE_URL
from fastapi import Depends

pool = None

async def init_db_pool():
    global pool
    if pool is not None:
        print(f"⚠️ PostgreSQL {DATABASE_URL} \n connection pool created: {pool}")
        print("⚠️ Warning: Database pool is already initialized.")
    pool = await asyncpg.create_pool(dsn=DATABASE_URL, min_size=1, max_size=10)
    print(f"✅ PostgreSQL {DATABASE_URL}")

async def close_db_pool():
    global pool
    if pool:
        await pool.close()
        print("❌ PostgreSQL connection pool closed.")


async def get_db_pool():
    """FastAPI 의존성 주입용 함수"""
    global pool
    if pool is None:
        raise Exception("⚠️ Database connection pool is not initialized!")
    return pool  # ✅ 항상 최신 pool을 반환