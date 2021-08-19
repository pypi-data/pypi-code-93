class Product:
    weight: float
    brand: str
    price_min: float
    price_max: float
    in_stock: bool
    ship: str
    delivery: str

    def __init__(self, attrs=None):
        self.__dict__ = attrs or dict()

    def __str__(self):
        return str(self.__dict__)
