# Initial Config
import requests
import pandas as pd


class Adverity:
    """
    Class contains functions to retrieve data, create and edit stacks, manage connections & datastreams
    as well as triggering fetches using the Adverity Management API. More information on this can be
    found here: https://help.adverity.com/hc/en-us/articles/360009414019-Adverity-Management-API-Basics-Introduction

    """

    def __init__(self, stack: str, username: str, password: str):
        """
        API calls require the stack name, username and password to create a token.
        Once this has been created, we can make API calls accordingly.

        Parameters
        ----------
        stack: str, the workstack in question, eg, 'omd-emea'.
        username: str, the username.
        password: str, the password.

        """
        self.stack = stack
        self.username = username
        self.password = password

    def create_validation_params(self) -> dict:
        """
        Creates a validation dict with the username and password supplied.

        Returns
        -------
        A dictionary like so {'username': 'your_username', 'password': 'your_password'}.

        """
        return {"username": self.username, "password": self.password}

    def create_base_url(self) -> str:
        """
        Creates a base url using the stack param defined in the initialisation.

        """
        return f"https://{self.stack}.datatap.adverity.com/"

    def validate_login(self) -> dict:
        """
        Validates the url using the username and password param.

        Returns
        -------
        A dictionary indicating whether validation has been successful.

        """
        validation_url = "validate_login"
        base_url = Adverity.create_base_url(self=self)

        validation_params = Adverity.create_validation_params(self=self)
        validation = requests.post(base_url + validation_url, json=validation_params)

        return validation.json()

    def initiate_access_token(self) -> str:
        """
        Takes the validation from the validate_login func and returns an access token.

        Returns
        -------
        A dictionary with the access_token if authentication is successful.

        """
        validation_params = Adverity.create_validation_params(self=self)
        access_token_url = "api/auth/token/"

        base_url = Adverity.create_base_url(self=self)
        access_token = requests.post(
            base_url + access_token_url, json=validation_params
        )

        return access_token.json()["token"]

    @staticmethod
    def create_headers(ACCESS_TOKEN: str) -> dict:
        """
        Creates a dict using the ACCESS_TOKEN to pass onto GET requests.

        Parameters
        ----------
        ACCESS_TOKEN: str input

        Returns
        -------
        A dictionary like this: {'Authorization': 'Token ACCESS_TOKEN'}

        """
        return {"Authorization": f"Token {ACCESS_TOKEN}"}

    def list_workspaces(self, workspaces_url, ACCESS_TOKEN: str) -> dict:
        """
        Lists the workspaces based on a stack as a dictionary.

        Parameters
        ----------
        workspaces_url: str, the url of the workspaces info to be accessed.
        ACCESS_TOKEN: str input

        Returns
        -------
        A dict with te workspace names and their respective urls.

        """
        headers = Adverity.create_headers(self=self, ACCESS_TOKEN=ACCESS_TOKEN)
        base_url = Adverity.create_base_url(self=self)

        workstreams = requests.get(url=base_url + workspaces_url, headers=headers)
        workstreams_dict = workstreams.json()

        names = []
        urls = []

        for i in range(0, len(workstreams_dict["results"])):
            _dict = workstreams_dict["results"][i]

            names.append(_dict["name"])
            urls.append(_dict["url"])

        return dict(zip(names, urls))

    def get_information_dict(self, url: str, ACCESS_TOKEN: str) -> dict:
        """
        Retrieves a dictionary of information from the url param specified.
        Parameters
        ----------
        url: str, the url to be accessed.
        ACCESS_TOKEN: str input.

        Returns
        -------

        """
        headers = Adverity.create_headers(self=self, ACCESS_TOKEN=ACCESS_TOKEN)
        base_url = Adverity.create_base_url(self=self)

        response = requests.get(url=base_url + url, headers=headers)

        return response.json()

    @staticmethod
    def get_information_df(information_dict: dict) -> pd.DataFrame:
        """
        Makes a dataframe of the information_dict retrieved using the
        get_information_dict func.

        Parameters
        ----------
        information_dict: dict, the dict generated from the func get_information_dict.

        Returns
        -------
        A pandas dataframe based on the information_dict provided.

        """
        if information_dict == {"detail": "Invalid page."}:
            return pd.DataFrame()
        else:
            df_list = []

            for i in range(0, len(information_dict["results"])):
                _dict = information_dict["results"][i]
                df = pd.DataFrame.from_dict(_dict, orient="index").T
                df_list.append(df)

            return pd.concat(df_list, axis=0)

    def get_all_information_df(self, ACCESS_TOKEN: str, url: str) -> pd.DataFrame:
        """
        Gets all the information for all pages based on the url param.

        Parameters
        ----------
        ACCESS_TOKEN: str input.
        url: str, the url to be accessed

        Returns
        -------

        """
        # Set the page number
        page_num = 1
        df_list = []

        while True:
            print(f"Getting data for page number: {page_num}")
            # Increment the page number by 1 to get data from all pages
            page_num += 1

            page_url = url + f"?page={page_num}"
            information_dict = Adverity.get_information_dict(
                self=self, url=page_url, ACCESS_TOKEN=ACCESS_TOKEN
            )

            df = Adverity.get_information_df(
                self=self, information_dict=information_dict
            )

            # If the dataframe is empty, because there is no data for that page number
            if df.empty:
                # Break the function
                break
            else:
                # If the dataframe is not empty, append it to the df_list param
                df_list.append(df)

        return pd.concat(df_list, axis=0)

    def get_datastream_dict(self, datastreams_url: str, ACCESS_TOKEN: str) -> dict:
        """
        Creates a dictionary of datastreams based on the access_token param and workstack.

        Parameters
        ----------
        datastreams_url: str, the url of the datastreams to be accessed.
        ACCESS_TOKEN: str input.

        Returns
        -------
        A dictionary of datastreams with the relevant data and metadata.

        """
        return Adverity.get_information_dict(
            self=self, url=datastreams_url, ACCESS_TOKEN=ACCESS_TOKEN
        )

    def make_datastreams_df(self, datastreams_dict: dict) -> pd.DataFrame:
        """
        Makes a dataframe from the datastreams_dict param created from the func
        get_datastream_dict.

        Parameters
        ----------
        datastreams_dict: dict, the dictionary of datastreams data.

        Returns
        -------
        A pandas dataframe with datastreams dictionary.

        """
        return Adverity.get_information_df(self=self, information_dict=datastreams_dict)

    def get_all_datastreams_df(self, ACCESS_TOKEN: str) -> pd.DataFrame:
        """
        Gets all of the datastreams data based on all pages returned.

        Parameters
        ----------
        ACCESS_TOKEN: str input

        Returns
        -------
        A pandas dataframe with all datastreams data for each page.

        """
        datastreams_url = "api/datastream-types/"
        return Adverity.get_all_information_df(
            self=self, ACCESS_TOKEN=ACCESS_TOKEN, url=datastreams_url
        )

    def get_datastream_types(self, datatypes_url: str, ACCESS_TOKEN: str) -> dict:
        return Adverity.get_information_dict(
            self=self, url=datatypes_url, ACCESS_TOKEN=ACCESS_TOKEN
        )

    def make_datatypes_df(self, datatypes_dict: dict) -> pd.DataFrame:
        """
        Makes a dataframe from the datastreams_dict param created from the func
        get_datastream_dict.

        Parameters
        ----------
        datastreams_dict: dict, the dictionary of datastreams data.

        Returns
        -------
        A pandas dataframe with datastreams dictionary.

        """
        return Adverity.get_information_df(self=self, information_dict=datatypes_dict)

    def get_connections_dict(self, connections_url: str, ACCESS_TOKEN: str) -> dict:
        """
        Retrieves a dictionary of connections in a workstack.

        Parameters
        ----------
        connections_url: str, the url of the connections to be accessed.
        ACCESS_TOKEN: str input.

        Returns
        -------
        A dictionary with connections based on the workstack and all their
        relevant information.

        """
        return Adverity.get_information_dict(
            self=self, url=connections_url, ACCESS_TOKEN=ACCESS_TOKEN
        )

    def make_connections_df(self, connections_dict: dict) -> pd.DataFrame:
        """
        Makes a dataframe from the connections_dict param created from the func
        get_connections_dict.

        Parameters
        ----------
        connections_dict: dict, the dictionary of connections data.

        Returns
        -------
        A pandas dataframe with connections dictionary.

        """
        return Adverity.get_information_df(self=self, information_dict=connections_dict)

    def get_all_connections_df(self, ACCESS_TOKEN: str) -> pd.DataFrame:
        """
        Gets all of the datastreams data based on all pages returned.

        Parameters
        ----------
        ACCESS_TOKEN: str input

        Returns
        -------
        A pandas dataframe with all datastreams data for each page.

        """
        connections_url = "api/connection-types/"
        return Adverity.get_all_information_df(
            self=self, ACCESS_TOKEN=ACCESS_TOKEN, url=connections_url
        )
