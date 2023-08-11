# broker_url = 'redis://redis:6379/' 127.0.0.1
# result_backend = 'redis://redis:6379/'
REDIS_HOST = '127.0.0.1'
REDIS_PORT = '6379'

broker_url = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'
result_backend = 'redis://' + REDIS_HOST + ':' + REDIS_PORT + '/0'

task_serializer = 'json'
result_serializer = 'json'
accept_content = ['json']
timezone = 'Asia/Bishkek'
enable_utc = False
broker_connection_retry_on_startup = True