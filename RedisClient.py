import redis
import os

class RedisClient:
    def __init__(self):
        self.client = redis.Redis(host=os.getenv('REDIS_HOST'), port=int(os.getenv('REDIS_PORT')), db=0)

    def get_unique_id(self):
        return self.client.incr('unique_id_counter')
    