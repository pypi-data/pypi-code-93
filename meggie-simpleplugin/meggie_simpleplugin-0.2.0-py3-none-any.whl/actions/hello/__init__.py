from meggie.utilities.messaging import messagebox
from meggie.mainwindow.dynamic import Action

class Hello(Action):
    """ Helloes the active subject.
    """
    def run(self):
        subject_name = self.experiment.active_subject.name

        message = 'Hello {}!'.format(subject_name)
        messagebox(self.window, message)
