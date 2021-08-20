import click
import operator

class IllegalIf(click.Option):
    def __init__(self, *args, **kwargs):
        self.current_option=args[0][0]
        self.illegal_if = kwargs.pop('illegal_if')
        self.illegal_if_not = kwargs.pop('illegal_if_not')
        assert self.illegal_if or self.illegal_if_not, "'illegal_if' or 'illegal_if_not' parameter required"
        if self.illegal_if:
            self.add_help(self.illegal_if.items(), ' [NOTE: \"%s\" cannot be \"%s\" when \"%s\" is passed.]', kwargs)
        if self.illegal_if_not:
            self.add_help(self.illegal_if_not.items(), ' [NOTE: \"%s\" must be \"%s\" when \"%s\" is passed.]', kwargs)
        super(IllegalIf, self).__init__(*args, **kwargs)

    def handle_parse_result(self, ctx, opts, args):
        we_are_present = self.name in opts

        if we_are_present:
            if self.illegal_if:
                self.check_values(opts,
                                  self.illegal_if.items(),
                                  "Illegal usage: \"%s\" cannot be \"%s\" when \"%s\" is passed.]",
                                  operator.eq)
            if self.illegal_if_not:
                self.check_values(opts,
                                  self.illegal_if_not.items(),
                                  "Illegal usage: \"%s\" must be \"%s\" when \"%s\" is passed.]",
                                  operator.ne)
        else:
            self.prompt = None

        return super(IllegalIf, self).handle_parse_result(
            ctx, opts, args)

    def add_help(self, items, message, kwargs):
        for key, value in items:
            kwargs['help'] = (kwargs.get('help', '') +
                              message %
                              (key, value, self.current_option)
                              ).strip()

    def check_values(self, opts, items, message, relate):
        for key, value in items:
            opts_key = key.replace("-", "_")
            if relate(opts[opts_key], value):
                raise click.UsageError(
                    message % (
                        (key, value, self.current_option)))
