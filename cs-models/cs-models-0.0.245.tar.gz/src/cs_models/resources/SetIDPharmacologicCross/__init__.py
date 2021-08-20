from sqlalchemy.exc import SQLAlchemyError
from marshmallow import ValidationError

from ...database import db_session
from ...resources.SetIDPharmacologicCross.models import SetIDPharmacologicCrossModel
from .schemas import (
    SetIDPharmacologicCrossPatchSchema,
    SetIDPharmacologicCrossQueryParamsSchema,
    SetIDPharmacologicCrossResourceSchema,
)


schema_resource = SetIDPharmacologicCrossResourceSchema()
schema_params = SetIDPharmacologicCrossQueryParamsSchema()
schema_patch = SetIDPharmacologicCrossPatchSchema()


class SetIDPharmacologicCross(object):
    @staticmethod
    def create(params):
        """
        Args:
            params: dict(SetIDPharmacologicCrossResourceSchema)

        Returns: SetIDPharmacologicCrossResourceSchema

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
            params: dict(SetIDPharmacologicCrossQueryParamsSchema)

        Returns: List<SetIDPharmacologicCrossResourceSchema>

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        setid_pharmacologic_cross_query = _build_query(params=data)
        response = schema_resource.dump(setid_pharmacologic_cross_query, many=True).data
        return response

    @staticmethod
    def one(params):
        """
        Args:
            params: dict(SetIDPharmacologicCrossQueryParamsSchema)

        Returns: SetIDPharmacologicCrossResourceSchema

        Raises:
            ValidationError
        """
        data, errors = schema_params.load(params)
        if errors:
            raise ValidationError(errors)
        setid_pharmacologic_cross_query = _build_query(params=data).one()
        response = schema_resource.dump(setid_pharmacologic_cross_query).data
        return response


def _helper_create(data):
    new_setid_pharmacologic_cross = SetIDPharmacologicCrossModel(**data)
    try:
        db_session.add(new_setid_pharmacologic_cross)
        db_session.commit()
        setid_pharmacologic_query = db_session.query(
            SetIDPharmacologicCrossModel).get(
            new_setid_pharmacologic_cross.spl_set_id)
        response = schema_resource.dump(setid_pharmacologic_query).data
        db_session.close()
        return response
    except SQLAlchemyError:
        db_session.rollback()
        db_session.close()
        raise


def _build_query(params):
    q = db_session.query(SetIDPharmacologicCrossModel)
    if params.get("spl_set_id"):
        q = q.filter_by(spl_set_id=params.get("spl_set_id"))
    if params.get("pharma_set_id"):
        q = q.filter_by(pharma_set_id=params.get("pharma_set_id"))
    return q
