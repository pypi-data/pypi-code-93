class BrokerSettings:
    token = ''
    api_key = ''
    api_secret = ''

class SymbolSettings(BrokerSettings):
    position_size = 0
    last_order_id = ''

settings = SymbolSettings()

settings.token = 'kdsfjklds'

print(settings.token)