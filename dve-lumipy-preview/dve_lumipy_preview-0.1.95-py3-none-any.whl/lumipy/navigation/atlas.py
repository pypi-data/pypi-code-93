from lumipy.common.lockable import Lockable
from lumipy.common.string_utils import indent_str, connector, prettify_tree, random_globe
from lumipy.navigation.provider_metadata import ProviderMetadata
from typing import List, Optional, Callable, Union

from lumipy.navigation.metaprovider import MetaProvider


class Atlas(Lockable):
    """The Atlas class represents information on collections of Luminesce providers.

    Information defining each provider is available as an attribute on the instance.
    """

    def __init__(self, provider_metadata_list: List[ProviderMetadata], **kwargs):
        """__init__ method of the Atlas class.

        Args:
            provider_metadata_list (List[ProviderMetadata]): list of provider definitions that will be stored
            and presented by the atlas
            **kwargs: keyword args specifying metadata to be displayed on the atlas printout.
        """
        if len(provider_metadata_list) == 0:
            raise ValueError("Atlas construction failed: provider definitions list input was empty.")

        self._client = provider_metadata_list[0].get_client()
        self._metadata = kwargs
        for p_meta in provider_metadata_list:
            self.__dict__[p_meta.get_name()] = MetaProvider(p_meta)
        super().__init__()

    def __str__(self):
        globe = random_globe()
        out_str = f" {globe}Atlas\n"
        if len(self._metadata) > 0:
            out_str += f"  {connector}Metadata:\n"
        for k, v in self._metadata.items():
            out_str += f"    {connector}{k}: {v}\n"

        out_str += f"  {connector}Available providers:\n"
        provider_strings = []
        for k, v in self.__dict__.items():
            if isinstance(v, MetaProvider):
                provider_strings.append(indent_str(v._mini_str(), n=4))

        out_str += "\n".join(
            provider_strings
        )
        return prettify_tree(out_str)

    def __repr__(self):
        return str(self)

    def list_providers(self) -> List[MetaProvider]:
        """Returns a list of the provider definitions in this atlas.

        Returns:
            List[ProviderMetadata]: list of provider definitions.
        """
        return [v for _, v in self.__dict__.items() if isinstance(v, MetaProvider)]

    def search_providers(self, target: Union[str, Callable]) -> 'Atlas':
        """Search the Atlas for providers that match a search string.

        Search is case-insensitive and only looks if the string is in the provider's python name, Luminese table name,
        or if the string is in the provider's description.

        Args:
            target (Optional[str]): the target string to search for. Must be supplied if filter_fn isn't.

        Returns:
            Atlas: another Atlas object containg providers that contain the search string.
        """

        if callable(target):
            def wrap_filter_fn(p):
                result = target(p)
                if isinstance(result, bool):
                    return result
                else:
                    raise TypeError(f"Search fn must always return a boolean. Returned a {type(result).__name__}.")

            search_filter = wrap_filter_fn
        elif isinstance(target, str):
            def check(p_meta):
                return (target.lower() in p_meta.get_name()) \
                       or (target.lower() in p_meta.get_table_name().lower()) \
                       or (target.lower() in p_meta.get_description().lower()) \
                       or any(target.lower() in f.field_name.lower() for f in p_meta.list_fields())

            search_filter = check
        else:
            raise ValueError("Invalid search criteria supplied: supply a string or a function.")

        return Atlas(
            [p.get_metadata() for p in self.list_providers() if search_filter(p.get_metadata())],
            atlas_type="Search Result",
            search_target=f'"{target}"'
        )

    def get_provider(self, target):
        result = [
            p for p in self.list_providers()
            if target.lower() == p.get_table_name().lower()
        ]
        if len(result) == 1:
            return result[0]
        else:
            # There can never be duplicate providers with the same name
            raise ValueError(f"Provider {target} not found in atlas.")

    def get_client(self):
        return self._client

    def get_namespaces(self, path):

        if path.endswith('.'):
            in_path = path[:-1]
        else:
            in_path = path

        locs = in_path.split('.')
        ppaths = [p.get_table_name().split('.') for p in self.list_providers()]

        for loc in locs:
            ppaths = [ppath[1:] for ppath in ppaths if len(ppath) > 1 and ppath[0] == loc]

        return list(set([f"{in_path}.{p[0]}" if len(p) > 0 else in_path for p in ppaths]))
