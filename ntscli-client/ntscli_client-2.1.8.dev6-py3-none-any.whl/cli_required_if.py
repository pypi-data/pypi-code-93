import click

class RequiredIf(click.Option):
    def __init__(self, *args, **kwargs):
        self.required_if = kwargs.pop('required_if')
        assert self.required_if, "'required_if' parameter required"
        for key, value in self.required_if.items():
            message = ' [NOTE: This argument is required when \"%s\" is passed.]' % key \
                if value == True \
                else ' [NOTE: This argument is required when \"%s\" is \"%s\".]' % (key, value)
            kwargs['help'] = (kwargs.get('help', '') + message).strip()
        super(RequiredIf, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        we_are_present = self.name in opts

        for key, value in self.required_if.items():
            opts_key = key.replace("-", "_")
            if opts_key in opts:
                if not we_are_present:
                    if opts[opts_key] == value:
                        message = ' [NOTE: Illegal usage: `%s` is required when \"%s\" is \"%s\".]' % (self.name, key, value)
                        raise click.UsageError(message)
                    elif value is True:
                        message = ' [NOTE: Illegal usage: `%s` is required when \"%s\" is passed.]' % (self.name, key)
                        raise click.UsageError(message)
                else:
                    self.prompt = None

        return super(RequiredIf, self).handle_parse_result(
            ctx, opts, args)
