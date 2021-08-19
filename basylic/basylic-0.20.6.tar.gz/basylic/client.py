import os
import requests
import json


class Basylic:
    """Class to access Basylic's API."""
    def __init__(self, refresh_token=None):
        """
        Instantiates the class Basylic which allows to access the Basylic API
        with given refresh token. To obtain your refresh token, visit 
        https://portal.basylic.fr/user. 
        
        Then, put the value of your refresh token in environment variable BASYLIC_REFRESH_TOKEN:
        >>> basylic = Basylic()

        Otherwise, you can specify it manually:

        >>> basylic = Basylic(refresh_token="...")
        """
        self.token = self.obtain_access_token(refresh_token)
    
    def obtain_access_token(self, refresh_token):
        """Returns the access token for given refresh token"""
        refresh_token = refresh_token or os.getenv("BASYLIC_REFRESH_TOKEN")
        url = "https://portal.basylic.fr/api/auth"
        data = {"refresh_token": refresh_token, "get": "token"}
        r = requests.post(url, data=data)
        return r.json()
    
    def send_document(self, file_path=None, document_type=None, applicants_information={}, file_obj=None, **kwargs):
        """Checks if document is fraudulent or genuine. 
        To call this method it is required:
        
        1. To put your access token in the environment variable BASYLIC_ACCESS_TOKEN and then to instantiate the class Basylic as follows:
        >>> basylic = Basylic()
        
        2a. One minimal set of arguments to use the document checker are `document_type` and `file_path`:
        >>> basylic.send_document(file_path="corinne-berthier-recto-verso.pdf", document_type="french_ids")

        The file_path argument is a string that contains the path to the file to be sent to Basylic.
        
        2b. The other minimal set of arguments to use the document checker are `document_type` and `file_obj`:
        >>> basylic.send_document(file_obj=file, document_type="french_ids")

        Where `file_obj` is a Multipart-encoded file (such as Django `InMemoryUploadedFile`) to be sent to Basylic.

        Document type is a string that specifies which Basylic sub-service will be used. Possible values for `document_type` are: 'french_ids', 'rib', 'ri', 'avis-imposition'...
        
        This will return a comprehensive JSON document with document compliance check and OCR transcription, among other information.

        If `file_obj` and `file_path` are both specified, `file_obj` will be sent to Basylic.

        3. It is recommended to include data about applicants. Data extracted by Basylic's OCR will be crosschecked with those data.
        >>> applicant_information = {"applicant_0": {"name": "BERTHIER"}}
        >>> basylic.send_document(file_path = "corinne-berthier-recto-verso.odf", document_type="french_ids")

        4. Various arguments could be passed as kwargs. For example:
        a. `save_report=True` will save the result of your request to your user space on Basylic's Portal.
        b. `with_image=True` will return a base64 image for each recognised document. This is handy if you wish to print the input image for comparison.
        c. `reference='abc...'` will add this key-value pair to the API output. If this key is specified, the report will appear under this name in Basylic's Portal. 
        """
        url = kwargs.get("url") or "https://api.basylic.io"

        if not document_type:
            return {"error": "The `document_type` argument is required. Possible values are `french_ids`, `rib`, `ri`, among others (please refer to list of services in Basylic Portal.)"}
        
        if file_obj:
            buffer = file_obj.file
            if hasattr(file_obj, "name"):
                filename = file_obj.name
            elif hasattr(file_obj, "filename"):
                filename = file_obj.filename
            else:
                filename = "untitled"
        else:
            if not file_path:
                return {"error": "Either `file_obj` or `file_path` should be specified"}
            buffer = open(file_path, "rb")
            filename = os.path.basename(file_path)
        
        files = {"file": ("uploaded_file", buffer)}

        data = {
            "api": document_type,
            "with_image": True,
            "crosschecking": True,
            "applicants_information": applicants_information,
            "document_basename": filename
        }
        data.update(kwargs)

        payload = dict(
            url=url,
            headers={"TOKEN": self.token},
            data={"data": json.dumps(data)},
            files=files
        )

        with requests.Session() as api:
            r = api.post(**payload)
        try:
            r.raise_for_status()
        except requests.HTTPError:
            print("Basylic returned error message : ")
            print(r.content.decode("utf-8"))
            raise
        return r.json()
