from os.path import join as path_join

class LinuxShell:
    def __init__(self, user, configure = None):
        self.user = user
        self.pwd = ""
        self.machine = f"{self.user}@machine:/home/{self.user}# "
        if configure:
            self.configure()

    def stdin(self):
        return input(self.machine)

    def stdout(self):
        return None

    def configure(self):
        type_error = False
        try:
            self.pwd = self.stdout("pwd")
            self.refresh(self.pwd)
        except TypeError:
            type_error = True
            raise TypeError("Standard output function is not configured")
        if not self.pwd:
            if self.user == "root":
                self.pwd = "/root"
                self.refresh(self.pwd)
            elif not type_error:
                self.pwd = f"/home/{self.user}"
                self.refresh(self.pwd)
        if not self.user:
            self.user = "www-data"

    def refresh(self, pwd):
        self.machine = f"{self.user}@machine:{pwd}# "

    def interact(self):
        while True:
            user_input = self.stdin().strip(' ')
            if user_input.startswith('cd '):
                print(user_input)
                temporary = user_input.split('cd ')[-1].strip(' ')
                if '/' in temporary and temporary.startswith('/'):
                    self.pwd = temporary
                else:
                    self.pwd = path_join(self.pwd, temporary)
                self.refresh(self.pwd)
            elif user_input == 'pwd':
                self.refresh(self.pwd)

            data = self.stdout(user_input)
            if data:
                print(data)
            elif data == "\n" or not data:
                print(f"machine: {user_input}: command not found")
