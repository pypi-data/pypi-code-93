import subprocess


class DeviceFlasher(object):
    def __init__(self):
        self._flash_methods = list()
        self._name = ""
        self._supported_platforms = list()
        self._needs_scan = False
        self._description = ""
        self._flash_file_ext = ".bin"

    @property
    def name(self):
        return self._name

    @property
    def flash_methods(self):
        return self._flash_methods

    @property
    def supported_platforms(self):
        return self._supported_platforms

    @property
    def needs_scan(self):
        return self._needs_scan

    @property
    def description(self):
        return self._description

    @property
    def flash_file_ext(self):
        return self._flash_file_ext

    def _wait_for_process(self, command):
        print("Running the following command: ")
        print(command)
        sub_proc = subprocess.Popen(
            command[0], stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
        )
        p_val = sub_proc.poll()
        while p_val is None:
            print(sub_proc.stdout.read().decode("UTF-8"))
            print(sub_proc.stderr.read().decode("UTF-8"))
            p_val = sub_proc.poll()

        if p_val is 0:
            print("Process Completed successfully.")
        else:
            print("And error occured. Error code {}".format(p_val))
