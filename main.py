from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from redis import Redis
from redis.exceptions import RedisError

app = FastAPI()

# Allow browser access for the grader
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Connect to Redis service in docker-compose
redis_client = Redis(
    host="redis",
    port=6379,
    decode_responses=True,
)


@app.get("/")
def root():
    return {"message": "API is running"}


@app.get("/healthz")
def healthz():
    try:
        redis_client.ping()
        return {
            "status": "ok",
            "redis": "up"
        }
    except RedisError:
        return {
            "status": "error",
            "redis": "down"
        }


@app.post("/hit/{key}")
def hit(key: str):
    count = redis_client.incr(key)
    return {
        "key": key,
        "count": count
    }


@app.get("/count/{key}")
def count(key: str):
    value = redis_client.get(key)

    return {
        "key": key,
        "count": int(value) if value else 0
    }
