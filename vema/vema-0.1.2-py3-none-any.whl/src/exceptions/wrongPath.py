class WrongPath(Exception):
    def __init__(self, path):
        self.path = path;

    def __str__(self):
        return "This path does not exist, it cannot be loaded. -> " + self.path;
