from typing import Any, Dict, MutableMapping, Optional, Union

from bson.objectid import ObjectId
from pydantic import ValidationError
from pymongo.collection import Collection

from .base import BaseCart, BaseItem, BaseMultiItem, BaseMultiProductItem
from .datastructures import (
    BoolConfig,
    CartConfig,
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
        self._cart = cart
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
        product_dict["id"] = self.product.id.__str__()
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

        item = self.item_cls.validate(product_id, config, self._cart)
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
                item.product.id, config, self._cart  # type: ignore
            )
            self.refresh_attrs()
        except IndexError:
            raise CartException(
                "index_does_exist",
            )


class FeeItem(BaseItem):
    def __init__(self, cart: "Cart") -> None:
        self._cart = cart
        self.amount = 0
        self.name = "運費"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "amount": self.amount,
        }


class MultiItem(BaseMultiItem):
    item_cls = FeeItem


class Cart(BaseCart):
    product_multi_item_cls = ProductMultiItem
    extra_multi_item_cls = MultiItem
    discount_multi_item_cls = MultiItem
    config_cls = CartConfig

    user_collection: Collection
    cart_collection: Collection
    user: MutableMapping[str, Any]

    def __init__(self, identity: str):
        self._user = self.load_user(identity)
        super().__init__(identity)

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


__all__ = [
    "cart_exception_handler",
    "Cart",
    "ProductItem",
    "ProductMultiItem",
    "FeeItem",
    "MultiItem",
]
