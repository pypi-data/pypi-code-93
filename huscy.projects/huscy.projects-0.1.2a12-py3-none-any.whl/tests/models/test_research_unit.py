from model_bakery import baker


def test_str_method(django_user_model):
    user = baker.prepare(django_user_model, first_name='first_name', last_name='last_name')
    research_unit = baker.prepare('projects.ResearchUnit', name='ResearchUnit1', code='RU1',
                                  principal_investigator=user)

    assert 'ResearchUnit1 (first_name last_name)' == str(research_unit)
