# -*- coding: utf-8 -*-
"""
    binalyzer_core
    ~~~~~~~~~~~~~~

    The core package of the Binalyzer library.

    :copyright: 2021 Denis Vasilík
    :license: MIT, see LICENSE for details.
"""

name = "binalyzer_core"

__tag__ = "v1.0.2"
__build__ = 151
__version__ = "{}".format(__tag__)
__commit__ = "031113f"

from .binalyzer import (
    Binalyzer,
)
from .extension import (
    BinalyzerExtension,
)
from .template import (
    Template,
)
from .template_engine import (
    TemplateEngine,
)
from .properties import (
    PropertyBase,
    ValueProperty,
    ReferenceProperty,
    AutoSizeValueProperty,
    StretchSizeProperty,
    OffsetValueProperty,
    RelativeOffsetValueProperty,
    RelativeOffsetReferenceProperty,
)
from .binding import (
    BindingContext,
    BackedBindingContext,
)
from .factory import (
    TemplateFactory,
)
from .template_provider import (
    TemplateProviderBase,
    TemplateProvider,
    PlainTemplateProvider,
)
from .data_provider import (
    DataProviderBase,
    DataProvider,
    BufferedIODataProvider,
    ZeroedDataProvider,
)
from .value_provider import (
    ValueProviderBase,
    ValueProvider,
    RelativeOffsetValueProvider,
    RelativeOffsetReferenceValueProvider,
    AutoSizeValueProvider,
    StretchSizeValueProvider,
    TemplateValueProvider,
    value_cache,
)
from .utils import (
    siblings,
    rightsiblings,
    leftsiblings,
)