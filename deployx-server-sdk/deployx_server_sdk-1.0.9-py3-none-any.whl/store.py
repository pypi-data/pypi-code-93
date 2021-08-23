import logging

class FeatureFlagStore:
    """
    add new flag to redis
    update already created flag in redis
    """

    def __init__(self):
        # * Initializate and check redis database
        self.redis_db = False

        try:
            import redis
            from redis.connection import ConnectionError

            try:
                self.r = redis.Redis()
                self.r.ping()
                self.redis_db = True
            except ConnectionError:
                logging.info("Redis database is not running.")

        except ModuleNotFoundError:
            logging.info("Redis not installed. If internet connection wiil be lost, you will get default value instead of redis.")

    def init_user(self, config, user, flag_key):
        self.config = config
        self.user = user
        self.flag_key = flag_key

    def save(self, status):
        identifier = '-'
        type_of_statuses = ['unique_identifier', 'UNIQUE_IDENTIFIER']
        for key in type_of_statuses:
            if key in self.user:
                identifier = self.user[key]
        logging.info('Save flag in store')
        self.r.hset(identifier, '{}_{}'.format(self.config.sdk_key, self.flag_key), str(status))

    def decode_status(self, status): 
        if int(status) in range(10):
            return int(status)
        raise TypeError('Error while getting status. Check your flag availability.')

    def decode_byte_status(self, status):
        return self.decode_status(status.decode('utf-8'))