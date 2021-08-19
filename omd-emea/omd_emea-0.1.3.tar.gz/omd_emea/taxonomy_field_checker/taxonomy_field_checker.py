# Initial Config
import os
import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By


# Classes
class Login:
    """
    Class contains the functions to open the Taxonomy Builder webpage and login.

    """

    def __init__(self, user_name: str, pwd: str):
        """
        In order to login to Taxonomy Builder, we need the relevant username and password.

        Parameters
        ----------
        user_name: str, the username.
        pwd: str, the password.

        """
        self.user_name = user_name
        self.pwd = pwd

    @staticmethod
    def open_webpage(url: str):
        """
        Opens the url passed off.

        Parameters
        ----------
        url: str, the url to be opened by Selenium.

        Returns
        -------
        A Chrome browser opened with the url and the selenium driver.

        """
        # Initiate the Chrome driver
        driver = webdriver.Chrome("/usr/local/bin/chromedriver")

        # Initiate the url to be accessed
        driver.get(url)

        return driver

    def login(self, driver, submit_xpath: str):
        """
        Logs on to the page based on the username and password from the init, the selenium driver
        and the submit_xpath param.

        Parameters
        ----------
        driver: the selenium driver.
        submit_xpath: str, the xpath of the submit button

        Returns
        -------
        The login initiated on the page.

        """
        # Set the username in the UserName field
        username = driver.find_element_by_name("UserName")
        username.clear()
        username.send_keys(self.user_name)

        # Set the password in the Password field
        password = driver.find_element_by_name("Password")
        password.clear()
        password.send_keys(self.pwd)

        # Find the submit button and click it
        driver.find_element_by_xpath(submit_xpath).click()


class SelectClient:
    """
    Class selects the Taxonomy Builder client once the login stage has been completed.

    """

    def __init__(self):
        pass

    @staticmethod
    def click_on_client_name(driver, client_name: str, wait_time: int):
        """
        Clicks on the Taxonomy Builder client based on the client_name param.

        Parameters
        ----------
        driver: the selenium driver.
        client_name: str, the name of the client.
        wait_time: int, the time to be waited so that the page loads.

        Returns
        -------
        The webpage being clicked based on the client name.

        """
        # Wait 10 seconds until the page loads
        buddy = WebDriverWait(driver, wait_time).until(
            EC.visibility_of_element_located((By.LINK_TEXT, client_name))
        )

        # Find the client name element and click it
        client = driver.find_element_by_link_text(client_name)

        client.click()


class TaxonomySections:
    """
    Class identifies the overall sections in the Taxonomy Builder based on the
    client name.

    """

    def __init__(self):
        pass

    @staticmethod
    def identify_taxonomy_sections(driver, panel_group_class_name: str) -> list:
        """
        Makes a list of overall taxonomy sections identified.

        Parameters
        ----------
        driver: the selenium driver.
        panel_group_class_name: str, the class name of the panel group, eg 'panel-group'.

        Returns
        -------
        A list of overall taxonomy sections.

        """
        return driver.find_element_by_class_name(panel_group_class_name).text.split(
            "\n"
        )

    @staticmethod
    def make_list_dict(_list: list) -> dict:
        """
        Makes a dictionary from the _list param where the keys are the index of the list and the
        values are the _list values.

        Parameters
        ----------
        _list: list, the list param input.

        Returns
        -------
        A dictionary of the the _list indices and their respective values.

        """
        return {v + 1: k for v, k in enumerate(_list)}


class TaxonomyFields:
    """
    Class identifies the taxonomy fields in each individual section.

    """

    def __init__(self):
        pass

    @staticmethod
    def click_on_taxonomy_section(driver, div_num: int):
        """
        Clicks on the individual taxonomy sections.

        Parameters
        ----------
        driver: the selenium driver.
        div_num: int, the section number.

        Returns
        -------
        The individual section based on the selenium driver being clicked.

        """
        xpath = f'//*[@id="taxonomyPanelHolder"]/div[{div_num}]/div[1]/h2/a'

        driver.find_element_by_xpath(xpath).click()

    @staticmethod
    def identify_field_names(driver) -> list:
        """
        Identifies the field names within each taxonomy section.

        Parameters
        ----------
        driver: the selenium driver.

        Returns
        -------
        A list of field names within each individual taxonomy section.

        """
        fields = driver.find_elements_by_class_name("fieldName")
        field_names = []

        for field in fields:
            field_name = field.text
            field_names.append(field_name)

        return list(filter(None, field_names))

    @staticmethod
    def identify_taxonomy_code(driver, div_num: int) -> str:
        """
        Identifies the taxonomy code of the relevant section.

        Parameters
        ----------
        driver: the selenium driver.
        div_num: int, the section number.

        Returns
        -------
        A string with the taxonomy code.

        """
        xpath = f'//*[@id="taxonomyPanelHolder"]/div[{div_num}]'
        return "Taxonomy" + driver.find_element_by_xpath(xpath).get_attribute(
            "data-taxonomyid"
        )


