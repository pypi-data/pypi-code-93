from huscy.projects import models, services


def test_delete_project(django_user_model, project):
    services.delete_project(project)

    assert not models.Project.objects.exists()
