from django.forms import widgets


class GndAcWidget(widgets.Select):

    class Media:
        css = {
            'all': ('https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/css/select2.min.css',)
        }
        js = (
            'https://code.jquery.com/jquery-3.5.1.min.js',
            'https://cdn.jsdelivr.net/npm/select2@4.1.0-rc.0/dist/js/select2.min.js',
            'gnd/lobid-ac.js',
        )

    def update_attrs(self, options, attrs):
        attrs = self.fix_class(attrs)
        for key, val in options.items():
            attrs['data-{}'.format(key)] = val

        return attrs

    def fix_class(self, attrs):
        class_name = attrs.pop('class', '')
        if class_name:
            class_name = f"{class_name} {'custom-select'}"
        else:
            class_name = 'custom-select'
        attrs['class'] = class_name

        return attrs

    def __init__(self, attrs=None, *args, **kwargs):

        attrs = attrs or {}
        options = kwargs.pop('options', {})
        new_attrs = self.update_attrs(options, attrs)
        super().__init__(new_attrs)
