import click


# Take from https://stackoverflow.com/questions/51846634/click-dynamic-defaults-for-prompts-based-on-other-options
class OptionPromptNull(click.Option):
    """
    Option class that allows default values based on previous params
    """

    _value_key = "_default_val"

    def __init__(self, *args, **kwargs):
        self.default_option = kwargs.pop("default_option", None)
        super(OptionPromptNull, self).__init__(*args, **kwargs)

    def get_default(self, ctx):
        if not hasattr(self, self._value_key):
            if self.default_option is None:
                default = super(OptionPromptNull, self).get_default(ctx)
            else:
                arg = ctx.params[self.default_option]
                default = self.type_cast_value(ctx, self.default(arg))
            setattr(self, self._value_key, default)
        return getattr(self, self._value_key)
