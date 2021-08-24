from ._config import TEST_DATA_FOLDER
from .base import BaseTest
from selenium.webdriver.common.by import By


class CramDeliveryRequest(BaseTest):
    def setup(self):
        self.log_in_and_visit_page('jira/wgs_delivery_request/')
        self._fill_in_form_with_default_values()

    def _fill_in_form_with_default_values(self):
        self.fill_in_form_field("workspace_name", "some_workspace")
        self.fill_in_form_field("cohort_name", "test_cohort_name")
        self.fill_in_form_field("project_name", "test_project_name")
        self.fill_in_form_field("internal_pi", "test_internal_pi")
        self.fill_in_form_field("discoverability", "test_internal_pi")
        self.fill_in_form_field("race_ethnicity", "Race")
        self.fill_in_form_field("age_specified", "23")
        self.fill_in_form_field("disease_description", "EPI")
        self.fill_in_form_field("primary_disease", "Cancer")
        self.select_radio_button("new_workspace", "no")
        self.select_radio_button("override_delivery", "yes")
        self.select_radio_button("data_type", "WGS")
        self.select_radio_button("deliver_metadata", "yes")
        self.select_radio_button("fee_for_service", "no")
        self.select_radio_button("clinical_data_delivery", "yes")
        self.select_radio_button("sample_threshold", "AUTOMATIC")
        self.select_radio_button("self_service_option", "manual_submission")
        self.select_radio_button("move_gvcfs", "no")
        self.upload_file_from_path('file_field',
                                   f'{TEST_DATA_FOLDER}/test_cram_v2_clinical_delivery_metadata.txt')

    def submit_test_form(self):
        self.setup()
        self.selenium.find_element(By.NAME, 'file_field').submit()
        self.assert_form_submitted_successfully()
        link = self.selenium.find_element(By.PARTIAL_LINK_TEXT, 'https://broadinstitute.atlassian.net/browse/POTE').text
        print(f"Issue has been created at {link}")
