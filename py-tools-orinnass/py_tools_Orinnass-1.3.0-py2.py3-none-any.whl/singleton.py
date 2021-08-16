class Singleton(type):
    """
    Паттерн Singleton

    Для создание класса Singleton нужно указать для класса параметр metaclass=Singleton
    """
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]
