import json
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

import config, redis_interface

app = FastAPI()
redis_server = redis_interface.connect_to_redis()


@app.get("/")
def root():
    return {"status": "Hello"}


@app.put("/logs/conn/")
def add_conn_log(log_line: str):
    entry = json.loads(log_line)
    conn_id = entry['uid']
    start_timestamp = entry['ts']
    duration = entry['duration']
    end_timestamp = start_timestamp + duration
    start_time_bucket = config.TIME_BUCKET_SIZE * (start_timestamp//config.TIME_BUCKET_SIZE)
    end_time_bucket = config.TIME_BUCKET_SIZE * (end_timestamp//config.TIME_BUCKET_SIZE)
    time_stamps = range(start_time_bucket, end_time_bucket, config.TIME_BUCKET_SIZE)
    pipeline = redis_server.pipeline()
    for stamp in time_stamps:
        redis_interface.append_to_list(pipeline, str(stamp), conn_id)
    conn_key = conn_id + ".conn"
    redis_interface.set_hash(pipeline, conn_key, entry)
    redis_interface.set_hash_key(pipeline, conn_id, "conn", conn_key)
    results = pipeline.execute()
    if not all(results):
        return False
    return True


@app.put("/logs/dns/")
def add_dns_log(log_line: str):
    entry = json.loads(log_line)
    conn_id = entry['uid']
    pipeline = redis_server.pipeline()
    dns_key = conn_id + ".dns"
    redis_interface.set_hash(pipeline, dns_key, entry)
    redis_interface.set_hash_key(pipeline, conn_id, "dns", dns_key)
    results = pipeline.execute()
    if not all(results):
        return False
    return True



@app.put("/logs/http/")
def add_http_log(log_line: str):
    entry = json.loads(log_line)
    conn_id = entry['uid']
    pipeline = redis_server.pipeline()
    http_key = conn_id + ".http"
    redis_interface.set_hash(pipeline, http_key, entry)
    redis_interface.set_hash_key(pipeline, conn_id, "http", http_key)
    results = pipeline.execute()
    if not all(results):
        return False
    return True


@app.put("/logs/ssl/")
def add_ssl_log(log_line: str):
    entry = json.loads(log_line)
    conn_id = entry['uid']
    pipeline = redis_server.pipeline()
    ssl_key = conn_id + ".ssl"
    redis_interface.set_hash(pipeline, ssl_key, entry)
    redis_interface.set_hash_key(pipeline, conn_id, "dns", ssl_key)
    results = pipeline.execute()
    if not all(results):
        return False
    return True


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
