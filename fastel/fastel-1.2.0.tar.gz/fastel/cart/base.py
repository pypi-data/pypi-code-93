import abc
import copy
import json
from typing import Any, Dict, Iterator, MutableMapping, Optional, Sequence, Type, Union

from bson import json_util
from pydantic import BaseModel, ValidationError

from .exceptions import CartException


class BaseCartConfig(BaseModel):
    @classmethod
    def model_with_optional_fields(cls: Type[BaseModel]) -> Type[BaseModel]:
        """Generate a `BaseModel` class with all the same fields as `model` but as optional"""

        class OptionalModel(cls):  # type: ignore
            ...

        for field in OptionalModel.__fields__.values():
            field.required = False

        # for generated schema for example (can be removed)
        OptionalModel.__name__ = f"Optional{cls.__name__}"

        return OptionalModel

    @classmethod
    def validate_optional(cls, value: Any) -> BaseModel:
        return cls.model_with_optional_fields().validate(value)


class BaseCart(
    metaclass=abc.ABCMeta,
):
    config_cls: Type[BaseCartConfig]

    _cache_cart: MutableMapping[str, Any]

    _total: int
    _tax: int
    _sales: int
    _fee: int

    items: "BaseMultiProductItem"
    extra_items: "BaseMultiItem"
    discount_items: "BaseMultiItem"

    INITIAL_CART = {
        "items": [],
        "extra_items": [],
        "discount_items": [],
        "total": 0,
        "subtotal": 0,
        "sales": 0,
        "tax": 0,
        "fee": 0,
    }

    @property
    @abc.abstractmethod
    def product_multi_item_cls(self) -> Type["BaseMultiProductItem"]:
        raise NotImplementedError("product_multi_item_cls")

    @property
    @abc.abstractmethod
    def extra_multi_item_cls(self) -> Type["BaseMultiItem"]:
        raise NotImplementedError("extra_multi_item_cls")

    @property
    @abc.abstractmethod
    def discount_multi_item_cls(self) -> Type["BaseMultiItem"]:
        raise NotImplementedError("discount_multi_item_cls")

    def __init__(self, identity: Any):
        self._identity = identity
        self._cache_cart = self.load_cart(identity)

        self.initial_validate()

    def __getattr__(self, item: str) -> Any:
        if item in self.config_cls.__fields__:
            return self._cache_cart[item]
        return self.__dict__[item]

    def __setattr__(self, key: str, value: Any) -> None:
        if key in self.config_cls.__fields__:
            self._set_cart(key, value)
        else:
            self.__dict__[key] = value

    @property
    def total(self) -> int:
        return self._total

    @property
    def subtotal(self) -> int:
        return self.items.total

    @property
    def tax(self) -> int:
        return self._tax

    @property
    def sales(self) -> int:
        return self._sales

    @property
    def fee(self) -> int:
        return self._fee

    @abc.abstractmethod
    def _set_cart(self, key: str, value: Any) -> None:
        raise NotImplementedError("_set_cart")

    @abc.abstractmethod
    def load_cart(self, identity: Any) -> MutableMapping[str, Any]:
        raise NotImplementedError("load_cart")

    def initial_validate(self) -> None:
        self.items = self.product_multi_item_cls(
            self,
            items=[
                self.product_multi_item_cls.item_cls.validate(
                    item["product"]["id"], item["config"], self
                )
                for item in self._cache_cart["items"]
            ],
        )
        self.extra_items = self.extra_multi_item_cls(
            self, items=[self.extra_multi_item_cls.item_cls(self)]  # type: ignore
        )
        self.discount_items = self.discount_multi_item_cls(self, items=[])
        self.refresh_attrs()
        self.save_cart()

    def to_dict(self) -> MutableMapping[str, Any]:
        cart_dict = copy.deepcopy(self._cache_cart)
        cart_dict = json.loads(json_util.dumps(cart_dict))
        return cart_dict

    def refresh_attrs(self) -> None:
        self._cache_cart["items"] = self.items.to_dict()

        extra_items = [self.extra_multi_item_cls.item_cls(self)]  # type: ignore
        self.extra_items = self.extra_multi_item_cls(self, extra_items)
        self._cache_cart["extra_items"] = self.extra_items.to_dict()

        self._fee = self.extra_items.total
        self._cache_cart["fee"] = self.fee

        self._total: int = self.items.total + self.extra_items.total
        self._cache_cart["total"] = self.total

        self._tax: int = round(self._total * 0.05)
        self._cache_cart["tax"] = self.tax

        self._sales: int = self._total - self._tax
        self._cache_cart["sales"] = self.sales

    def add_item(self, product_id: str, config: BaseModel) -> MutableMapping[str, Any]:
        self.items.add_item(product_id, config)

        self.refresh_attrs()
        self.save_cart()
        return self.to_dict()

    def delete_item(self, index: int) -> MutableMapping[str, Any]:
        self.items.delete_item(index)
        self.refresh_attrs()
        self.save_cart()
        return self.to_dict()

    def edit_item(self, index: int, config: BaseModel) -> MutableMapping[str, Any]:
        self.items.edit_item(index, config)

        self.refresh_attrs()
        self.save_cart()
        return self.to_dict()

    def edit_config(
        self, config: Union[Dict[str, Any], BaseModel]
    ) -> MutableMapping[str, Any]:
        if not isinstance(config, BaseModel):
            try:
                config = self.config_cls.validate_optional(config)
            except ValidationError:
                raise CartException("validation_error")

        for key, value in config.dict(exclude_unset=True).items():
            setattr(self, key, value)

        self.refresh_attrs()
        self.save_cart()
        return self.to_dict()

    def empty_cart(self) -> MutableMapping[str, Any]:
        self.items.clean_item()
        self._total = 0
        self._sales = 0
        self._fee = 0
        self._tax = 0
        self.save_cart()
        return self.to_dict()

    @abc.abstractmethod
    def save_cart(self) -> None:
        raise NotImplementedError("save_cart")


