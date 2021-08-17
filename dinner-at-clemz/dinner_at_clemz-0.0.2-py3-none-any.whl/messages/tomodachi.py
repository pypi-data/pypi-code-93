class Tomodachi:

    def __init__(self, name, designation, message):
        self.name = name
        self.designation = designation
        self.message = message
        self.message_sep = "#############################"

    def show_message(self):
         print(''' Message from {} \n Designation: {} \n Message: {}\n {}\n'''\
                    .format(self.name, self.designation, self.message, self.message_sep))


