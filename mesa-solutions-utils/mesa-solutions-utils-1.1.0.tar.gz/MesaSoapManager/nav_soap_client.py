from requests import Session, HTTPError
from requests.auth import HTTPBasicAuth
from zeep import Client
from zeep.transports import Transport
from zeep.cache import SqliteCache
from zeep.exceptions import Fault
from zeep.helpers import serialize_object


class NavSoapClient():

    def __init__(self, nav_user, nav_password, nav_soap_service, nav_company): 
        """
        Constructs an instance of a nav soap client

        param nav_user: The username of the nav user connecting to the SOAP service
        param nav_password: The password for the user
        param nav_soap_service: The base URL for the SOAP service
        param nav_company: The company contained in the NAV instance
        """
        self.nav_user = nav_user
        self.nav_password = nav_password
        self.nav_soap_service = nav_soap_service
        self.nav_company = nav_company


    def read_multiple_soap_records(self, soap_object, filter_data=[{'property': '', 'value': ''}], set_size=0):
        """
        Return SOAP records from NAV

        param soap_object: The soap service endpoint. For example Firm_Planned_Prod_Order
        param filter_data: An array of dictionaries, where the property key cooresponds to a SOAP element 
        and the value key cooresponds to the value of the property to filter on. You can filter by multiple properties
        param set_size: Specifies the number of items to return. A set_size of 0 will return all of the records
        """
        session = Session()
        session.auth = HTTPBasicAuth(self.nav_user, self.nav_password)

        soap_service_url = self.nav_soap_service + self.nav_company + "/Page/" + soap_object
        client = Client(soap_service_url, transport=Transport(
            session=session, cache=SqliteCache()))

        filter_field = client.get_type(f"ns0:{soap_object}_Fields")
        filter_type = client.get_type(f"ns0:{soap_object}_Filter")

        # Build the search filters from the filter_data
        # Notice the default values for the filter_data arguement are empty
        # so we bring back all of the records as a default
        filters = [filter_type(filter_field(item['property']), item['value'])
                for item in filter_data]

        # setService tells the service how many records to return
        soap_response = client.service.ReadMultiple(filter=filters, setSize=set_size)

        serialized_response = serialize_object(soap_response)
        return serialized_response


    def create_soap_record(self, soap_object, data):
        """
        Create a SOAP record in NAV

        param soap_object: The soap service endpoint. For example Firm_Planned_Prod_Order
        param data: A dictionary of key value pairs. The keys must match the actions SOAP elements
        """
        session = Session()
        session.auth = HTTPBasicAuth(self.nav_user, self.nav_password)

        soap_service_url = self.nav_soap_service + \
            self.nav_company + "/Page/" + soap_object
        client = Client(soap_service_url, transport=Transport(
            session=session, cache=SqliteCache()))

        complex_type = client.get_type(f"ns0:{soap_object}")
        record = complex_type(**data)

        soap_response = client.service.Create(record)

        serialized_response = serialize_object(soap_response)
        return serialized_response

    
    def create_soap_record_with_lines(self, soap_object, data, line_property, line_data):
        """
        Create a SOAP record in NAV with one or many lines

        param soap_object: The soap service endpoint. For example Firm_Planned_Prod_Order
        param data: A dictionary of key value pairs. The keys must match the actions SOAP elements
        param line_property: The name of the list of lines. For instance Firm_Planned_Prod_Order is ProdOrderLines
        param line_data: An array of dictionaries. The keys must match the lines SOAP elements
        """
        session = Session()
        session.auth = HTTPBasicAuth(self.nav_user, self.nav_password)

        soap_service_url = self.nav_soap_service + \
            self.nav_company + "/Page/" + soap_object
        client = Client(soap_service_url, transport=Transport(
            session=session, cache=SqliteCache()))

        complex_type = client.get_type(f"ns0:{soap_object}")
        line_list_type = client.get_type(f"ns0:{soap_object}_Lines_List")
        line_type = client.get_type(f"ns0:{soap_object}_Lines")

        lines = [line_type(**line) for line in line_data]
        data[line_property] = line_list_type(lines)

        record = complex_type(**data)

        soap_response = client.service.Create(record)

        serialized_response = serialize_object(soap_response)
        return serialized_response


    def update_soap_record(self, soap_object, data):
        """
        Update a SOAP record in NAV with one or many lines. The record's key must be
        in the data dictionary with the data you want to update. The key usually looks 
        something like this... 32;HRUAAACLAgAAAAJ7BjEAMAAxADEANwAw10;16521815631;14

        param soap_object: The soap service endpoint. For example Firm_Planned_Prod_Order
        param data: A dictionary of key value pairs. The keys must match the actions SOAP elements
        """
        session = Session()
        session.auth = HTTPBasicAuth(self.nav_user, self.nav_password)

        soap_service_url = self.nav_soap_service + \
            self.nav_company + '/Page/' + soap_object
        client = Client(soap_service_url, transport=Transport(
            session=session, cache=SqliteCache()))

        complex_type = client.get_type(f'ns0:{soap_object}')
        record = complex_type(**data)

        soap_response = client.service.Update(record)

        serialized_response = serialize_object(soap_response)
        return serialized_response


    def delete_soap_record(self, soap_object, record_key):
        """
        Delete a SOAP record in NAV by the records key. The key usually looks 
        something like this... 32;HRUAAACLAgAAAAJ7BjEAMAAxADEANwAw10;16521815631;14

        param soap_object: The soap service endpoint. For example Firm_Planned_Prod_Order
        param record_key: The key of the record you want to delete
        """
        session = Session()
        session.auth = HTTPBasicAuth(self.nav_user, self.nav_password)

        soap_service_url = self.nav_soap_service + \
            self.nav_company + "/Page/" + soap_object
        client = Client(soap_service_url, transport=Transport(
            session=session, cache=SqliteCache()))

        soap_response = client.service.Delete(record_key)

        serialized_response = serialize_object(soap_response)
        return serialized_response


    def refresh_prod_order(self, prod_order_status, prod_order_no):
        """
        Refreshes a firm planned production order in NAV using the order's
        production order status and production order number. The prod_order_status
        should always have a value of 2, which cooresponds to a status of firm 
        planned in NAV

        param prod_order_status: Should always have a value of 2 (firm planned)
        param prod_order_no: The order number of the record you want to refresh
        """
        session = Session()
        session.auth = HTTPBasicAuth(self.nav_user, self.nav_password)

        soap_service_url = self.nav_soap_service + \
            self.nav_company + "/Codeunit/MfgFunctionsWS"
        client = Client(soap_service_url, transport=Transport(
            session=session, cache=SqliteCache()))

        soap_response = client.service.RefreshProdOrder(
            prodOrderStatus=prod_order_status, prodOrderNo=prod_order_no)

        serialized_response = serialize_object(soap_response)
        return serialized_response


    def release_prod_order(self, prod_order_status, prod_order_no):
        """
        Releases a firm planned production order in NAV using the order's
        production order status and production order number. A released order
        cannot be undone. Only firm planned orders are released, so the 
        prod_order_status is always 2 (firm planned)

        param prod_order_status: Should always have a value of 2 (firm planned)
        param prod_order_no: The order number of the record you want to release
        """
        session = Session()
        session.auth = HTTPBasicAuth(self.nav_user, self.nav_password)

        soap_service_url = self.nav_soap_service + \
            self.nav_company + "/Codeunit/MfgFunctionsWS"
        client = Client(soap_service_url, transport=Transport(
            session=session, cache=SqliteCache()))

        soap_response = client.service.ReleaseProdOrder(
            prodOrderStatus=prod_order_status, prodOrderNo=prod_order_no)

        serialized_response = serialize_object(soap_response)
        return serialized_response


    def get_item_images(self, item_number):
        """
        Returns a base64 encoded string that represents the image for
        a given item_number

        param item_number: The item number pulled from the Integration_Item_Card service
        """
        session = Session()
        session.auth = HTTPBasicAuth(self.nav_user, self.nav_password)

        soap_service_url = self.nav_soap_service + \
            self.nav_company + "/Codeunit/MfgFunctionsWS"
        client = Client(soap_service_url, transport=Transport(
            session=session, cache=SqliteCache()))

        soap_response = client.service.GetItemImageMS(itemNo=item_number)

        serialized_response = serialize_object(soap_response)
        return serialized_response


    def update_alert_output(self):
        """
        Remotely triggers Microsoft NAV's Alert Output job.
        """
        session = Session()
        session.auth = HTTPBasicAuth(self.nav_user, self.nav_password)

        soap_service_url = self.nav_soap_service + \
            self.nav_company + "/Codeunit/SiteManagementWS"
        client = Client(soap_service_url, transport=Transport(
            session=session, cache=SqliteCache()))

        soap_response = client.service.UpdateAlertOutput()

        serialized_response = serialize_object(soap_response)
        return serialized_response
