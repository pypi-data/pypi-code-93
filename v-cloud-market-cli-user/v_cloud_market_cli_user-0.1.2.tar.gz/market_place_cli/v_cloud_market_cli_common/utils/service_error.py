class ServiceException(Exception):
    pass

class WalletServiceException(Exception):
    pass

class WalletDecryptionException(WalletServiceException):
    pass

class WalletEncryptionException(WalletServiceException):
    pass

class WalletStorageLoadingException(WalletServiceException):
    pass

class WalletStorageSavingException(WalletServiceException):
    pass
