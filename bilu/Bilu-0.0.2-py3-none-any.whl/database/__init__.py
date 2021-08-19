import os

from bilu.database.mongo import MongoManager

db_manager = MongoManager(
    host=os.environ.get('MONGODB_URI', 'mongodb://localhost:27017'),
    username=os.environ.get('MONGODB_USERNAME', ''),
    password=os.environ.get('MONGODB_PASSWORD', ''),
    database=os.environ.get('MONGODB_DATABASE', None),
    min_pool_size=os.environ.get('MONGODB_MIN_POOL_SIZE', 0),
    max_pool_size=os.environ.get('MONGODB_MAX_POOL_SIZE', 100),
    read_preference=os.environ.get(
        'MONGODB_READ_PREFERENCE',
        'secondaryPreferred'
    )
)
