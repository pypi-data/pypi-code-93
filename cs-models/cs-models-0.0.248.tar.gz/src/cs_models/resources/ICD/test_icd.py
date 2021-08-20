from marshmallow import ValidationError
from freezegun import freeze_time
from test.backendtestcase import TestCase
from sqlalchemy.orm import Session
from src.cs_models.database import engine, operations
from src.cs_models.resources.ICD.models import ICDModel
from src.cs_models.resources.ICD.schemas import ICDResourceSchema


@freeze_time("2020-01-01")
class ICDResourceTestCase(TestCase):
    def setUp(self):
        super(ICDResourceTestCase, self).setUp()
        with operations.session_scope() as session:
            self.icd1 = operations.create(
                session=session,
                model=ICDModel,
                schema=ICDResourceSchema,
                obj={
                    "icd_code": "3B10",
                    "description": "['VIII deficiency', 'Haemophilia A', "
                                   "'anti-factor VIII inhibitor', 'Hereditary factor VIII deficiency']",
                    "class_kind": "category",
                    "is_leaf": False,
                },
            )

        self.valid_data = {
            'icd_code': '3A21',
            'description': "['haemolytic anaemia', 'Paroxysmal nocturnal "
                           "haemoglobinuria', 'Microangiopathic haemolytic anaemia']",
            'class_kind': 'category',
            'is_leaf': False
        }

    def test_create_inside_context_manager(self):
        with operations.session_scope() as session:
            instance = operations.create(
                session=session,
                model=ICDModel,
                schema=ICDResourceSchema,
                obj={
                    "icd_code": "3A50",
                    "description": "['Thalassaemias', 'Haemoglobin H disease']",
                    "class_kind": "category",
                    "is_leaf": False,
                },
            )
            self.assertEqual(
                ICDResourceSchema().dump(instance).data,
                {
                    "icd_code": '3A50',
                    "description": "['Thalassaemias', 'Haemoglobin H disease']",
                    "id": 2,
                    "class_kind": "category",
                    "is_leaf": False,
                    "updated_at": "2020-01-01T00:00:00+00:00",
                },
            )

    def test_create(self):
        session = Session(bind=engine)
        try:
            instance = operations.create(
                session=session,
                model=ICDModel,
                schema=ICDResourceSchema,
                obj={
                    "icd_code": "3A50",
                    "description": "['Thalassaemias', 'Haemoglobin H disease']",
                    "class_kind": "category",
                    "is_leaf": False,
                },
            )
            self.assertEqual(
                ICDResourceSchema().dump(instance).data,
                {
                    "icd_code": '3A50',
                    "description": "['Thalassaemias', 'Haemoglobin H disease']",
                    "id": 2,
                    "class_kind": "category",
                    "is_leaf": False,
                    "updated_at": "2020-01-01T00:00:00+00:00",
                },
            )

            # This commit is not really needed since
            # we commit in `create` but is done for consistency.
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def test_create_validation_error(self):
        session = Session(bind=engine)
        self.assertRaises(
            ValidationError,
            operations.create,
            session,
            ICDModel,
            ICDResourceSchema,
            {
                "icd_code": "3A50",
                "description": "",
                "class_kind": "category",
                "is_leaf": False,
            },
        )

    def test_update_or_create(self):
        with operations.session_scope() as session:
            instance, created = operations.update_or_create(
                session=session,
                model=ICDModel,
                schema=ICDResourceSchema,
                query_fields=["icd_code"],
                obj={
                    "icd_code": "3A50",
                    "description": "['Thalassaemias', 'Haemoglobin H disease']",
                    "class_kind": "category",
                    "is_leaf": False,
                },
            )
            self.assertEqual(
                ICDResourceSchema().dump(instance).data,
                {
                    "icd_code": "3A50",
                    "id": 2,
                    "description": "['Thalassaemias', 'Haemoglobin H disease']",
                    "class_kind": "category",
                    "is_leaf": False,
                    "updated_at": "2020-01-01T00:00:00+00:00",
                },
            )
            self.assertTrue(created)

            instance, created = operations.update_or_create(
                session=session,
                model=ICDModel,
                schema=ICDResourceSchema,
                query_fields=["icd_code"],
                obj={
                    "icd_code": "3A50",
                    "description": "['Hemophilia']",
                    "class_kind": "category",
                    "is_leaf": False,
                },
            )
            self.assertEqual(
                ICDResourceSchema().dump(instance).data,
                {
                    "icd_code": "3A50",
                    "id": 2,
                    "description": "['Hemophilia']",
                    "class_kind": "category",
                    "is_leaf": False,
                    "updated_at": "2020-01-01T00:00:00+00:00",
                },
            )
            self.assertFalse(created)

    def test_bulk_save(self):
        """Verifies that new objects are created in bulk."""
        with operations.session_scope() as session:
            operations.bulk_save(
                session=session,
                instances=[
                    ICDModel(**obj)
                    for obj in [
                        {
                            "icd_code": "3A50",
                            "description": "['Hemophilia']",
                            "class_kind": "category",
                            "is_leaf": False,
                        },
                        {
                            "icd_code": "3A60",
                            "description": "['Colitis']",
                            "class_kind": "category",
                            "is_leaf": False,
                        },
                    ]
                ],
            )
            self.assertEqual(
                ICDResourceSchema()
                .dump(session.query(ICDModel).all(), many=True)
                .data,
                [
                    {
                        "id": 1,
                        "icd_code": "3B10",
                        "description": "['VIII deficiency', 'Haemophilia A', "
                                       "'anti-factor VIII inhibitor', 'Hereditary factor VIII deficiency']",
                        "class_kind": "category",
                        "is_leaf": False,
                        "updated_at": "2020-01-01T00:00:00+00:00",
                    },
                    {
                        "id": 2,
                        "icd_code": "3A50",
                        "description": "['Hemophilia']",
                        "class_kind": "category",
                        "is_leaf": False,
                        "updated_at": "2020-01-01T00:00:00+00:00",
                    },
                    {
                        "id": 3,
                        "icd_code": "3A60",
                        "description": "['Colitis']",
                        "class_kind": "category",
                        "is_leaf": False,
                        "updated_at": "2020-01-01T00:00:00+00:00",
                    },
                ],
            )

    def test_bulk_save_updates_and_creates(self):
        with operations.session_scope() as session:
            instance1 = operations.create(
                session=session,
                model=ICDModel,
                schema=ICDResourceSchema,
                obj={
                    "icd_code": "3A50",
                    "description": "['Hemophilia']",
                    "class_kind": "category",
                    "is_leaf": False,
                },
            )
            instance2 = operations.create(
                session=session,
                model=ICDModel,
                schema=ICDResourceSchema,
                obj={
                    "icd_code": "3A60",
                    "description": "['Colitis']",
                    "class_kind": "category",
                    "is_leaf": False,
                },
            )
            instance1.description = "['Hemophilia A']"
            instance2.class_kind = "block"

            operations.bulk_save(
                session=session,
                instances=[
                    instance1,
                    instance2,
                    ICDModel(
                        **{
                            "icd_code": "3A70",
                            "description": "['Cancer']",
                            "class_kind": "category",
                            "is_leaf": False,
                        }
                    ),
                    ICDModel(
                        **{
                            "icd_code": "3A80",
                            "description": "['Alzheimer']",
                            "class_kind": "category",
                            "is_leaf": False,
                        }
                    ),
                ],
            )

            self.assertEqual(
                [
                    {
                        "id": 1,
                        "icd_code": "3B10",
                        "description": "['VIII deficiency', 'Haemophilia A', "
                                       "'anti-factor VIII inhibitor', 'Hereditary factor VIII deficiency']",
                        "class_kind": "category",
                        "is_leaf": False,
                        "updated_at": "2020-01-01T00:00:00+00:00",
                    },
                    {
                        "id": 2,
                        "icd_code": "3A50",
                        "description": "['Hemophilia A']",
                        "class_kind": "category",
                        "is_leaf": False,
                        "updated_at": "2020-01-01T00:00:00+00:00",
                    }
                    ,
                    {
                        "id": 3,
                        "icd_code": "3A60",
                        "description": "['Colitis']",
                        "class_kind": "block",
                        "is_leaf": False,
                        "updated_at": "2020-01-01T00:00:00+00:00",
                    },
                    {
                        "id": 4,
                        "icd_code": "3A70",
                        "description": "['Cancer']",
                        "class_kind": "category",
                        "is_leaf": False,
                        "updated_at": "2020-01-01T00:00:00+00:00",
                    },
                    {
                        "id": 5,
                        "icd_code": "3A80",
                        "description": "['Alzheimer']",
                        "class_kind": "category",
                        "is_leaf": False,
                        "updated_at": "2020-01-01T00:00:00+00:00",
                    },
                ],
                ICDResourceSchema()
                .dump(session.query(ICDModel).all(), many=True)
                .data,
            )
