# # huey - as it is more lightweight than celery
# # To create huey tasks just create a tasks.py file in the app same as celery
# # common decorators are @huey.task() and @huey.periodic_task(crontab(minute=0, hour=0))
# from huey import RedisHuey
# from redis import ConnectionPool
#
# pool = ConnectionPool()
# HUEY = RedisHuey(SITE_NAME, connection_pool=pool.from_url(REDIS_URL))
