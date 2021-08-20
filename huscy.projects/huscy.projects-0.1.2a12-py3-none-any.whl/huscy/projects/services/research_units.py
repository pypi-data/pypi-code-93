from huscy.projects.models import ResearchUnit


def get_research_units():
    return ResearchUnit.objects.order_by('name')
