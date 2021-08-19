from typing import Dict

from tecton._internals import utils
from tecton._internals.sdk_decorators import sdk_public_method


class Fco:
    """
    The class primarily intended for interactively initialized objects (with the exception of the name method)
    """

    @classmethod
    def _fco_type_name_singular_snake_case(cls) -> str:
        raise NotImplementedError

    @classmethod
    def _fco_type_name_plural_snake_case(cls) -> str:
        raise NotImplementedError

    @classmethod
    def _fco_type_name_singular_capitalized(cls) -> str:
        return utils.snake_to_capitalized(cls._fco_type_name_singular_snake_case())

    @classmethod
    def _fco_type_name_plural_capitalized(cls) -> str:
        return utils.snake_to_capitalized(cls._fco_type_name_plural_snake_case())

    @property
    def _fco_metadata(self):
        raise Exception("unimplemented _fco_metadata property")

    @property  # type: ignore
    @sdk_public_method
    def name(self) -> str:
        """
        The name of this Tecton Primitive.
        """
        # This method supports declaratively initialized objects as it is convenient to use
        # in declarative repo for linking FCOs by name
        return self._args.info.name if hasattr(self, "_args") else self._fco_metadata.name  # type: ignore

    @property  # type: ignore
    @sdk_public_method
    def description(self) -> str:
        """
        The description of this Tecton Primitive, set by user.
        """
        return self._fco_metadata.description

    @property  # type: ignore
    @sdk_public_method
    def family(self) -> str:
        """
        The family of this Tecton Primitive, used to group Primitives.
        """
        return self._fco_metadata.family

    @property  # type: ignore
    @sdk_public_method
    def tags(self) -> Dict[str, str]:
        """
        Tags associated with this Tecton Primitive (key-value pairs of arbitrary metadata set by user.)
        """
        return self._fco_metadata.tags

    @property  # type: ignore
    @sdk_public_method
    def owner(self) -> str:
        """
        The owner of this Tecton Primitive (typically the email of the primary maintainer.)
        """
        return self._fco_metadata.owner

    @property  # type: ignore
    @sdk_public_method
    def created_at(self) -> str:
        """
        Returns the creation date of this Tecton Primitive.
        """
        return self._fco_metadata.created_at.ToDatetime().strftime("%Y-%m-%d %H:%M:%S")

    @property  # type: ignore
    @sdk_public_method
    def defined_in(self) -> str:
        """
        Returns filename where this Tecton Primitive has been declared.
        """
        return self._fco_metadata.source_filename

    @property
    def workspace(self) -> str:
        """
        Returns the workspace this Tecton Primitive was created in.
        """
        return self._fco_metadata.workspace
