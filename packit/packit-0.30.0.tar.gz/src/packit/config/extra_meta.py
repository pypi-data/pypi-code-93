from pbr import util

from .base import BaseConfig

from packit.utils import parse_boolean


class ExtraMetaConfig(BaseConfig):

    FIELD_IS_PURE = 'is_pure'

    def __call__(self, config, facility_section_name):
        try:
            # PBR 5.6.0 and later
            # Add a tuple of a tuple and a string, to the end of a tuple: 3 parens.
            util.CFG_TO_PY_SETUP_ARGS += (
                (("metadata", ExtraMetaConfig.FIELD_IS_PURE), ExtraMetaConfig.FIELD_IS_PURE),
            )
        except AttributeError:
            # Before PBR 5.6.0
            util.D1_D2_SETUP_ARGS[ExtraMetaConfig.FIELD_IS_PURE] = ("metadata",)

        meta_config = config.setdefault('metadata', {})

        is_pure_val = meta_config.get(self.FIELD_IS_PURE)

        if is_pure_val is not None:
            is_pure = parse_boolean(is_pure_val)
            meta_config[self.FIELD_IS_PURE] = lambda: is_pure


extra_meta_config = ExtraMetaConfig()
