import sqlalchemy as db
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy.orm.decl_api import declared_attr

def get_default_Base_cls():
    class BaseModel:
            __abstract__ = True

            @declared_attr
            def __tablename__(cls):
                return cls.__name__.lower()

            id = db.Column(db.Integer, primary_key=True, nullable=False, autoincrement=True)
    
    return BaseModel


def makeBase(Base_cls: type = get_default_Base_cls()):
    registry = db.orm.registry()
    return registry.generate_base(cls = Base_cls)


