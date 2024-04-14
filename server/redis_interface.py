import time
import uuid

from typing import Dict

import redis

import config


def acquire_lock_with_expiration(
        conn: redis.Redis, lockname: str, acquire_timeout: int = 10, lock_timeout: int = 10
):
    identifier = str(uuid.uuid4())
    lock_key = "lock:" + lockname
    end = time.time() + acquire_timeout
    while time.time() < end:
        if conn.setex(lock_key, lock_timeout, identifier):
            return identifier
        time.sleep(0.001)
    return False


def release_lock(conn: redis.Redis, lockname: str, identifier: str):
    lock_key = "lock:" + lockname
    pipe = conn.pipeline(True)
    while True:
        try:
            pipe.watch(lock_key)
            if pipe.get(lock_key) == identifier:
                pipe.multi()
                pipe.delete(lock_key)
                pipe.execute()
                return True
            pipe.unwatch()
            break
        except redis.exceptions.WatchError:
            pass
    return False


def set_key_safely(conn: redis.Redis, key: str, value: str, timeout: int = 10):
    identifier = acquire_lock_with_expiration(conn, key, timeout)
    if identifier is False:
        raise Exception("Failed to set key")
    conn.set(key, value)
    release_lock(conn, key, identifier)
    return True


def append_to_list(conn: redis.Redis, key: str, value: str, timeout: int = 10):
    identifier = acquire_lock_with_expiration(conn, key, timeout)
    conn.append(key, value)
    release_lock(conn, key, identifier)
    return True


def set_hash(conn: redis.Redis, key: str, hash_vals: Dict, timeout: int = 10):
    identifier = acquire_lock_with_expiration(conn, key, timeout)
    conn.hset(key, mapping=hash_vals)
    release_lock(conn, key, identifier)
    return True


def set_hash_key(conn: redis.Redis, key: str, hash_key: str, hash_value: str, timeout: int = 10):
    identifier = acquire_lock_with_expiration(conn, key, timeout)
    conn.hset(key, hash_key, hash_value)
    release_lock(conn, key, identifier)
    return True


def connect_to_redis() -> redis.Redis:
    conn = redis.Redis(config.REDIS_HOST, config.REDIS_PORT, decode_responses=config.REDIS_DECODE_RESPONSES)
    return conn
