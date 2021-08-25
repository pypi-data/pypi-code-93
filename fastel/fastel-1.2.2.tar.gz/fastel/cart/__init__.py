from datetime import datetime
from typing import Any, Dict, MutableMapping, Optional, Type, Union

from bson.objectid import ObjectId
from pydantic import ValidationError
from pymongo.collection import Collection

from .base import BaseCart, BaseItem, BaseMultiItem, BaseMultiProductItem
from .datastructures import (
    BoolConfig,
    CartConfig,
    Coupon,
    Discount,
    ItemConfig,
    LogisticTypes,
    PaymentSubTypes,
)
from .datastructures import Product as ProductStructure
from .datastructures import SingleChoice, SingleConfig, VariantTypes
from .exceptions import CartException, cart_exception_handler


class ProductItem(BaseItem):
    product_collection: Collection
    product_cls = ProductStructure

    def __init__(
        self, cart: Optional["Cart"], product: ProductStructure, config: "ItemConfig"
    ) -> None:
        self.cart = cart
        self.product = product
        self.config = config
        self.amount = self._get_product_amount(config)
        self.name = self.product.name

    def _get_variant_price(self, config: Union[SingleConfig, BoolConfig]) -> int:
        try:
            variant = list(
                filter(
                    lambda product: product.name == config.name,
                    self.product.variants,
                )
            )[0]
        except IndexError:
            raise CartException("invalid_variant")

        if variant.type == VariantTypes.bool:
            return variant.price

        try:
            choice = list(
                filter(lambda _choice: _choice.name == config.choice, variant.choices)  # type: ignore
            )[0]
        except IndexError:
            raise CartException("invalid_variant")

        assert isinstance(choice, SingleChoice)
        return choice.price

    def _get_product_amount(self, config: ItemConfig) -> int:
        variant_price = sum(
            [self._get_variant_price(variant) for variant in config.variants]
        )
        price = self.product.price + variant_price
        return price * config.qty

    def to_dict(self) -> Dict[str, Any]:
        config = self.config.dict(exclude_unset=True)
        product_dict = self.product.dict()
        return {
            "name": self.name,
            "amount": self.amount,
            "config": config,
            "product": product_dict,
        }

    @classmethod
    def validate(  # type: ignore
        cls,
        product_id: Union[str, ObjectId],
        config: Union[ItemConfig, Dict[str, Any]],
        cart: Optional["Cart"],
    ) -> "ProductItem":
        if isinstance(product_id, str):
            product_id = ObjectId(product_id)
        product = cls.product_collection.find_one({"_id": product_id})
        if not product:
            raise

        validated_product = cls.product_cls.validate(product)
        if isinstance(config, dict):
            config = cls.config_cls.validate(config)  # type: ignore
        assert isinstance(config, ItemConfig)
        return cls(cart, validated_product, config)


class ProductMultiItem(BaseMultiProductItem):
    default_item_length: int = 10

    def add_item(self, product_id: str, config: "ItemConfig") -> None:  # type: ignore
        if len(self) >= self.default_item_length:
            raise CartException("item_length_limit")

        item = self.item_cls.validate(product_id, config, self.cart)
        self.items.append(item)
        self.refresh_attrs()

    def delete_item(self, index: int) -> None:
        try:
            self.items.pop(index)
            self.refresh_attrs()
        except IndexError:
            raise CartException(
                "index_does_exist",
            )

    def edit_item(self, index: int, config: "ItemConfig") -> None:  # type: ignore
        try:
            item = self.items[index]
            self.items[index] = self.item_cls.validate(
                item.product.id, config, self.cart  # type: ignore
            )
            self.refresh_attrs()
        except IndexError:
            raise CartException(
                "index_does_exist",
            )


class FeeItem(BaseItem):
    def __init__(self, cart: "Cart") -> None:
        self.cart = cart
        self.amount = 0
        self.name = "運費"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "amount": self.amount,
        }


class MultiItem(BaseMultiItem):
    item_cls = FeeItem
    cart: "Cart"

    def validate(self) -> None:
        self.items = [self.item_cls(self.cart)]


