import uvicorn
from fastapi import FastAPI
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from contextlib import asynccontextmanager

from routers.wpp_router import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    redis = aioredis.from_url("redis://localhost", encoding="utf8", decode_responses=True)
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
    yield
    await redis.close()

app = FastAPI(title="Test Task", debug=True, lifespan=lifespan)

app.include_router(router)

if __name__ == "__main__":
    uvicorn.run("api:app", port=8080, log_level="info")


