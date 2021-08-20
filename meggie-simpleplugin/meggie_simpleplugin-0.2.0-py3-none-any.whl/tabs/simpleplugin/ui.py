from meggie.utilities.messaging import messagebox


def hello(experiment, data, window):
    """ Helloes the active subject.
    """
    message = 'Hello {}!'.format(experiment.active_subject.name)
    messagebox(window, message)
