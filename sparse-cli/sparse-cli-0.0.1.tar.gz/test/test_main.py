
from .support import runner

from sparse import config

def test_help():
    result = runner.invoke('--help')

    assert result.exit_code == 0
    assert 'Commands' in result.output

def test_docs():
    result = runner.invoke('docs')
    assert result.exit_code == 0

    assert 'Opened {0}'.format(config.documentation_url()) in result.output
