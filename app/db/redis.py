from fastapi import FastAPI
from redis import asyncio as aioredis


# 创建redis实例
def register_redis(app: FastAPI):
    async def redis_pool():
        redis_conn = await aioredis.from_url(
            url='redis://localhost',
            port=6379,
            db=0,
            encoding='utf-8',
            decode_responses=True
        )
        return redis_conn

    @app.on_event('startup')
    async def startup_event():
        app.state.redis = await redis_pool()