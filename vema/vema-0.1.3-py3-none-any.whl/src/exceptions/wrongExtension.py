class WrongExtension(Exception):
    def __init__(self, extension):
        self.extension = extension;

    def __str__(self):
        return "The render extension is wrong. -> " + self.extension;