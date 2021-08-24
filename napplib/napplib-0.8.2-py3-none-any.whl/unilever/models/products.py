from typing import List


class UnileverProduct:
    productTitle: str
    sku: str
    ean: str
    price: str
    stockQty: int

    def __init__(self, productTitle: str, sku: str, ean: str, price: str, stockQty: int):
        self.productTitle = productTitle
        self.sku = sku
        self.ean = ean
        self.price = price
        self.stockQty = stockQty


class Products:
    products: List[UnileverProduct]

    def __init__(self, products: List[UnileverProduct]):
        self.products = products