class TaxonomySubFields:
    """
    Class identifies the sub fields within each taxonomy field and section.

    """

    def __init__(self):
        pass

    @staticmethod
    def click_on_subtaxonomy_field(driver, taxonomy_code: str, sub_field_num: int):
        """
        Clicks on the individual sub taxonomy field.

        Parameters
        ----------
        driver: the selenium driver.
        taxonomy_code: str, the taxonomy code, eg 'Taxonomy2961'.
        sub_field_num: int, the sub field number, eg 1.

        Returns
        -------
        The individual sub-section based on the selenium driver being clicked.

        """
        try:
            # Click on sub field
            sub_fields_xpath = (
                f'//*[@id=" {taxonomy_code}Fields"]/li[{sub_field_num}]/div/div/a/div/b'
            )
            driver.find_element_by_xpath(sub_fields_xpath).click()
        except:
            pass

    @staticmethod
    def obtain_taxonomy_fields(driver, taxonomy_code: str, sub_field_num: int) -> list:
        """
        Obtains the sub taxonomy fields. Retrieves all sub fields within a section automatically.

        Parameters
        ----------
        driver: the selenium driver.
        taxonomy_code: str, the taxonomy code, eg 'Taxonomy2961'.
        sub_field_num: int, the sub field number, eg 1.

        Returns
        -------
        A list of sub taxonomy fields.

        """
        # Set the value number
        values = []
        value_num = 1

        while True:
            # Gets all fields by incrementally adding to the value_num param
            value_num += 1
            value_xpath = f'//*[@id=" {taxonomy_code}Fields"]/li[{sub_field_num}]/div/div/div/ul/li[{value_num}]'

            # Obtain the value from the xpath
            try:
                value = driver.find_element_by_xpath(value_xpath).text
            # If there is an error, return an empty string
            except:
                value = ""

            # If the length of the value string is 0, break the function
            if len(value) == 0:
                break
            else:
                # if the length of value is non zero, append it to the values list
                values.append(value)

        return values

    @staticmethod
    def make_taxonomy_subfields_dataframe(
        driver,
        taxonomy_code: str,
        sub_field_num: int,
        field_names_dict: dict,
        taxonomy_section_num: int,
        taxonomy_sections_dict: dict,
    ) -> pd.DataFrame:
        """
        Makes a dataframe of the taxonomy subfields based on a field.

        Parameters
        ----------
        driver: the selenium driver.
        taxonomy_code: str, the taxonomy code, eg 'Taxonomy2961'.
        sub_field_num: int, the sub field number, eg 1.
        field_names_dict: dict, the dictionary of the field names and their indices.
        taxonomy_section_num: int, the number of overall taxonomy section to be accessed.
        taxonomy_sections_dict: dict, the dictionary of the overall taxonomy sections and their indices.

        Returns
        -------
        A dataframe of the taxonomy fields for each field.

        """

        # Obtain the taxonomy section name
        taxonomy_section_name = taxonomy_sections_dict.get(taxonomy_section_num)

        # Obtain the field name from the subfield number
        field_name = field_names_dict.get(sub_field_num)

        # Obtain the sub taxonomy fields
        sub_taxonomy_fields = TaxonomySubFields().obtain_taxonomy_fields(
            driver=driver, taxonomy_code=taxonomy_code, sub_field_num=sub_field_num
        )

        # Construct the dataframe
        columns = ["Taxonomy_Section", "Taxonomy_Field", "Taxonomy_Field_values"]
        df = pd.DataFrame(columns=columns)

        # Populate the columns
        df["Taxonomy_Field_values"] = sub_taxonomy_fields
        df["Taxonomy_Field"] = field_name
        df["Taxonomy_Section"] = taxonomy_section_name

        return df

    @staticmethod
    def obtain_taxonomy_fields_dataframe(
        driver,
        taxonomy_code: str,
        taxonomy_section_num: int,
        taxonomy_sections_dict: dict,
        field_names_dict: dict,
    ) -> pd.DataFrame:
        """
        Makes a dataframe for all taxonomy sub fields per field.

        Parameters
        ----------
        driver: the selenium driver.
        taxonomy_code: str, the taxonomy code, eg 'Taxonomy2961'.
        taxonomy_section_num: int, the number of overall taxonomy section to be accessed.
        taxonomy_sections_dict: dict, the dictionary of the overall taxonomy sections and their indices.
        field_names_dict: dict, the dictionary of the field names and their indices.

        Returns
        -------
        A dataframe of all taxonomy sub fields for each field.

        """
        df_list = []

        for sub_field_num in list(field_names_dict.keys()):
            # Obtain the sub field name
            sub_field_name = field_names_dict.get(sub_field_num)
            print(f"Obtaining data for {sub_field_name}")

            TaxonomySubFields().click_on_subtaxonomy_field(
                driver=driver, taxonomy_code=taxonomy_code, sub_field_num=sub_field_num
            )

            time.sleep(1)

            df = TaxonomySubFields().make_taxonomy_subfields_dataframe(
                driver=driver,
                taxonomy_code=taxonomy_code,
                sub_field_num=sub_field_num,
                field_names_dict=field_names_dict,
                taxonomy_section_num=taxonomy_section_num,
                taxonomy_sections_dict=taxonomy_sections_dict,
            )
            df_list.append(df)

            TaxonomySubFields().click_on_subtaxonomy_field(
                driver=driver, taxonomy_code=taxonomy_code, sub_field_num=sub_field_num
            )

        return pd.concat(df_list, axis=0)

    @staticmethod
    def obtain_all_taxonomy_fields_dataframe(
        driver, taxonomy_sections_dict: dict
    ) -> pd.DataFrame:
        """
        Obtains a dataframe for all taxonomy sub fields for each field and each section.

        Parameters
        ----------
        driver: the selenium driver.
        taxonomy_sections_dict: dict, the dictionary of the overall taxonomy sections and their indices.

        Returns
        -------
        A dataframe with all subfields, fields and taxonomy sections mapped.

        """
        df_list = []

        for taxonomy_section_num in list(taxonomy_sections_dict.keys()):
            # Obtain taxonomy section name
            taxonomy_section_name = taxonomy_sections_dict.get(taxonomy_section_num)
            print(" ")
            print(f"Getting data for {taxonomy_section_name}")

            # Click on the taxonomy section
            TaxonomyFields().click_on_taxonomy_section(
                driver=driver, div_num=taxonomy_section_num
            )
            time.sleep(1)

            # Obtain a dictionary of fields
            field_names_dict = TaxonomySections().make_list_dict(
                TaxonomyFields().identify_field_names(driver=driver)
            )

            # Obtain the taxonomy code
            taxonomy_code = TaxonomyFields().identify_taxonomy_code(
                driver=driver, div_num=taxonomy_section_num
            )

            # Make a dataframe for each section
            df = TaxonomySubFields().obtain_taxonomy_fields_dataframe(
                driver=driver,
                taxonomy_code=taxonomy_code,
                taxonomy_section_num=taxonomy_section_num,
                taxonomy_sections_dict=taxonomy_sections_dict,
                field_names_dict=field_names_dict,
            )

            # Append to the list
            df_list.append(df)

        return pd.concat(df_list, axis=0)


