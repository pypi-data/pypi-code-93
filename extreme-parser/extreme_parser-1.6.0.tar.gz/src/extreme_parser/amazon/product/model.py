class Product:
    parent_asin: str
    weight: float
    brand: str
    price_min: float
    price_max: float
    in_stock: bool
    stock: int
    ship: str
    delivery: str
    material: str
    description: str

    def __init__(self, attrs=None):
        self.__dict__ = attrs or dict()

    def __str__(self):
        return str(self.__dict__)
