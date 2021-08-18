
import os
import sys


class Parameters(object):

    def __init__(self):
        pass

    def pop_parm(self, parameters, key):
        if key in parameters.keys():
            parameters.pop(key)
        return parameters

    @staticmethod
    def get_default_base_path():
        if "win" in sys.platform.lower():
            base_path = r"\\172.29.190.4\share\sqa\FW_Release\redtail"   #shanghai r"\\10.3.10.2\Share\sqa\dell_bin\logs"
        else:
            base_path = "/mnt/sqa/FW_Release/redtail"
        return base_path

    def generate_redtail_images(self, parameters):
        output_parm = dict()
        if "base_path" in parameters:
            base_path = parameters["base_path"]
        else:
            base_path = self.get_default_base_path()
        if "image1" not in parameters.keys() and "volume" in parameters.keys() and "base_version" in parameters.keys():
            ret = self.get_image_path(base_path, parameters["volume"], parameters["base_version"])
            if ret is not None:
                output_parm["image1"] = ret
                output_parm["base_version"] = parameters["base_version"]
        if "image2" not in parameters.keys():
            if "volume" in parameters.keys() and "target_version" in parameters.keys():
                ret = self.get_image_path(base_path, parameters["volume"], parameters["target_version"])
                if ret is not None:
                    output_parm["image2"] = ret
                    output_parm["target_version"] = parameters["target_version"]
            else:
                if "image1" in output_parm.keys():
                    output_parm["image2"] = output_parm["image1"]
                    output_parm["target_version"] = output_parm["base_version"]
        return output_parm

    def get_image_path(self, base_path, volume, commit_id):
        # commit_id = commit_id[0:6]
        _files = os.listdir(base_path)
        if os.path.exists(base_path):
            for item in _files:
                item_path = os.path.join(base_path, item)
                if os.path.isdir(item_path):
                    ret = self.get_image_path(item_path, volume, commit_id)
                    if ret is not None:
                        return ret
                elif ("_{}_".format(volume) in item) and (commit_id in item):
                    return os.path.join(base_path, item)
