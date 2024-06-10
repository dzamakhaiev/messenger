LOKI_HOST = 'loki'
LOKI_PORT = 3100
LOKI_URL = f'http://{LOKI_HOST}:{LOKI_PORT}'
LOKI_PUSH = '/loki/api/v1/push'
FORMAT = '%(asctime)s %(levelname)s %(unit)s: %(message)s'
DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
