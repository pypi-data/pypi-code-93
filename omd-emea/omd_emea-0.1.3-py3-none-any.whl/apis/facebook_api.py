# Initial Config
import pandas as pd
import requests
import itertools
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adaccountuser import AdAccountUser
from facebook_business.adobjects.adreportrun import AdReportRun
import time


class FacebookData:
    """
    Class contains functions to retrieving data via the Facebook Graph API.
    More information can be found here: https://developers.facebook.com/docs/graph-api/explorer

    """

    def __init__(self, app_id: str, app_secret: str, access_token: str):
        """
        All API calls using the Facebook Graph API requires the app_id, app_secret and the
        access token.

        Note that before API calls can be made, you have to create an app first.
        More information on this can be found here: https://developers.facebook.com/docs/development/.

        Parameters
        ----------
        app_id: str, the id of your app.
        app_secret: str, the secret of your app.
        access_token: str, the access token created of your app.

        """
        self.app_id = app_id
        self.app_secret = app_secret
        self.access_token = access_token

    def get_long_lived_access_token(self) -> str:
        """
        Access tokens generated from the Facebook Graph API are, by nature, short lived (one hour). This function uses
        a GET request to make them long lived (60 days).

        Returns
        -------
        A string with the long lived access_token.

        """
        # Construct the url
        short_lived_user_access_token = self.access_token
        long_lived_user_access_token_url = f"https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id={self.app_id}&client_secret={self.app_secret}&fb_exchange_token={short_lived_user_access_token}"

        # Initiate the GET request
        res = requests.get(url=long_lived_user_access_token_url)

        # Construct a dictionary
        res_dict = res.json()

        return res_dict["access_token"]

    def initialisation(self, access_token: str):
        """
        Performs the initialisation using the necessary components from the the __init__.

        Parameters
        ----------
        access_token: str, the access token created of your app.

        Returns
        -------
        A completed initialisation based on the necessary components.

        """
        return FacebookAdsApi.init(self.app_id, self.app_secret, access_token)

    @staticmethod
    def get_all_account_ids() -> list:
        """
        Retrieves a list of account ids. Note that prior access to the user has to be
        given first.

        Returns
        -------
        A list of account ids.

        """
        me = AdAccountUser(fbid="me")

        my_accounts = list(me.get_ad_accounts())

        account_ids = []
        for account in my_accounts:
            _id = account["account_id"]
            account_ids.append(_id)

        return account_ids

    @staticmethod
    def initialise_facebook_account(account_id: str):
        """
        Performs the account initialisation based on the account_id param.

        Parameters
        ----------
        account_id: str, the account id.

        Returns
        -------
        A completed initialisation based on the account_id.

        """
        return AdAccount(f"act_{account_id}")

    @staticmethod
    def get_campaigns(account) -> list:
        """
        Gets a list of campaigns and their respective ids based on the account initialisation
        performed using the initialise_facebook_account func.

        Parameters
        ----------
        account: the account initialisation to be performed.

        Returns
        -------
        A list of campaigns and their ids.

        """
        return account.get_campaigns()

    def get_campaign_ids(self, account, access_token: str) -> list:
        """
        Returns a list of campaign ids.

        Parameters
        ----------
        account: the account initialisation to be performed.
        access_token: str, the access token created of your app.

        Returns
        -------
        A list of unique campaign ids.

        """
        campaigns = FacebookData(
            self.app_id, self.app_secret, access_token
        ).get_campaigns(account=account)

        campaign_ids = []
        for campaign in campaigns:
            _id = campaign["id"]
            campaign_ids.append(_id)

        return campaign_ids

    @staticmethod
    def initialise_job(
        campaign,
        params: dict,
        _async=bool,
    ) -> list:
        """
        Performs the API call with either synchronous or asynchronous calls.

        Parameters
        ----------
        campaign: the campaign initialised with the campaign id.
        params: dict, a dictionary of parameters for the API call.
        _async: bool, to determine whether the job should be asynchronous or not.

        Returns
        -------
        A list of results to be transformed into a dataframe.

        """
        # Get the response
        if _async:
            # Get the response
            async_response = campaign.get_insights_async(params=params)
            async_response.api_get()

            while async_response[AdReportRun.Field.async_percent_completion] < 100:
                time.sleep(1)
                async_response.api_get()

            time.sleep(1)
            return async_response.get_result(params={"limit": 1000})

        else:
            # Get the response
            return campaign.get_insights(params=params)

    @staticmethod
    def get_campaign_data(
        campaign_id: str,
        fields: list,
        date_preset: str,
        _async: bool,
        breakdowns: str = None,
        time_increment: int = None,
    ) -> pd.DataFrame:
        """
        Retrieves the data using the Facebook Graph API based on the campaign_id.

        Parameters
        ----------
        campaign_id: str, the id of the campaign.
        fields: list, the list of fields to retrieve data for, eg ['account_id', 'campaign_id', 'impressions', 'spend'].
        date_preset: str, the time range of the data to receive, eg: 'yesterday'.
        _async: bool, to determine whether the job should be asynchronous or not.
        breakdowns: str, any breakdowns of the data that can be specified, eg 'dma'.
        time_increment: int, the time increments to be specified to breakdown data, eg 1.

        For a full range of allowed params for fields, date_preset, breakdowns & time_increment, please consult
        this page: https://developers.facebook.com/docs/marketing-api/insights/parameters/v11.0.

        Returns
        -------
        A dataframe with the relevant data based on the campaign_id.

        """
        # Initialise the campaign
        campaign = Campaign(campaign_id)

        # Set the params dict
        params = {
            "date_preset": date_preset,
            "fields": fields,
            "breakdowns": breakdowns,
            "time_increment": time_increment,
        }

        # Get the response
        response = FacebookData.initialise_job(
            campaign=campaign, params=params, _async=_async
        )

        # Evaluate if the response object is empty
        if len(response) == 0:
            return None
        else:
            df_list = []
            for i in response:
                df = pd.DataFrame.from_dict(i, orient="index")
                df_list.append(df)

            return pd.concat(df_list, axis=1)

    def get_all_campaigns_data(
        self,
        account,
        access_token: str,
        fields: list,
        date_preset: str,
        _async: bool,
        breakdowns: str = None,
        time_increment: int = None,
    ) -> pd.DataFrame:
        """
        Retrieves all campaign data (based on their ids) for a given account.

        Parameters
        ----------
        account: the account initialisation to be performed.
        access_token: str, the access token created of your app.
        fields: list, the list of fields to retrieve data for, eg ['account_id', 'campaign_id', 'impressions', 'spend'].
        date_preset: str, the time range of the data to receive, eg: 'yesterday'.
        _async: bool, to determine whether the job should be asynchronous or not.
        breakdowns: str, any breakdowns of the data that can be specified, eg 'dma'.
        time_increment: int, the time increments to be specified to breakdown data, eg 1.

        Returns
        -------
        A pandas dataframe with all campaign data.

        """
        # Get all the campaign_ids
        campaign_ids = FacebookData(
            self.app_id, self.app_secret, access_token
        ).get_campaign_ids(account, access_token)

        # Make a list of dataframes
        df_list = []
        for campaign_id in campaign_ids:
            print(f"Getting data for campaign id: {campaign_id}")
            data = FacebookData(
                self.app_id, self.app_secret, access_token
            ).get_campaign_data(
                campaign_id=campaign_id,
                fields=fields,
                date_preset=date_preset,
                _async=_async,
                breakdowns=breakdowns,
                time_increment=time_increment,
            )

            df_list.append(data)

        # Return a pandas dataframe
        try:
            return pd.concat(df_list, axis=1).T
        except Exception as e:
            print(e)
            return pd.DataFrame(columns=fields)

    def get_all_accounts_data(
        self,
        access_token: str,
        fields: list,
        date_preset: str,
        _async: bool,
        breakdowns: str = None,
        time_increment: int = None,
    ) -> list:
        """
        Retrieves all data for all Facebook accounts, note that prior access has to be granted
        to the user.

        Parameters
        ----------
        access_token: str, the access token created of your app.
        fields: list, the list of fields to retrieve data for, eg ['account_id', 'campaign_id', 'impressions', 'spend'].
        date_preset: str, the time range of the data to receive, eg: 'yesterday'.
        _async: bool, to determine whether the job should be asynchronous or not.
        breakdowns: str, any breakdowns of the data that can be specified, eg 'dma'.
        time_increment: int, the time increments to be specified to breakdown data, eg 1.

        Returns
        -------
        A pandas dataframe with all accounts data.

        """

        # Retrieve all account ids
        account_ids = FacebookData(
            self.app_id, self.app_secret, access_token
        ).get_all_account_ids()

        all_account_data = []
        for account_id in account_ids:
            # Initialise the account
            print(" ")
            print(f"Initialising account: {account_id}")
            my_account = FacebookData(
                self.app_id, self.app_secret, access_token
            ).initialise_facebook_account(account_id=account_id)

            # Get all campaign data
            account_data = FacebookData(
                self.app_id, self.app_secret, access_token
            ).get_all_campaigns_data(
                account=my_account,
                access_token=access_token,
                fields=fields,
                date_preset=date_preset,
                _async=_async,
                breakdowns=breakdowns,
                time_increment=time_increment,
            )

            # Append to the all_account_data
            all_account_data.append(account_data)

        return all_account_data

    @staticmethod
    def get_all_accounts_data_columns(all_accounts_data: list) -> list:
        """
        Makes a nested list of all columns for each dataframe stored in the all_accounts_data
        list, created using the func get_all_accounts_data.

        Parameters
        ----------
        all_accounts_data: list, a list of all accounts dataframe.

        Returns
        -------
        A nested list with all columns for every dataframe contained in all_accounts_data.

        """
        all_cols = []
        for idx, val in enumerate(all_accounts_data):
            cols = all_accounts_data[idx].columns.tolist()
            all_cols.append(cols)

        return all_cols

    @staticmethod
    def get_common_cols(all_cols: list) -> list:
        """
        Retrieves all common columns in the all_cols param list provided.

        Parameters
        ----------
        all_cols: list, a nested list of all columns, generated using the get_all_accounts_data_columns
        func.

        Returns
        -------
        A list of all common columns in the nested all_cols param.

        """
        return list(
            set.intersection(set(all_cols[0]), *itertools.islice(all_cols, 1, None))
        )

    @staticmethod
    def get_all_accounts_data_dataframe(
        all_accounts_data: list, common_cols: list
    ) -> pd.DataFrame:
        """
        Makes a final dataframe of campaign data for all accounts (based on the relevant authorisations).

        Parameters
        ----------
        all_accounts_data: list, a list of all accounts data, created using the get_all_accounts_data func.
        common_cols: list, a list of all column columns in the list param all_accounts_data, generated
        using the func get_common_cols.

        Returns
        -------
        A pandas dataframe with all campaign data for all accounts.

        """
        new_df_list = []
        for idx, val in enumerate(all_accounts_data):
            new_df = all_accounts_data[idx][common_cols]
            new_df_list.append(new_df)

        return pd.concat(new_df_list, axis=0)


