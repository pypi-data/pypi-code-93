import inspect
from datetime import datetime
from functools import lru_cache
from typing import Any, Dict, List, Optional, Set, Tuple, Type, cast

from tortoise import Tortoise, fields
from tortoise.backends.base.client import BaseDBAsyncClient
from tortoise.contrib.pydantic import PydanticModel, pydantic_model_creator
from tortoise.contrib.pydantic.creator import PydanticMeta
from tortoise.models import Field, MetaInfo, Model

from .patch import patch_pydantic


class BaseModel(Model):
    id: int = fields.IntField(pk=True)
    created_at: datetime = fields.DatetimeField(null=False, auto_now_add=True)
    updated_at: datetime = fields.DatetimeField(null=False, auto_now=True)

    class Meta:
        abstract = True

    # class PydanticMeta:
    #     computed: Tuple[str, ...] = ()  # 计算量, 异步计算量返回值需要标记为 Optional
    #     list_exclude: Tuple[str, ...] = ()  # 列表排除
    #     detail_include: Tuple[str, ...] = ()  # 详情叠加
    #     form_exclude: Tuple[str, ...] = ()  # 表单排除

    class FormPydanticMeta:
        computed = []

    async def dict(self, prefetch: Optional[List[str]] = None) -> Dict[str, Any]:
        if prefetch:
            await self.fetch_related(*prefetch)
        return self.detail().from_orm(self).dict()

    @classmethod
    @lru_cache
    def list(cls) -> Type[PydanticModel]:
        meta: Optional[PydanticMeta] = getattr(cls, "PydanticMeta", None)
        list_exclude: Tuple[str, ...] = meta and getattr(meta, "list_exclude", ()) or ()
        return cls.make_pydantic(name="list", exclude=list_exclude)

    @classmethod
    @lru_cache
    def detail(
        cls,
        required_override: Optional[bool] = None,
        from_models: Tuple[str, ...] = (),
    ) -> Type[PydanticModel]:
        meta: Optional[PydanticMeta] = getattr(cls, "PydanticMeta", None)
        detail_include: Tuple[str, ...] = (
            meta and getattr(meta, "detail_include", ()) or ()
        )
        return cls.make_pydantic(
            name="detail",
            include=detail_include,
            required_override=required_override,
            from_models=from_models,
        )

    @classmethod
    @lru_cache
    def form(
        cls,
        required_override: Optional[bool] = None,
        from_models: Tuple[str, ...] = (),
    ) -> Type[PydanticModel]:
        meta: Optional[PydanticMeta] = getattr(cls, "PydanticMeta", None)
        form_exclude: Tuple[str, ...] = meta and getattr(meta, "form_exclude", ()) or ()
        return cls.make_pydantic(
            name="form",
            exclude=(*form_exclude, "id", "created_at", "updated_at"),
            required_override=required_override,
            from_models=from_models,
            is_form=True,
        )

    @classmethod
    def make_pydantic(
        cls,
        name: str,
        include: Optional[Tuple[str, ...]] = None,
        exclude: Optional[Tuple[str, ...]] = None,
        required_override: Optional[bool] = None,
        from_models: Tuple[str, ...] = (),
        is_form: bool = False,
    ):
        parts = [cls.__module__, cls.__qualname__, name]
        if from_models:
            parts.append("in")
            parts += from_models
        if required_override is not None:
            parts.append("required" if required_override else "optional")

        return patch_pydantic(
            pydantic_model_creator(
                cls,
                name=".".join(parts),
                include=include or (),
                exclude=exclude or (),
                meta_override=cls.FormPydanticMeta if is_form else None,
            ),
            from_models=(*from_models, cls.__qualname__),
            required_override=required_override,
            is_form=is_form,
        )

    def update(self, input: Any):
        dic: Dict[str, Any] = (
            input if isinstance(input, dict) else input.dict(exclude_unset=True)
        )
        self.update_from_dict(dic)  # type: ignore

    async def fetch_related(
        self, *args: Any, using_db: Optional[BaseDBAsyncClient] = None
    ) -> None:
        meta: Optional[PydanticMeta] = getattr(self.__class__, "PydanticMeta", None)
        computed: Set[str]
        if meta and hasattr(meta, "computed"):
            computed = set(meta.computed)
            for field in args:
                if field in computed:
                    f = getattr(self, field, None)
                    if not f:
                        continue
                    if inspect.iscoroutinefunction(f):
                        setattr(self, field, await f())
        else:
            computed = set()

        normlized_args = [
            self.normalize_field(field) if isinstance(field, str) else field
            for field in args
            if field not in computed
        ]
        return await super().fetch_related(*normlized_args, using_db=using_db)

    @classmethod
    async def save_related(cls, raw: Any) -> Tuple[Any, Dict[str, Any]]:
        meta: MetaInfo = getattr(cls, "_meta")

        # 保存 ForeignKeyField
        fk_fields: Set[str] = meta.fk_fields
        for fk_field_name in fk_fields:
            v: Optional[Any] = raw.pop(fk_field_name, None)
            if not v:
                continue

            field_model: Type[BaseModel] = cast(
                Type[BaseModel], cls.get_field_model(fk_field_name)
            )

            v_id = v.pop("id", None)
            if v_id:
                field_value: Optional[BaseModel] = await field_model.filter(
                    id=v_id
                ).first()
                assert field_value
                field_value.update(v)
            else:
                field_value = field_model(**v)
            await field_value.save()
            raw[fk_field_name] = field_value

        # 保存 ManyToMany
        m2m_raw: Dict[str, Any] = {}
        m2m_fields: Set[str] = meta.m2m_fields
        for m2m_field_name in m2m_fields:
            v: Optional[Any] = raw.pop(m2m_field_name, None)
            if not v:
                continue
            assert isinstance(v, List)
            vs: List[Any] = v

            field_model: Type[BaseModel] = cast(
                Type[BaseModel], cls.get_field_model(m2m_field_name)
            )

            field_values: List[BaseModel] = []
            for v in vs:
                assert v
                v_id = v.pop("id", None)
                if v_id:
                    field_value: Optional[BaseModel] = await field_model.filter(
                        id=v_id
                    ).first()
                    assert field_value
                    field_value.update(v)
                else:
                    field_value = field_model(**v)
                await field_value.save()
                field_values.append(field_value)

            if field_values:
                m2m_raw[m2m_field_name] = field_values

        return raw, m2m_raw

    @staticmethod
    def normalize_field(field: str) -> str:
        return field.replace(".", "__")

    @classmethod
    @lru_cache
    def get_model(cls, model_name: str) -> Optional[Type[Model]]:
        parts: List[str] = model_name.split(".")
        if len(parts) == 1:
            parts.insert(0, next(iter(Tortoise.apps)))
        return cast(
            Optional[Type[BaseModel]],
            Tortoise.apps.get(parts[0], {}).get(parts[1], None),
        )

    @classmethod
    @lru_cache
    def get_field(
        cls, model_name: str, field_name: str
    ) -> Tuple[Optional[Type[Model]], Optional[Field]]:
        model = cls.get_model(model_name)
        meta: Optional[MetaInfo] = model and getattr(model, "_meta")
        field = model and meta and meta.fields_map.get(field_name)
        return model, field

    @classmethod
    @lru_cache
    def get_field_model(cls, field: str) -> Type[Model]:
        meta: MetaInfo = getattr(cls, "_meta")
        fields_map = meta.fields_map
        fk_field = fields_map[field]
        model_name = getattr(fk_field, "model_name")
        model = cls.get_model(model_name)
        assert model
        return model
