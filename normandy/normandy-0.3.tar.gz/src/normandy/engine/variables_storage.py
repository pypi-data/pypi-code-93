
class variables_storage:

    def update(self, name, var):
        from _pickle import dump

        with open(f"temp/{name}", "wb") as file:
            dump(var, file)

    def get(self, name):
        from _pickle import load

        with open(f"temp/{name}", "rb") as file:
            return load(file)
