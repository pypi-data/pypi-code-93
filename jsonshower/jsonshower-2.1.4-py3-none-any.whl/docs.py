from typing import List, Dict, Any
from .errors import MissingFieldError

class DocUtilsMixin:
    @classmethod
    def get_field(self, field: str, doc: Dict, missing_treatment: bool='raise_error'):
        """
            For nested dictionaries, tries to access a field.
            e.g. 
            field = kfc.item
            This should return "chickens" based on doc below.
            {
                "kfc": {
                    "item": "chickens"
                }
            }
            Args:
                field:
                    Field of a document.
                doc: 
                    document
                missing_treatment:
                    Can be one of return_empty_string/return_none/raise_error
            Example:
                >>> from vectorai.client import ViClient
                >>> vi_client = ViClient(username, api_key, vectorai_url)
                >>> sample_document = {'kfc': {'item': 'chicken'}}
                >>> vi_client.get_field('kfc.item', sample_document) == 'chickens'
        """
        d = doc
        for f in field.split("."):
            try:
                d = d[f]
            except KeyError:
                try: 
                    return doc[field]
                except KeyError:
                    if missing_treatment == 'return_none':
                        return None
                    elif missing_treatment == 'return_empty_string':
                        return ''
                    raise MissingFieldError("Document is missing " + f + ' of ' + field)

            except TypeError:
                if self._is_string_integer(f):
                    # Get the Get the chunk document out.
                    d = d[int(f)]
                else:
                    if missing_treatment == 'return_none':
                        return None
                    elif missing_treatment == 'return_empty_string':
                        return ''
                    raise MissingFieldError("Document is missing " + f + ' of ' + field)
        return d
    
    @classmethod
    def _is_string_integer(cls, x):
        """Test if a string is numeric
        """
        try:
            int(x)
            return True
        except:
            return False


    @classmethod
    def get_fields(self, fields: List[str], doc: Dict, missing_treatment='return_empty_string') -> List[Any]:
        """
            For nested dictionaries, tries to access a field.
            e.g. 
            field = kfc.item
            This should return "chickens" based on doc below.
            {
                "kfc": {
                    "item": "chickens"
                }
            }
            Args:
                fields:
                    List of fields of a document.
                doc: 
                    document
            Example:
                >>> from vectorai.client import ViClient
                >>> vi_client = ViClient(username, api_key, vectorai_url)
                >>> sample_document = {'kfc': {'item': 'chicken'}}
                >>> vi_client.get_field('kfc.item', sample_document) == 'chickens'
        """
        return [self.get_field(f, doc, missing_treatment) for f in fields]

    def get_field_across_documents(self, field: str, docs: List[Dict], missing_treatment: str='return_empty_string'):
        """
            For nested dictionaries, tries to access a field.
            e.g. 
            field = kfc.item
            This should return "chickens" based on doc below.
            {
                "kfc": {
                    "item": "chickens"
                }
            }
            Args:
                fields:
                    List of fields of a document.
                doc: 
                    document
            Example:
                >>> from vectorai.client import ViClient
                >>> vi_client = ViClient(username, api_key, vectorai_url)
                >>> documents = vi_client.create_sample_documents(10)
                >>> vi_client.get_field_across_documents('size.cm', documents)
                # returns 10 values in the nested dictionary
        """
        return [self.get_field(field, doc, missing_treatment) for doc in docs]
    
    def get_fields_across_document(self, fields: List[str], doc: Dict, missing_treatment='return_empty_string'):
        """
        Get numerous fields across a document.
        """
        return [self.get_field(f, doc, missing_treatment=missing_treatment) for f in fields]
