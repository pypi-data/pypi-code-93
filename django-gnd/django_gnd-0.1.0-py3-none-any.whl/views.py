from django.views.generic import TemplateView

from gnd.forms import GndForm


class GndFormView(TemplateView):

    template_name = 'gnd/tryout.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = GndForm
        return context
