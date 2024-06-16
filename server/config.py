
# Redis connection info
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_DECODE_RESPONSES = True

# Number of seconds to bucket together entries. In other words,
# a given bucket of entries in Redis will cover this many seconds, so when
# you query redis, you will get back all the connections that were active during
# this timeperiod
TIME_BUCKET_SIZE = 10

