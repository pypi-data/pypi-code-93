from ....util.config import SurfingConfigurator

# key space
cas_default_key_space = SurfingConfigurator().get_cassandra_setting().default_key_space
CAS_KEY_SPACE = 'surfing' if not cas_default_key_space else cas_default_key_space