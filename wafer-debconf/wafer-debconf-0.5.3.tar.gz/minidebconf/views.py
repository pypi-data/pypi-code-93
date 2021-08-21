from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from django.views.generic.edit import UpdateView, DeleteView
from django.shortcuts import redirect
from django.urls import reverse
from minidebconf.forms import RegisterForm
from minidebconf.models import Registration, is_registered


class RegistrationMixin:
    @property
    def user(self):
        return self.request.user

    def get_object(self):
        if is_registered(self.user):
            return Registration.objects.get(user=self.user)
        else:
            return Registration(user=self.user)



class RegisterView(LoginRequiredMixin, RegistrationMixin, UpdateView):
    form_class = RegisterForm
    template_name = 'minidebconf/register.html'

    def get_success_url(self):
        return reverse('registration_finished')


class UnregisterView(LoginRequiredMixin, RegistrationMixin, DeleteView):

    def get_success_url(self):
        return reverse('wafer_user_profile', args=[self.user.username])


class RegistrationFinishedView(LoginRequiredMixin, TemplateView):
    template_name = 'minidebconf/registration_finished.html'
