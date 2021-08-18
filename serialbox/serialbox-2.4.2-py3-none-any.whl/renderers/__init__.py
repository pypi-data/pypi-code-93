from rest_framework import renderers


class SBAdminRenderer(renderers.AdminRenderer):
    template = 'rest_framework/sbadmin.html'
