import configparser
import os
from pathlib import Path

import pytest

from trifacta.util import tfconfig as tfc
from trifacta.util import tfrequests as tfr

CONFIGURATION = "CONFIGURATION"


class TestConfigClass:
    def setup_conf_file(self, directory):
        # set up temporary config file so we can mess with it
        self.base_conf = str(Path.home()) + "/.trifacta.py.conf"
        self.conf = (
            directory.join(".trifacta.py.conf")
        )
        # shutil.copyfile(self.base_conf, self.conf)
        config, exists = tfc.read_config()
        keys = dict(config)
        keys['filepath'] = self.conf
        tfc.setup_configuration(**keys)

    def gen_conf_file(self, keys):
        config = configparser.ConfigParser()

        config[CONFIGURATION] = keys

        with open(self.conf, "w") as f:
            config.write(f)

    # make sure we get a PermissionError if conf file is missing
    def test_check_config_missing(self, tmpdir):
        self.setup_conf_file(tmpdir)
        os.remove(self.conf)
        with pytest.raises(PermissionError):
            tfc.check_config(self.conf)
        with pytest.raises(PermissionError):
            tfr.get_config(self.conf)
        config, config_exists = tfc.read_config(self.conf)
        assert (not config_exists)

    # make sure we get a KeyError on each key in the standard config
    def test_check_config_keys_missing(self, tmpdir):
        self.setup_conf_file(tmpdir)
        config, success = tfc.read_config()
        for k, v in config.items():
            sub = dict(config.items())
            del sub[k]
            self.gen_conf_file(sub)
            with pytest.raises(KeyError):
                tfc.check_config(self.conf)
            os.remove(self.conf)
        self.setup_conf_file(tmpdir)

    # # make sure the printout starts with CONFIGURATION and includes
    # # each key in the standard config
    # def test_print_config(self, capsys):
    #     config, exists = tfc.read_raw_config()
    #     tfc.print_raw_config(config)
    #     config, exists = tfc.read_config()
    #     out, err = capsys.readouterr()
    #     assert(out[0:13] == 'CONFIGURATION')
    #     for k in config.keys():
    #         assert(re.search(str(k), out))