class CouponItem(BaseItem):
    coupon_collection: Collection
    model_cls = Coupon

    def __init__(self, coupon: Coupon):
        self.coupon = coupon
        self.amount = coupon.discount

    @property
    def threshold(self) -> int:
        return self.coupon.threshold

    @classmethod
    def validate(cls, code: str) -> "CouponItem":  # type: ignore
        now = datetime.now().timestamp() * 1000
        coupon_ins = cls.coupon_collection.find_one(
            {"code": code, "start_time": {"$lte": now}, "end_time": {"$gte": now}}
        )
        if coupon_ins is None:
            raise CartException("invalid_coupon")

        coupon = cls.model_cls.validate(coupon_ins)
        return cls(coupon)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "coupon",
            "name": self.coupon.name,
            "amount": self.coupon.discount,
            "coupon": self.coupon.dict(),
        }


class DiscountItem(BaseItem):
    discount_collection: Collection
    item_cls = Discount

    def __init__(self, discount: Discount):
        self.discount = discount
        self.amount = discount.discount

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": "discount",
            "name": self.discount.name,
            "amount": self.discount.discount,
            "discount": self.discount.dict(),
        }

    @classmethod
    def validate(cls, value: Dict[str, Any]) -> "DiscountItem":  # type: ignore
        return cls(cls.item_cls.validate(value))


class DiscountMultiItem(BaseMultiItem):
    cart: "Cart"
    coupon_cls: Optional[Type[CouponItem]] = None
    discount_cls: Optional[Type[DiscountItem]] = None

    def verify_coupon(self) -> bool:
        if self.cart.coupon is None:
            return False
        return self.cart.subtotal > self.cart.coupon.threshold

    def validate(self) -> None:
        self.items = []
        if self.coupon_cls is not None:
            if self.cart.coupon is not None:
                if not self.verify_coupon():
                    raise CartException("invalid_coupon")
                self.items.append(self.cart.coupon)

        if self.discount_cls is not None:
            now = datetime.now().timestamp() * 1000
            discounts = self.discount_cls.discount_collection.find(
                {
                    "start_time": {"$lte": now},
                    "end_time": {"$gte": now},
                    "threshold": {"$lte": self.cart.subtotal},
                }
            )
            discounts.sort((("threshold", -1),))
            for d in discounts:
                self.items.append(self.discount_cls.validate(d))
                break

        self.refresh_attrs()


class Cart(BaseCart):
    product_multi_item_cls = ProductMultiItem
    extra_multi_item_cls = MultiItem
    discount_multi_item_cls: Type[DiscountMultiItem] = DiscountMultiItem
    config_cls = CartConfig
    coupon_cls = CouponItem

    user_collection: Collection
    cart_collection: Collection
    user: MutableMapping[str, Any]

    discount_items: DiscountMultiItem

    def __init__(self, identity: str, coupon: Optional[str] = None):
        self.coupon = None
        self._user = self.load_user(identity)
        super().__init__(identity)
        self.coupon = self.validate_coupon(coupon)

    def load_user(self, identity: str) -> MutableMapping[str, Any]:
        return self.user_collection.find_one({"owner": identity})  # type: ignore

    def load_cart(self, identity: str) -> MutableMapping[str, Any]:
        cart = self.cart_collection.find_one({"owner": identity})
        if not cart:
            cart = {
                "owner": identity,
                **self.INITIAL_CART,
                **self.config_cls.validate_optional({}).dict(),
            }
            cart_result = self.cart_collection.insert_one(cart)
            cart["_id"] = cart_result.inserted_id

        return cart  # type: ignore

    def _set_cart(self, key: str, value: Any) -> None:
        self._cache_cart[key] = value

    def save_cart(self) -> None:
        self.cart_collection.find_one_and_update(
            {"_id": self._cache_cart["_id"]}, {"$set": self._cache_cart}
        )

    def validate(self) -> None:
        try:
            self.config_cls.validate(self._cache_cart)
        except ValidationError:
            raise CartException("validation_error")

        if self.total <= 0:
            raise CartException("total_lowest_exceed")

    def validate_coupon(self, code: Optional[str] = None) -> Optional[CouponItem]:
        if code is None:
            return None
        elif self.discount_items.coupon_cls is not None:
            return self.discount_items.coupon_cls.validate(code)
        return None


__all__ = [
    "cart_exception_handler",
    "Cart",
    "ProductItem",
    "ProductMultiItem",
    "FeeItem",
    "MultiItem",
]
