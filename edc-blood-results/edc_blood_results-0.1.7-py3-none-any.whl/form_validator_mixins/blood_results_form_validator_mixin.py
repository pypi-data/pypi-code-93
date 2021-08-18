from edc_lab.form_validators import CrfRequisitionFormValidatorMixin
from edc_reportable import ReportablesFormValidatorMixin


class BloodResultsFormValidatorMixin(
    ReportablesFormValidatorMixin,
    CrfRequisitionFormValidatorMixin,
):

    value_field_suffix = "_value"
    panel = None
    panels = None

    def evaluate_value(self, field_name):
        """A hook to evaluate a field value"""
        pass

    def clean(self):
        self.required_if_true(
            any(self.fields_names_with_values), field_required=self.requisition_field
        )

        requisition = self.validate_requisition(*self.panel_list)

        if requisition:
            for fields_name in self.fields_names_with_values:
                try:
                    utest_id, _ = fields_name.split(self.value_field_suffix)
                except ValueError:
                    utest_id = fields_name
                if f"{utest_id}_units" in self.cleaned_data:
                    self.required_if_not_none(
                        field=f"{utest_id}{self.value_field_suffix or ''}",
                        field_required=f"{utest_id}_units",
                        field_required_evaluate_as_int=True,
                    )
                if f"{utest_id}_abnormal" in self.cleaned_data:
                    self.required_if_not_none(
                        field=f"{utest_id}{self.value_field_suffix or ''}",
                        field_required=f"{utest_id}_abnormal",
                        field_required_evaluate_as_int=True,
                    )
                if f"{utest_id}_reportable" in self.cleaned_data:
                    self.required_if_not_none(
                        field=f"{utest_id}{self.value_field_suffix or ''}",
                        field_required=f"{utest_id}_reportable",
                        field_required_evaluate_as_int=True,
                    )
                self.evaluate_value(f"{utest_id}_value")
            self.validate_reportable_fields(
                reference_range_collection_name=(
                    requisition.panel_object.reference_range_collection_name
                ),
                **self.reportables_evaluator_options,
            )

    @property
    def fields_names_with_values(self):
        """Returns a list result `value` fields that are not None"""
        fields_names_with_values = []
        field_names = [f"{utest_id}{self.value_field_suffix}" for utest_id in self.utest_ids]
        for field_name in field_names:
            if self.cleaned_data.get(field_name):
                fields_names_with_values.append(field_name)
        return field_names

    @property
    def utest_ids(self):
        utest_ids = []
        for panel in self.panel_list:
            for utest_id in panel.utest_ids:
                try:
                    utest_id, _ = utest_id
                except ValueError:
                    pass
                utest_ids.append(utest_id)
        return utest_ids

    @property
    def panel_list(self):
        if self.panel:
            return [self.panel]
        return self.panels