def main(
    app_id: str,
    app_secret: str,
    access_token: str,
    fields: list,
    _async: bool,
    date_preset: str = None,
    time_increment: int = None,
) -> pd.DataFrame:
    """
    The main method to get all campaign data for each account.

    Parameters
    ----------
    app_id: str, the app id.
    app_secret: str, the app secret.
    access_token: str, the access token.
    fields: list, the column list to be passed off.
    _async: bool, to determine whether the job should be asynchronous or not.
    date_preset: str, the date preset needed, eg 'maximum', or 'last_7d. For a full list
    of parameters, please see here: https://developers.facebook.com/docs/marketing-api/insights/parameters/v11.0.
    time_increment: int, the time_increment to be passed off.

    Returns
    -------

    """
    # Initialisation
    FacebookData(app_id, app_secret, access_token).initialisation(
        access_token=access_token
    )

    # Get a list of all accounts data
    all_accounts_data = FacebookData(
        app_id, app_secret, access_token
    ).get_all_accounts_data(
        access_token=access_token,
        fields=fields,
        _async=_async,
        date_preset=date_preset,
        time_increment=time_increment,
    )

    # Get all the columns in the all_accounts_data list param
    all_cols = FacebookData(
        app_id, app_secret, access_token
    ).get_all_accounts_data_columns(all_accounts_data=all_accounts_data)

    # Obtain the common columns
    common_cols = FacebookData(app_id, app_secret, access_token).get_common_cols(
        all_cols=all_cols
    )

    # Create the final dataframe
    return FacebookData(
        app_id, app_secret, access_token
    ).get_all_accounts_data_dataframe(
        all_accounts_data=all_accounts_data, common_cols=common_cols
    )
