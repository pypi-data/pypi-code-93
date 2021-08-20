from huscy.projects.models import Session


def create_session(experiment, duration, operator, title='', order=0):
    experiment_session_count = experiment.sessions.count()
    project_session_count = Session.objects.filter(experiment__project=experiment.project).count()

    return Session.objects.create(
        duration=duration,
        experiment=experiment,
        operator=operator,
        order=order or experiment_session_count + 1,
        title=title or f'Session {project_session_count + 1}'
    )


def get_sessions():
    return Session.objects.all()
