import redis
from server_side.database import settings


class RedisHandler:

    def __init__(self):
        try:
            self.connection = redis.Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)
        except redis.exceptions.ConnectionError as e:
            quit(e)

    def __del__(self):
        if self.connection:
            self.connection.close()


if __name__ == '__main__':
    handler = RedisHandler()
