import os
import pytest
import tempfile

from seeq import spy
from seeq.base import system


@pytest.mark.system
def test_copy():
    with tempfile.TemporaryDirectory() as temp_folder:
        long_folder_name = os.path.join(temp_folder, 'long_' * 20)
        spy.docs.copy(long_folder_name)

        assert os.path.exists(long_folder_name)
        assert not os.path.exists(os.path.join(long_folder_name, 'spy.workbooks.ipynb'))
        assert not os.path.exists(os.path.join(long_folder_name, 'Advanced Reports and Dashboards.ipynb'))

        with pytest.raises(RuntimeError):
            spy.docs.copy(long_folder_name)

        assert os.path.exists(long_folder_name)

        spy.docs.copy(long_folder_name, overwrite=True, advanced=True)

        assert os.path.exists(long_folder_name)
        assert os.path.exists(os.path.join(long_folder_name, 'spy.workbooks.ipynb'))
        assert os.path.exists(os.path.join(long_folder_name, 'Advanced Reports and Dashboards.ipynb'))

        system.removetree(long_folder_name)
