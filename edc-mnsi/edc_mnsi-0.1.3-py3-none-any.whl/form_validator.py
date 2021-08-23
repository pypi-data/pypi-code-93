from edc_constants.constants import NO, NOT_EXAMINED, OTHER, YES
from edc_form_validators import FormValidator

from .fieldsets import patient_history_fields


class MnsiFormValidator(FormValidator):
    def clean(self):
        self.required_if(
            NO,
            field="mnsi_performed",
            field_required="mnsi_not_performed_reason",
        )
        self.clean_patient_history_fields()
        self.clean_physical_assessments()

    def clean_patient_history_fields(self):
        for field in patient_history_fields:
            self.applicable_if(
                YES,
                field="mnsi_performed",
                field_applicable=field,
            )

    def clean_physical_assessments(self):
        applicable_if_opts = dict(
            not_applicable_value=NOT_EXAMINED,
            applicable_msg="Invalid. Foot was examined",
            not_applicable_msg="Invalid. Foot was not examined",
        )
        for foot_choice in ["right", "left"]:

            self.applicable_if(
                YES,
                field="mnsi_performed",
                field_applicable=f"examined_{foot_choice}_foot",
            )

            self.applicable_if(
                YES,
                field=f"examined_{foot_choice}_foot",
                field_applicable=f"normal_appearance_{foot_choice}_foot",
                **applicable_if_opts,
            )

            self.m2m_required_if(
                response=NO,
                field=f"normal_appearance_{foot_choice}_foot",
                m2m_field=f"abnormal_obs_{foot_choice}_foot",
            )

            self.m2m_other_specify(
                OTHER,
                m2m_field=f"abnormal_obs_{foot_choice}_foot",
                field_other=f"abnormal_obs_{foot_choice}_foot_other",
            )

            self.applicable_if(
                YES,
                field=f"examined_{foot_choice}_foot",
                field_applicable=f"ulceration_{foot_choice}_foot",
                **applicable_if_opts,
            )

            self.applicable_if(
                YES,
                field=f"examined_{foot_choice}_foot",
                field_applicable=f"ankle_reflexes_{foot_choice}_foot",
                **applicable_if_opts,
            )
            self.applicable_if(
                YES,
                field=f"examined_{foot_choice}_foot",
                field_applicable=f"vibration_perception_{foot_choice}_toe",
                **applicable_if_opts,
            )
            self.applicable_if(
                YES,
                field=f"examined_{foot_choice}_foot",
                field_applicable=f"monofilament_{foot_choice}_foot",
                **applicable_if_opts,
            )
