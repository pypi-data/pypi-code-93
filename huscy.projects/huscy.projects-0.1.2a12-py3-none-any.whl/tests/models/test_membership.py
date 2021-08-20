from model_bakery import baker


def test_str_method(django_user_model):
    project = baker.prepare('projects.Project', title='project1')
    user = baker.prepare(django_user_model, first_name='first_name', last_name='last_name')
    membership = baker.prepare('projects.Membership', project=project, user=user)

    expected_result = 'first_name last_name is member in project project1'
    assert expected_result == str(membership)
