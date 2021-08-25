class KeyVaultSecret:
    def __init__(self, key: str, value: str, overwrite: bool = True):
        self.overwrite = overwrite
        self.value = value
        self.key = key
