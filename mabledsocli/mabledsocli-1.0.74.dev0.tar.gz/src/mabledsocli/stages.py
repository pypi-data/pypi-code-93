
import re
from .constants import *
from .exceptions import DSOException


REGEX_PATTERN = r"^([a-zA-Z][a-zA-Z0-9]+)/?([0-9])?$"

class Stages():

    # @staticmethod
    # def default_stage():
    #     return 'default/0'

    @staticmethod
    def raw_parse(stage):
        if not stage:
            import traceback
            traceback.print_stack() 
            raise DSOException(MESSAGES['Stage'].format(stage, REGEX_PATTERN))
        m = re.match(REGEX_PATTERN, stage)
        if m is None:
            raise DSOException(MESSAGES['InvalidStage'].format(stage, REGEX_PATTERN))
        stage = m.groups()[0]
        env = int(m.groups()[1]) if len(m.groups()) > 1 and m.groups()[1] else ''
        return stage, env

    @staticmethod
    def normalize(stage):
        stage, env = Stages.raw_parse(stage)
        # stage = stage or 'default'
        ### force dafault env if stage is default: default/env not allowed
        env = env if env and not stage == 'default' else 0
        return f"{stage}/{env}"

    def parse_normalized(stage):
        stage = Stages.normalize(stage)
        return Stages.raw_parse(stage)

    @staticmethod
    def get_default_env(stage):
        stage = Stages.parse_normalized(stage)[0]
        return f"{stage}/0"

    @staticmethod
    def parse_name(stage):
        return Stages.parse_normalized(stage)[0]

    @staticmethod
    def parse_env(stage):
        return Stages.parse_normalized(stage)[1]

    @staticmethod
    def shorten(stage):
        if not stage: return 'default'
        stage, env = Stages.parse_normalized(stage)
        if env == 0:
            return stage
        else:
            return f"{stage}/{env}"

    @staticmethod
    def is_default(stage):
        return stage in ['default', 'default/0']

    @staticmethod
    def is_default_env(stage):
        env = Stages.parse_normalized(stage)[1]
        return env == 0
