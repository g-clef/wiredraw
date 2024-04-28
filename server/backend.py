import json
from fastapi import FastAPI
import uvicorn

import config
import redis_interface
import schema

app = FastAPI()
redis_server = redis_interface.connect_to_redis()


@app.get("/")
async def root():
    return {"status": "Hello"}


@app.put("/zeek/conn/")
async def add_conn_log(log_line: str):
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
        redis_interface.add_to_set(pipeline, str(stamp), conn_id)
    conn_key = conn_id + ".conn"
    redis_interface.set_hash(pipeline, conn_key, entry)
    redis_interface.set_hash_key(pipeline, conn_id, "conn", conn_key)
    results = pipeline.execute()
    if not all(results):
        return False
    return True


@app.put("/zeek/dns/")
async def add_dns_log(log_line: str):
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



@app.put("/zeek/http/")
async def add_http_log(log_line: str):
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


@app.put("/zeek/ssl/")
async def add_ssl_log(log_line: str):
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


@app.get("/events/list/{timestamp}")
async def event_list(timestamp: int) -> schema.EventBucket:
    # find the bucket that contains this timestamp, return the datastructure that contains
    # the basic information about this bucket.
    start_time_bucket = config.TIME_BUCKET_SIZE * (timestamp//config.TIME_BUCKET_SIZE)
    events = redis_server.smembers(str(start_time_bucket))
    response = schema.EventBucket(timestamp=timestamp)
    pipeline = redis_server.pipeline()
    for event in events:
        await pipeline.hgetall(f"{event}.conn")
    all_conn_entrys = pipeline.execute()
    for entry in all_conn_entrys:
        event = schema.EventSummary(source_ip=entry['id.orig_h'],
                                    dest_ip=entry['id.resp_h'],
                                    zeek_id=entry['uid'],
                                    total_bytes=entry['orig_bytes'] + entry['resp_bytes'],
                                    direction=entry['orig_bytes'] - entry['resp_bytes'])
        response.events.append(event)
    return response


@app.get("/events/details/{zeek_id}")
async def event_details(zeek_id: str) -> schema.EventDetails:
    # return the full set of zeek entries for a given zeek id
    log_keys = redis_server.hgetall(zeek_id)
    response = schema.EventDetails(zeek_id=zeek_id)
    pipeline = redis_server.pipeline()
    log_names = list()
    for log_name, key_name in log_keys.items():
        log_names.append(log_name)
        await pipeline.hgetall(key_name)
    all_logs = pipeline.execute()
    for entry, log_name in zip(all_logs, log_names):
        event = schema.Event(zeek_id=entry['uid'], log_type=log_name,log=entry)
        response.events.append(event)
    return response


@app.get("/stats")
async def stats():
    results = redis_server.hgetall("stats")
    return results


async def recompute_stats():
    min_key = None
    max_key = None
    key_sizes = dict()
    for key in redis_server.scan():
        try:
            key = int(key)
        except ValueError:
            continue
        if min_key is None or min_key > key:
            min_key = key
        if max_key is None or max_key < key:
            max_key = key
        size = redis_server.scard(str(key))
        key_sizes[str(key)] = size
    stats = dict(min_key=min_key, max_key=max_key, sizes=key_sizes)
    pipeline = redis_server.pipeline()
    redis_interface.set_hash(pipeline, "stats", stats)
    pipeline.execute()


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
