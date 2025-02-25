from typing import Optional, List
from asyncpg import Pool

async def fetch_one(pool: Pool, query: str, *params) -> Optional[dict]:
    if pool is None:
        raise Exception("Database connection pool is not initialized!")  # 🚨 디버깅 로그 추가
    async with pool.acquire() as conn:
        return await conn.fetchrow(query, *params)

async def fetch_all(pool: Pool, query: str, *params) -> List[dict]:
    async with pool.acquire() as conn:
        return await conn.fetch(query, *params)

async def execute(pool: Pool, query: str, *params) -> str:
    async with pool.acquire() as conn:
        return await conn.execute(query, *params)
