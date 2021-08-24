from typing import List


class UnileverProductStock:
    sku: str
    stockQty: int

    def __init__(self, sku: str, stockQty: int):
        self.sku = sku
        self.stockQty = stockQty


class ProductsStock:
    products: List[UnileverProductStock]

    def __init__(self, products: List[UnileverProductStock]):
        self.products = products
