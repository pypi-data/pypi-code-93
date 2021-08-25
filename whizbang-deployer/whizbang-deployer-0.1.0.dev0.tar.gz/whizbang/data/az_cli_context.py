from az.cli import az


class AzCliContext:
    def __init__(self):
        pass

    def execute(self, command):
        # command = command + " --verbose"
        exit_code, result_dict, logs = az(command)
        if exit_code == 0:
            return result_dict
        else:
            print(result_dict)
            print(logs)
            return None
