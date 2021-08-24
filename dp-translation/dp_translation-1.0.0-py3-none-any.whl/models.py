import sqlalchemy as db
from dp_sqlalchemy_wrapper import makeBase
from sqlalchemy.orm import relationship

"""
LogicalEntity <--> LogicalEntityTranlsationInTargetLanguage <--> TargetLanguage 

"""
TranslationBase = makeBase()

class LogicalEntity(TranslationBase ):
    logical_key = db.Column(db.String, unique=True)
    translation_relations = relationship("LogicalEntityLanguageTranslationRelation", back_populates="logical_entity")

class LogicalEntityLanguageTranslationRelation(TranslationBase ):
    logical_key_ref = db.Column(db.String, nullable=False)
    code_ref = db.Column(db.String, nullable=False)
    translation = db.Column(db.String, nullable=False)
    language = relationship("Language", back_populates="translation_relations")
    logical_entity = relationship("LogicalEntity", back_populates="translation_relations")

class Language(TranslationBase):
    code = db.Column(db.String(2), unique=True, nullable=False) # ISO-639-1-Code
    translation_relations = relationship("LogicalEntityLanguageTranslationRelation", back_populates="language")
