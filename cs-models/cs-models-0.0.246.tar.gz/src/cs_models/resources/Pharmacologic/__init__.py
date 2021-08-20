from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

from cs_models.utils.utils import update_model
from ...database import db_session
from ...resources.Pharmacologic.models import PharmacologicModel
from .schemas import (
    PharmacologicPatchSchema,
    PharmacologicQueryParamsSchema,
    PharmacologicResourceSchema,
)


schema_resource = PharmacologicResourceSchema()
schema_params = PharmacologicQueryParamsSchema()
schema_patch = PharmacologicPatchSchema()


class Pharmacologic(object):
    @staticmethod
    def create(params):
        """
        Args:
            params: dict(PharmacologicResourceSchema)

        Returns: PharmacologicResourceSchema

        Raises:
            ValidationError
            SQLAlchemyError
        """
        data, errors = schema_resource.load(params)
        if errors:
            raise ValidationError(errors)
        response = _helper_create(data)
        return response

    @staticmethod
    def read(params):
        """
        Args:
            params: dict(PharmacologicQueryParamsSchema)

        Returns: List<PharmacologicResourceSchema>

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        pharmacologic_query = _build_query(params=data)
        response = schema_resource.dump(pharmacologic_query, many=True).data
        return response

    @staticmethod
    def one(params):
        """
        Args:
            params: dict(PharmacologicQueryParamsSchema)

        Returns: PharmacologicResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        pharmacologic_query = _build_query(params=data).one()
        response = schema_resource.dump(pharmacologic_query).data
        return response

    @staticmethod
    def update(id, params):
        """

        Args:
            id: int
            params: PharmacologicPatchSchema

        Returns:
            PharmacologicResourceSchema

        Raises:
            sqlalchemy.orm.exc.NoResultFound
            sqlalchemy.orm.exc.MultipleResultsFound
            ValidationError
        """
        pharmacologic_query = db_session.query(PharmacologicModel).filter_by(
            id=id).one()
        data, errors = schema_patch.load(params)
        if errors:
            raise ValidationError(errors)

        response = _helper_update(data, pharmacologic_query)
        return response

    @staticmethod
    def delete(id):
        """
        Args:
            id: int

        Returns: string

        Raises:
            sqlalchemy.orm.exc.NoResultFound
            sqlalchemy.orm.exc.MultipleResultsFound
            SQLAlchemyError
        """
        ndc_query = db_session.query(PharmacologicModel).filter_by(id=id).one()
        try:
            db_session.delete(ndc_query)
            db_session.commit()
            db_session.close()
            return "Successfully deleted"
        except SQLAlchemyError:
            db_session.rollback()
            db_session.close()
            raise


def _helper_create(data):
    new_pharmacologic = PharmacologicModel(**data)
    try:
        db_session.add(new_pharmacologic)
        db_session.commit()
        pharmacologic_query = db_session.query(PharmacologicModel).get(
            new_pharmacologic.id)
        response = schema_resource.dump(pharmacologic_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _helper_update(data, pharmacologic_query):
    data["id"] = pharmacologic_query.id
    try:
        update_model(data, pharmacologic_query)
        db_session.commit()
        response = schema_resource.dump(pharmacologic_query).data
        return response
    except SQLAlchemyError:
        db_session.rollback()
        raise


def _build_query(params):
    q = db_session.query(PharmacologicModel)
    if params.get("id"):
        q = q.filter_by(id=params.get("id"))
    if params.get("pharma_set_id"):
        q = q.filter_by(pharma_set_id=params.get("pharma_set_id"))
    if params.get("nui"):
        q = q.filter_by(nui=params.get("nui"))
    if params.get("class_name"):
        q = q.filter_by(class_name=params.get("class_name"))
    return q
