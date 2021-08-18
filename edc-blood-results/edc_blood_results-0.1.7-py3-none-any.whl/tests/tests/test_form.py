from django.apps import apps as django_apps
from django.test import TestCase
from edc_action_item import site_action_items
from edc_appointment.models import Appointment
from edc_constants.constants import NO, NOT_APPLICABLE, YES
from edc_lab.models import Panel
from edc_reportable import GRADE3, GRAMS_PER_DECILITER
from edc_utils import get_utcnow
from edc_visit_tracking.constants import SCHEDULED

from edc_blood_results.action_items import register_actions

from ..forms import BloodResultsFbcForm
from ..test_case_mixin import TestCaseMixin


class TestBloodResultForm(TestCaseMixin, TestCase):
    def setUp(self):
        super().setUp()
        site_action_items.registry = {}
        register_actions()
        self.subject_identifier = self.enroll()
        appointment = Appointment.objects.get(
            subject_identifier=self.subject_identifier,
            visit_code="1000",
        )
        subject_visit = django_apps.get_model("edc_metadata.subjectvisit").objects.create(
            report_datetime=get_utcnow(),
            appointment=appointment,
            reason=SCHEDULED,
        )
        panel = Panel.objects.get(name="fbc")
        requisition = django_apps.get_model("edc_metadata.subjectrequisition").objects.create(
            subject_visit=subject_visit,
            panel=panel,
            requisition_datetime=subject_visit.report_datetime,
        )
        self.data = dict(
            report_datetime=subject_visit.report_datetime,
            subject_visit=subject_visit,
            assay_datetime=subject_visit.report_datetime,
            requisition=requisition,
            tracking_identifier="X",
            action_identifier="-",
            results_reportable=NOT_APPLICABLE,
            results_abnormal=NO,
        )

    def test_ok(self):
        form = BloodResultsFbcForm(data=self.data)
        form.is_valid()
        self.assertEqual({}, form._errors)

    def test_missing_units(self):
        self.data.update(haemoglobin_value=10)
        form = BloodResultsFbcForm(data=self.data)
        form.is_valid()
        self.assertIn("haemoglobin_units", form._errors)

    def test_haemoglobin_abnormal_required(self):
        self.data.update(haemoglobin_value=10, haemoglobin_units=GRAMS_PER_DECILITER)
        form = BloodResultsFbcForm(data=self.data)
        form.is_valid()
        self.assertIn("haemoglobin_abnormal", form._errors)

    def test_haemoglobin_reportable_required(self):
        self.data.update(
            haemoglobin_value=10,
            haemoglobin_units=GRAMS_PER_DECILITER,
            haemoglobin_abnormal=NO,
        )
        form = BloodResultsFbcForm(data=self.data)
        form.is_valid()
        self.assertIn("haemoglobin_reportable", form._errors)

    def test_haemoglobin_normal(self):
        self.data.update(
            haemoglobin_value=14,
            haemoglobin_units=GRAMS_PER_DECILITER,
            haemoglobin_abnormal=NO,
            haemoglobin_reportable=NOT_APPLICABLE,
        )
        form = BloodResultsFbcForm(data=self.data)
        form.is_valid()
        self.assertEqual({}, form._errors)

    def test_haemoglobin_high(self):
        self.data.update(
            haemoglobin_value=18,
            haemoglobin_units=GRAMS_PER_DECILITER,
            haemoglobin_abnormal=YES,
            haemoglobin_reportable=NO,
            results_abnormal=YES,
            results_reportable=NO,
        )
        form = BloodResultsFbcForm(data=self.data)
        form.is_valid()
        self.assertEqual({}, form._errors)

    def test_haemoglobin_g4(self):
        self.data.update(
            haemoglobin_value=7.5,
            haemoglobin_units=GRAMS_PER_DECILITER,
            haemoglobin_abnormal=YES,
            haemoglobin_reportable=GRADE3,
            results_abnormal=YES,
            results_reportable=YES,
        )
        form = BloodResultsFbcForm(data=self.data)
        form.is_valid()
        self.assertEqual({}, form._errors)
