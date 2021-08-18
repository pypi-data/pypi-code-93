"""
This is a python wrapper client for the Zenefits API.

We include base methods for returning Zenefits data in a dictionary format.

To see api endpoints see: https://developers.zenefits.com/docs/getting-started
"""
import requests
import logging
import json
logging.basicConfig(level=logging.NOTSET)

class ZenefitsClient():
    """
    Our base client. You should generate an Access Token as described in the Zenefits
    API docs
    """
    def __init__(self, access_token, sandbox=False):

        self.sandbox = sandbox
        self.access_token = access_token

        # Caches to prevent redundant api calls
        self.cache = {}

    ########################################################################
    # Caching Functions                                                     #
    ########################################################################
    def check_cache(self, ref_object_str):
        """
        Check the cache if items exist

        Args:
            ref_object_str (string): zenefits ref_object of the objects (i.e. "/core/people")
            object_id (string): string id of the zenefits object

        Returns:
            bool: Whether the string is actually in the cache, used to determine if we've called a url
        """
        return True if ref_object_str in list(self.cache.keys()) else False
    
    def get_from_cache(self, ref_object_str, object_id=None):
        """
        Grab the objects (or object) from cache

        Args:
            ref_object (string): zenefits ref_object of the objects (i.e. "/core/people")
            object_id (string): string id of the zenefits object

        Returns:
            dict: Return the dictionary of the ids, or just the object if given id
        """
        items = self.cache.get(ref_object_str)
        if items:
            if object_id:
                return items.get(object_id)
            return items
        
        return {}

    def insert_into_cache(self, ref_object_str, zenefit_objects):
            """
            Populate our client cache with the given ref_object and a list of zenefit objects.
            This function will fully replace the cached ref_object
            {
                ref_object_str: {
                    id: zenefit_object,
                    id: zenefit_object
                }
            }
            Should be called after get_url_objects to prevent redundant calls

            Args:
                ref_object_str (string): The cache ref_object_str, zenefits ref_object_str of the objects (i.e. "/core/people")
                zenefit_objects (list): List of the zenefit objects we want to cache
            """
            cached_items = {}
            for zenefit_object in zenefit_objects:
                obj_id = zenefit_object.get("id")
                cached_items[obj_id] = zenefit_object

            self.cache[ref_object_str] = cached_items

            logging.info(f"Cached updated for {ref_object_str}")
    
    def populate_cache(self, zenefits_reference_obj):
        """
        Populate the cache with the items from the given Zenefits reference object.
        Will replace existing items in the cache.

        Args:
            zenefits_reference_obj (dict): Zenefits Reference Object
        """
        # We always call all items under the assumption that querying one item 
        # through this client will lead to additional queries
        # TODO implement a faster one item pull method

        # Fetch all my objects
        ref_object_str = zenefits_reference_obj.get("ref_object")
        data = self.get_url_objects("https://api.zenefits.com" + ref_object_str)
        self.insert_into_cache(ref_object_str, data)
        self.cache
        logging.info(f"Populating Cache for {ref_object_str}") 
            
    ########################################################################
    # Helper Functions                                                     #
    ########################################################################
    def populate_reference_object(self, zenefits_reference_object):
        """
        Populate the given Zenefits object (one level deep only)

        Args:
            zenefits_reference_object (dict): A single Zenefits reference object to populate
            example: 
                {
                    "object": "/meta/ref/list",
                    "ref_object": "/core/people",
                    "url": "https://api.zenefits.com/core/departments/1/people"
                }

        Returns:
            [dict]: The populated Zenefits reference object
            example: 
                {
                    "name": {},
                    "name2": {}
                }
        """
        # First check our cache if we've called our cache before
        in_cache = self.check_cache(zenefits_reference_object.get("ref_object"))

        # If we haven't populated our cache, populate our cache
        if not in_cache:
            self.populate_cache(zenefits_reference_object)

        # Grab our cached objects
        cached_object = self.get_from_cache(zenefits_reference_object.get("ref_object"))

        # Determine what type of object we want to return (list or detail)
        object_type = zenefits_reference_object.get("object").split("/")[-1]
        # If we are a list type object, return the cached entry
        if object_type == "list":

            return cached_object
        # If I'm a detail object, return just the detailed object
        elif object_type == "detail":
            # Grab the ID from the url
            # Sometimes it's after a /, sometimes it's after a =
            if not zenefits_reference_object.get("url"):
                
                return {}
            object_id = zenefits_reference_object.get("url").split("/")[-1]
            if '=' in object_id:
                object_id = zenefits_reference_object.get("url").split("=")[-1]

            return cached_object.get(object_id)


    ########################################################################
    # API Call Functions                                                   #
    ########################################################################
    def get_url_objects(self, url, includes=None):
        """
        Retrieve the base objects returned from the given url. Takes into account paginated requests and pulls
        all objects. Can pass in a list of parameters in includes to populate the reference items
        Note that Zenefits API restricts what fields can be in includes, which is why for our main client
        calls we don't use it.

        Args:
            url (str): URL that we want to pull from
            includes (list): List of parameter strings telling Zenefits to populate objects

        Returns:
            zenefit_objects (list): List of zenefit objects

        """
        zenefit_objects = []

        payload = {}
        headers = {
            'Authorization': f"Bearer {self.access_token}", 
            "Content-Type": "application/json; charset=utf-8"
        }

        # Populate the given fields from zenefits
        if includes:
            includes_string = includes[0]
            for parameter in includes[1:]:
                includes_string = includes_string + " " + parameter
            payload["includes"] = includes_string

        response = requests.get(url, auth=None, params=payload, headers=headers, verify=True, timeout=10.000)
        if response.status_code != 200:
            logging.ERROR("Objects not fetched")

            return response

        # Yes they return a nested object with another nested object called data
        data = json.loads(response.content.decode("utf-8"))['data']
        
        # Check to see if there is a second data object called data
        # Perform the check if in keys to account for the case where data is
        # an empty list. I.e. as long as data['data'] exists, even if empty, extend it
        zenefit_objects.extend(data['data']) if ('data' in list(data.keys())) else zenefit_objects.extend(data)

        # Check our paginated url, while one exists, continue extending the list unitl I have all objects
        next_url = data.get('next_url')
        if next_url:
            zenefit_objects.extend(self.get_url_objects(next_url))
        
        return zenefit_objects

    
    ########################################################################
    # Core Client Call Functions                                           #
    ########################################################################
    def get_department(self, name=None, populate=True):
        """
        Retrieve all departments unless name specified. Includes populated references as objects.
        We only populate one level deep (i.e. department: {people: { company }} will have the info
        for department and people, but company will be the url that Zenefits sends back.

        Args:
            name (str, optional): Name of department to return. Defaults to None.
            populate (bool, optional): Populate reference objects. Defaults to True.
        
        Returns:
            [dict]: Dictionary of department names and values
        """
        url = "http://api.zenefits.com/core/departments"

        data = self.get_url_objects(url)
        # Data is a list of objects. For related items (i.e. People) Zenefits returns a URL. We need to populate them.
        
        self.populate_cache(
            {
                "object": "/meta/ref/list",
                "ref_object": "/core/departments",
                "url": f"{url}"
            }
        )

        populated_data = {}
        for department in data:
            # Populate my references to other objects
            populated_department = {}
            for key, value in department.items():
                # If my value is an object and I want to populate (include objects)
                if type(value) is dict and populate:
                    populated_department[key] = self.populate_reference_object(value)
                # If my value isn't an object, just set to the value
                else:
                    populated_department[key] = value
            # Add my newly populated dictionary to my populated data
            populated_data[department['name']] = populated_department

        if name:
            return populated_data[name]

        return populated_data

    def get_people(self, name=None, populate=True):
        """
        Retrieve all people unless name specified. Includes populated references as objects.
        We only populate one level deep (i.e. department: {people: { company }} will have the info
        for department and people, but company will be the url that Zenefits sends back.

        Args:
            name (str, optional): FirstName_LastName of a person. Defaults to None.
            populate (bool, optional): Populate reference objects. Defaults to True.
        
        Returns:
            [dict]: Dictionary of peoples FirstName_LastName and values
        """
        url = "http://api.zenefits.com/core/people"
        
        data = self.get_url_objects(url)
        # Populate our cache
        self.populate_cache(
            {
                "object": "/meta/ref/list",
                "ref_object": "/core/people",
                "url": f"{url}"
            }
        )

        populated_data = {}
        for people in data:
            # Populate my references to other objects
            populated_people = {}
            for key, value in people.items():
                # If my value is an object and I want to populate (include objects)
                if type(value) is dict and populate:
                    populated_people[key] = self.populate_reference_object(value)
                # If my value isn't an object, just set to the value
                else:
                    populated_people[key] = value
            # Add my newly populated dictionary to my populated data
            full_name = populated_people['first_name'] + '_' + populated_people['last_name']
            populated_data[full_name] = populated_people

        if name:
            return populated_data[name]

        return populated_data