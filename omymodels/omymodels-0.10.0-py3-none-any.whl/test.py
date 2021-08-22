from omymodels import convert_models, create_models

models_from = """

    import sqlalchemy as sa
    from sqlalchemy.ext.declarative import declarative_base
    from enum import Enum
    from sqlalchemy.sql import func
    from sqlalchemy.dialects.postgresql import JSON
    
    
    Base = declarative_base()
    
    
    class MaterialType(str, Enum):
    
        article = 'article'
        video = 'video'
    
    
    class Material(Base):
    
        __tablename__ = 'material'
    
        id = sa.Column(sa.Integer(), autoincrement=True, primary_key=True)
        title = sa.Column(sa.String(), nullable=False)
        description = sa.Column(sa.Text())
        link = sa.Column(sa.String(), nullable=False)
        type = sa.Column(sa.Enum(MaterialType))
        additional_properties = sa.Column(JSON(), server_default='{"key": "value"}')
        created_at = sa.Column(sa.TIMESTAMP(), server_default=func.now())
        updated_at = sa.Column(sa.TIMESTAMP())
"""
# result = create_models(ddl)['code']
result = convert_models(models_from, models_type="gino")
print(result)
