from typing import List


class ProductPrice:
    def __init__(self, Price: float,
                        ProductCode: str,
                        OldPrice: float = None,
                        SellerCode: str = None):
        self.Price = Price
        self.ProductCode = ProductCode
        if OldPrice:
            self.OldPrice = OldPrice
        if SellerCode:
            self.SellerCode = SellerCode


class ProductStock:
    def __init__(self, Quantity: int,
                        SellerCode: str,
                        SkuCode: str):
        self.Quantity = Quantity
        self.SellerCode = SellerCode
        self.SkuCode = SkuCode
