from typing import List


class UnileverProductPrice:
    sku: str
    price: str

    def __init__(self, sku: str, price: str):
        self.sku = sku
        self.price = price


class ProductsPrice:
    products: List[UnileverProductPrice]

    def __init__(self, products: List[UnileverProductPrice]):
        self.products = products
