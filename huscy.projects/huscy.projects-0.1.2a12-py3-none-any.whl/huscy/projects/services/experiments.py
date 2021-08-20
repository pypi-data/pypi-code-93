from huscy.projects.models import Experiment


def create_experiment(project, title='', description='', order=0):
    project_experiment_count = project.experiments.count()

    return Experiment.objects.create(
        description=description,
        order=order or project_experiment_count + 1,
        project=project,
        title=title or f'Experiment {project_experiment_count+1}',
    )


def get_experiments(project=None):
    queryset = Experiment.objects
    if project:
        queryset = queryset.filter(project=project)
    return queryset.all()
