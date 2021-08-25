import abc
import builtins
import datetime
import enum
import typing

import jsii
import publication
import typing_extensions

from .._jsii import *

from .. import (
    FileBase as _FileBase_aff596dc,
    IResolver as _IResolver_0b7d1958,
    Project as _Project_57d89203,
)


class GitAttributesFile(
    _FileBase_aff596dc,
    metaclass=jsii.JSIIMeta,
    jsii_type="projen.git.GitAttributesFile",
):
    '''(experimental) Assign attributes to file names in a git repository.

    :see: https://git-scm.com/docs/gitattributes
    :stability: experimental
    '''

    def __init__(self, project: _Project_57d89203) -> None:
        '''
        :param project: -

        :stability: experimental
        '''
        jsii.create(GitAttributesFile, self, [project])

    @jsii.member(jsii_name="addAttributes")
    def add_attributes(self, glob: builtins.str, *attributes: builtins.str) -> None:
        '''(experimental) Maps a set of attributes to a set of files.

        :param glob: Glob pattern to match files in the repo.
        :param attributes: Attributes to assign to these files.

        :stability: experimental
        '''
        return typing.cast(None, jsii.invoke(self, "addAttributes", [glob, *attributes]))

    @jsii.member(jsii_name="synthesizeContent")
    def _synthesize_content(
        self,
        _: _IResolver_0b7d1958,
    ) -> typing.Optional[builtins.str]:
        '''(experimental) Implemented by derived classes and returns the contents of the file to emit.

        :param _: -

        :stability: experimental
        '''
        return typing.cast(typing.Optional[builtins.str], jsii.invoke(self, "synthesizeContent", [_]))


__all__ = [
    "GitAttributesFile",
]

publication.publish()