def main(client_name: str, user_name: str, pwd: str):
    """
    The main process being executed.

    Parameters
    ----------
    client_name: str, the name of the client.
    user_name: str, the username, eg 'aniruddha.sengupta@omd.com'.
    pwd: str, the password.

    Returns
    -------
    The taxonomy field checker being initiated and recording the available sub fields for a given
    client.

    """
    # Open up the webpage and initiate the driver
    print("Opening up the webpage and initiating the driver")
    driver = Login(user_name=user_name, pwd=pwd).open_webpage(
        url="https://taxonomybuilder.oneomg.com/"
    )

    # Login to the webpage
    print("Logging into the webpage")
    Login(user_name=user_name, pwd=pwd).login(
        driver=driver, submit_xpath='//*[@id="submitButton"]'
    )

    # Click on the client name
    print(f"Clicking on the client name: {client_name}")
    SelectClient.click_on_client_name(
        driver=driver, client_name=client_name, wait_time=5
    )

    # Identify the overall taxonomy sections
    print("Identifying the overall taxonomies section")
    taxonomy_sections = TaxonomySections.identify_taxonomy_sections(
        driver=driver, panel_group_class_name="panel-group"
    )

    # Make a dictionary from the overall taxonomy sections
    print("Making a dictionary of the overall taxonomy sections")
    taxonomy_sections_dict = TaxonomySections.make_list_dict(_list=taxonomy_sections)

    # Obtain an overall dataframe for all available fields for each taxonomy section & sub section based on the
    # client name
    print(
        f"Obtaining a dataframe for every taxonomy section for the client: {client_name}"
    )
    df = TaxonomySubFields.obtain_all_taxonomy_fields_dataframe(
        driver=driver, taxonomy_sections_dict=taxonomy_sections_dict
    )

    return df
