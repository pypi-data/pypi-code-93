from enum import IntEnum
from typing import (
    Any,
    Callable,
    Coroutine,
    Dict,
    Generic,
    List,
    Type,
    TypeVar,
    Union,
    cast,
)

from fastapi import APIRouter, Body, Depends, Path, Query, status
from fastapi.responses import ORJSONResponse
from pydantic import BaseModel as PydanticBaseModel
from pydantic import create_model
from tortoise.queryset import Q, QuerySet
from tortoise.transactions import atomic

from .. import json
from ..model import BaseModel
from .exceptions import HTTPNotFoundError

UserModel = TypeVar("UserModel")
Model = TypeVar("Model", bound=BaseModel)
CreateForm = TypeVar("CreateForm", bound=PydanticBaseModel)
UpdateForm = TypeVar("UpdateForm", bound=PydanticBaseModel)


class ResourceMethod(IntEnum):
    list = 0
    get = 1
    create = 2
    put = 3
    delete = 4


class API(Generic[UserModel, Model, CreateForm, UpdateForm]):
    def __init__(
        self,
        model: Type[Model],
        create_form: Type[CreateForm],
        update_form: Type[UpdateForm],
        get_current_user: Callable[
            ..., Union[Coroutine[Any, Any, UserModel], UserModel]
        ],
        enable_create: bool = True,
        enable_update: bool = True,
        enable_delete: bool = True,
        enable_get: bool = True,
    ) -> None:
        super().__init__()
        self.model = model
        self.create_form = create_form
        self.update_form = update_form
        self.get_current_user = get_current_user
        self.enable_create = enable_create
        self.enable_update = enable_update
        self.enable_delete = enable_delete
        self.enable_get = enable_get

    def translate_id(self, user: UserModel, id: str) -> str:
        return id

    def q(
        self,
        user: UserModel,
        q: QuerySet[Model],
        method: ResourceMethod = ResourceMethod.list,
    ) -> QuerySet[Model]:
        return q

    async def before_create(
        self, user: UserModel, obj: Model, input: CreateForm
    ) -> Model:
        return obj

    async def after_create(self, user: UserModel, obj: Model, input: CreateForm) -> Any:
        return obj

    async def before_update(
        self, user: UserModel, obj: Model, input: UpdateForm
    ) -> Model:
        return obj

    async def after_update(self, user: UserModel, obj: Model, input: UpdateForm) -> Any:
        return obj

    async def before_delete(self, user: UserModel, obj: Model) -> Model:
        return obj

    @classmethod
    def ids_path(cls):
        return Path(..., title="ID", description="支持采用 `1,2,3` 形式传入多个")

    @classmethod
    def prefetch_query(cls):
        return Query(
            [],
            title="动态加载计算字段",
            description="获取更多字段, 支持采用 `prefetch=id&prefetch=user.id` 形式传入多个",
        )

    @classmethod
    def get_form_type(cls, form: Any) -> Any:
        f = getattr(form, "form_type", None)
        return f and f() or Body(...)

    def bind(self, router: APIRouter):
        ListPydanticModel = self.model.list()
        DetailPydanticModel = self.model.detail()
        CreateForm = self.create_form
        UpdateForm = self.update_form

        DetailPydanticModels = Union[
            DetailPydanticModel, List[DetailPydanticModel]  # type: ignore
        ]
        Response = create_model(
            f"{self.model.__name__}.Response",
            __base__=PydanticBaseModel,
            total=0,
            data=(List[ListPydanticModel], ...),  # type: ignore
        )

        methods: Dict[str, Callable[..., Any]] = {}

        if self.enable_create:

            @router.post(
                "/",
                response_model=DetailPydanticModels,
                response_class=ORJSONResponse,
                status_code=status.HTTP_201_CREATED,
            )
            @atomic()
            async def create(
                input: Union[CreateForm, List[CreateForm]] = self.get_form_type(
                    CreateForm
                ),
                prefetch: List[str] = self.prefetch_query(),
                current_user: UserModel = Depends(self.get_current_user),
            ) -> Any:
                is_batch = isinstance(input, list)
                inputs = cast(List[CreateForm], input if is_batch else [input])

                returns: List[PydanticBaseModel] = []
                for inpu in inputs:
                    raw: Dict[str, Any] = inpu.dict(exclude_unset=True)
                    raw, m2m_raw = await self.model.save_related(raw)
                    obj = self.model(**raw)

                    obj_rtn = await self.before_create(current_user, obj, inpu)
                    if obj_rtn is not obj:
                        obj = obj_rtn

                    await obj.save()
                    prefetch = list(set([*prefetch, *m2m_raw.keys()]))
                    for k, v in m2m_raw.items():
                        await getattr(obj, k).add(*v)
                    if prefetch:
                        await obj.fetch_related(*prefetch)

                    obj_rtn = await self.after_create(current_user, obj, inpu)
                    if obj_rtn and obj_rtn is not obj:
                        obj = obj_rtn

                    if isinstance(obj, PydanticBaseModel):
                        returns.append(obj)
                    else:
                        returns.append(DetailPydanticModel.from_orm(obj))
                return returns if is_batch else returns[0]

            methods["create"] = create

        if self.enable_get:
            help = """支持采用 `condition=...&condition=...` 传入多个, 使用 JSON 序列化

###### 简单查询

```javascript
{
    "email": "name@example.com",
    "name.contains": "name",
    "id.in": [1, 2, 3],
}
```

###### 跨表查询

```javascript
{
    "user.email": "name@example.com",
    "user.name.contains": "name",
}
```

###### 运算方式, 可选项: `and` `or` `not` `not_or`

```javascript
{
    ".logic": "or",
    "name.contains": "name",
    "email.contains": "example.com",
}
```
            """

            @router.get("/", response_model=Response, response_class=ORJSONResponse)
            async def index(
                offset: int = Query(0, title="分页偏移"),
                limit: int = Query(20, title="分页限额"),
                condition: List[str] = Query([], title="查询条件", description=help),
                order_by: List[str] = Query(
                    [],
                    title="排序",
                    description="支持采用 `order_by=id&order_by=user.id` 形式传入多个",
                ),
                prefetch: List[str] = self.prefetch_query(),
                current_user: UserModel = Depends(self.get_current_user),
            ) -> Any:
                q = self.model.all()
                q = self.q(current_user, q, ResourceMethod.list)

                # 通用过滤方案
                # https://tortoise-orm.readthedocs.io/en/latest/query.html
                if condition:
                    for raw in condition:
                        kv = json.loads(raw)
                        reverse = False
                        join_type = kv.pop(".logic", "AND").upper()
                        if join_type == "NOT":
                            reverse = True
                            join_type = "AND"
                        elif join_type == "NOT_OR":
                            reverse = True
                            join_type = "OR"
                        condition_q = Q(
                            **{
                                self.model.normalize_field(k): safe_condition_value(v)
                                for k, v in kv.items()
                            },
                            join_type=join_type,
                        )
                        if reverse:
                            condition_q = ~condition_q
                        q = q.filter(condition_q)

                q = q.distinct()
                total = await q.count()

                if order_by:
                    for item in order_by:
                        q = q.order_by(self.model.normalize_field(item))

                objs = await q.offset(offset).limit(limit)

                if prefetch:
                    for obj in objs:
                        await obj.fetch_related(*prefetch)

                return Response(
                    total=total,
                    data=[ListPydanticModel.from_orm(obj) for obj in objs],
                )

            @router.get(
                "/{id}",
                response_model=DetailPydanticModel,
                response_class=ORJSONResponse,
            )
            @atomic()
            async def get(
                id: str = Path(..., title="id"),
                prefetch: List[str] = self.prefetch_query(),
                current_user: UserModel = Depends(self.get_current_user),
            ) -> Any:
                id = self.translate_id(current_user, id)
                q = self.q(
                    current_user,
                    self.model.all().filter(id=id),
                    ResourceMethod.get,
                )
                obj = await q.first()
                if not obj:
                    raise HTTPNotFoundError
                if prefetch:
                    await obj.fetch_related(*prefetch)
                return DetailPydanticModel.from_orm(obj)

            methods["index"] = index
            methods["get"] = get

        if self.enable_update:

            @router.put(
                "/{ids}",
                response_model=DetailPydanticModels,
                response_class=ORJSONResponse,
            )
            @atomic()
            async def update(
                ids: str = self.ids_path(),
                input: UpdateForm = self.get_form_type(UpdateForm),
                prefetch: List[str] = self.prefetch_query(),
                current_user: UserModel = Depends(self.get_current_user),
            ) -> Any:
                rtns: List[Any] = []
                raw = input.dict(exclude_unset=True)
                for id in ids.split(","):
                    id = id.strip()
                    id = self.translate_id(current_user, id)
                    obj = await self.q(
                        current_user,
                        self.model.filter(id=id),
                        ResourceMethod.put,
                    ).get()

                    obj_rtn = await self.before_update(current_user, obj, input)
                    if obj_rtn is not obj:
                        obj = obj_rtn

                    raw, m2m_raw = await self.model.save_related(raw)
                    obj.update(raw)

                    await obj.save()
                    obj_prefetch = list(set([*prefetch, *m2m_raw.keys()]))
                    for k, v in m2m_raw.items():
                        await getattr(obj, k).add(*v)
                    if obj_prefetch:
                        await obj.fetch_related(*obj_prefetch)

                    obj_rtn = await self.after_update(current_user, obj, input)
                    if obj_rtn and obj_rtn is not obj:
                        obj = obj_rtn

                    rtns.append(
                        obj
                        if isinstance(obj, PydanticBaseModel)
                        else DetailPydanticModel.from_orm(obj)
                    )
                return len(rtns) > 1 and rtns or rtns[0]

            methods["update"] = update

        if self.enable_delete:

            @router.delete(
                "/{ids}",
                response_model=DetailPydanticModels,
                response_class=ORJSONResponse,
            )
            @atomic()
            async def delete(
                ids: str = self.ids_path(),
                current_user: UserModel = Depends(self.get_current_user),
            ) -> Any:
                rtns: List[Any] = []
                for id in ids.split(","):
                    id = self.translate_id(current_user, id)
                    obj = await self.q(
                        current_user,
                        self.model.filter(id=id),
                        ResourceMethod.delete,
                    ).get()
                    obj_rtn = await self.before_delete(current_user, obj)
                    if obj_rtn is not obj:
                        obj = obj_rtn

                    await obj.delete()
                    rtns.append(DetailPydanticModel.from_orm(obj))
                return len(rtns) > 1 and rtns or rtns[0]

            methods["delete"] = delete

        return methods


def safe_condition_value(
    v: Union[List[Any], Any]
) -> Union[str, float, List[Union[str, float]]]:
    if isinstance(v, List):
        rs: List[Union[str, float]] = []
        for e in v:
            r = safe_condition_value(e)
            assert not isinstance(r, list)
            rs.append(r)
        return rs
    return v if isinstance(v, float) else str(v)


def get_anonymous_user() -> Dict[str, str]:
    return {}


class PublicAPI(API[object, Model, CreateForm, UpdateForm]):
    def __init__(
        self,
        model: Type[Model],
        create_form: Type[CreateForm],
        update_form: Type[UpdateForm],
        enable_create: bool = True,
        enable_update: bool = True,
        enable_delete: bool = True,
        enable_get: bool = True,
    ) -> None:
        super().__init__(
            model,
            create_form=create_form,
            update_form=update_form,
            get_current_user=get_anonymous_user,
            enable_create=enable_create,
            enable_update=enable_update,
            enable_delete=enable_delete,
            enable_get=enable_get,
        )
