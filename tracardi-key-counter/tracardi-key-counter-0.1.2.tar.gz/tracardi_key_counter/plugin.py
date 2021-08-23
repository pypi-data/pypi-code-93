from tracardi_dot_notation.dot_accessor import DotAccessor
from tracardi_plugin_sdk.domain.register import Plugin, Spec, MetaData
from tracardi_plugin_sdk.action_runner import ActionRunner
from tracardi_plugin_sdk.domain.result import Result
from tracardi.domain.profile import Profile

from tracardi_key_counter.service.key_counter import KeyCounter


class KeyCounterAction(ActionRunner):

    def __init__(self, **kwargs):
        if 'path' not in kwargs:
            raise ValueError("Key `path` not defined in KeyCounterAction.")

        self.path = kwargs['path']

    async def run(self, payload):

        dot = DotAccessor(self.profile, self.session, None, self.event, self.flow)

        if self.path not in dot:
            dot[self.path] = {}

        counter_dict = dot[self.path]

        # save counts
        counter = KeyCounter(counter_dict)
        counter.count(payload)

        dot[self.path] = counter.counts

        self.profile.replace(Profile(**dot.profile))

        return Result(port='counts', value=counter.counts)


def register() -> Plugin:
    return Plugin(
        start=False,
        debug=False,
        spec=Spec(
            module='tracardi_key_counter.plugin',
            className='KeyCounterAction',
            inputs=['payload'],
            outputs=['counts'],
            version="0.1.2",
            license="MIT",
            author="Risto Kowaczewski",
            init={
                'path': None
            }
        ),
        metadata=MetaData(
            name='Key counter',
            desc='Counts keys and saves it in provided dotted path to profile.',
            type='flowNode',
            width=200,
            height=100,
            icon='bar-chart',
            group=['Stats']
        )
    )
