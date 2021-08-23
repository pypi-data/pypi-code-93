from textwrap import TextWrapper
from typing import List

from .utils import get_domain, get_metadatarecord, map_metadatarecord_to_result


class Entity:
    """
    Class to represent every ELG entity
    """

    def __init__(
        self,
        id: int,
        resource_name: str,
        resource_short_name: List[str],
        resource_type: str,
        entity_type: str,
        description: str,
        keywords: List[str],
        detail: str,
        licences: List[str],
        languages: List[str],
        country_of_registration: List[str],
        creation_date: str,
        last_date_updated: str,
        functional_service: bool,
        functions: List[str],
        intended_applications: List[str],
        views: int,
        downloads: int,
        size: int,
        service_execution_count: int,
        status: str,
        under_construction: bool,
        domain: str,
        record: dict = None,
        **kwargs,
    ):
        """Init an Entity object with the entity information"""
        self.id = id
        self.resource_name = resource_name
        self.resource_short_name = resource_short_name
        self.resource_type = resource_type
        self.entity_type = entity_type
        self.description = description
        self.keywords = keywords
        self.detail = detail
        self.licences = licences
        self.languages = languages
        self.country_of_registration = country_of_registration
        self.creation_date = creation_date
        self.last_date_updated = last_date_updated
        self.functional_service = functional_service
        self.functions = functions
        self.intended_applications = intended_applications
        self.views = views
        self.downloads = downloads
        self.size = size
        self.service_execution_count = service_execution_count
        self.status = status
        self.under_construction = under_construction
        self.domain = domain
        self.record = record

    def __str__(self):
        id_wrapper = TextWrapper(initial_indent="Id             ", width=70, subsequent_indent=" " * 15)
        name_wrapper = TextWrapper(initial_indent="Name           ", width=70, subsequent_indent=" " * 15)
        resource_type_wrapper = TextWrapper(initial_indent="Resource type  ", width=70, subsequent_indent=" " * 15)
        entity_type_wrapper = TextWrapper(initial_indent="Entity type    ", width=70, subsequent_indent=" " * 15)
        description_wrapper = TextWrapper(initial_indent="Description    ", width=70, subsequent_indent=" " * 15)
        licences_wrapper = TextWrapper(initial_indent="Licences       ", width=70, subsequent_indent=" " * 15)
        languages_wrapper = TextWrapper(initial_indent="Languages      ", width=70, subsequent_indent=" " * 15)
        status_wrapper = TextWrapper(initial_indent="Status         ", width=70, subsequent_indent=" " * 15)
        return (
            "-" * 70
            + "\n"
            + id_wrapper.fill(str(self.id))
            + "\n"
            + name_wrapper.fill(str(self.resource_name))
            + "\n"
            + resource_type_wrapper.fill(str(self.resource_type))
            + "\n"
            + entity_type_wrapper.fill(str(self.entity_type))
            + "\n"
            + description_wrapper.fill(str(self.description))
            + "\n"
            + licences_wrapper.fill(str(self.licences))
            + "\n"
            + languages_wrapper.fill(str(self.languages))
            + "\n"
            + status_wrapper.fill(str(self.status))
            + "\n"
            + "-" * 70
        )

    def __repr__(self):
        return str(self.__class__)[:-1] + f" [{self.id}] {self.resource_name}>"

    @classmethod
    def from_search_result(cls, result: dict, domain: str = "live"):
        """
        Class method to init an Entity object from a search result.

        Args:
            result (dict): result of the search API.
            domain (str, optional): ELG domain you want to use. "live" to use the public ELG, "dev" to use the
                development ELG and another value to use a local ELG. Defaults to "live".

        Returns:
            elg.Entity: Entity object.
        """
        result["domain"] = get_domain(domain=domain)
        # Add default value here because this field is not returned by the catalog in the dev cluster
        if "functional_service" not in result.keys():
            result["functional_service"] = True
        # Add default values to some parameters as they have been removed from the search API result
        if "status" not in result.keys():
            result["status"] = None
        if "size" not in result.keys():
            result["size"] = None
        return cls(**result)

    @classmethod
    def from_id(
        cls,
        id: int,
        domain: str = "live",
        use_cache: bool = True,
        cache_dir: str = "~/.cache/elg",
    ):
        """
        Class method to init an Entity object from its id.

        Args:
            id (int): id of the entity.
            domain (str, optional): ELG domain you want to use. "live" to use the public ELG, "dev" to use the
                development ELG and another value to use a local ELG. Defaults to "live".
            use_cache (bool, optional): True if you want to use cached files. Defaults to True.
            cache_dir (str, optional): path to the cache_dir. Set it to None to not store any cached files. Defaults to "~/.cache/elg".

        Returns:
            elg.Entity: Entity object.
        """
        domain = get_domain(domain=domain)
        record = get_metadatarecord(id=id, domain=domain, use_cache=use_cache, cache_dir=cache_dir)
        result = map_metadatarecord_to_result(id, record)
        result["domain"] = domain
        return cls(**result)