class BaseItem:
    config_cls: Type[BaseModel]
    amount: int
    name: str
    _cart: Optional[BaseCart]

    @classmethod
    def validate(cls, *args: Any, **kwargs: Any) -> Any:
        raise NotImplementedError("validate")

    def to_dict(self) -> Dict[str, Any]:
        raise NotImplementedError("to_dict() should be implemented")


class BaseMultiItem:
    item_cls: Type[BaseItem]

    _total: int
    _sales: int
    _tax: int

    def __init__(self, cart: "BaseCart", items: Sequence[BaseItem]) -> None:
        self.items = list(items)
        self._cart = cart
        self.refresh_attrs()

    def __len__(self) -> int:
        return len(self.items)

    def __iter__(self) -> Iterator[BaseItem]:
        return iter(self.items)

    @property
    def total(self) -> int:
        return self._total

    @property
    def sales(self) -> int:
        return self._sales

    @property
    def tax(self) -> int:
        return self._tax

    def get_total(self) -> int:
        return sum([item.amount for item in self.items])

    def get_sales(self) -> int:
        return round(self.total / 1.05)

    def get_tax(self) -> int:
        return self.total - self.sales

    def to_dict(self) -> Sequence[Dict[str, Any]]:
        return [item.to_dict() for item in self.items]

    def clean_item(self) -> None:
        self.items = []
        self.refresh_attrs()

    def refresh_attrs(self) -> None:
        self._total = self.get_total()
        self._sales = self.get_sales()
        self._tax = self.get_tax()


class BaseMultiProductItem(BaseMultiItem):
    def add_item(self, product_id: str, config: BaseModel) -> None:
        raise NotImplementedError("add_item")

    def delete_item(self, index: int) -> None:
        raise NotImplementedError("delete_item")

    def edit_item(self, index: int, config: BaseModel) -> None:
        raise NotImplementedError("edit")
