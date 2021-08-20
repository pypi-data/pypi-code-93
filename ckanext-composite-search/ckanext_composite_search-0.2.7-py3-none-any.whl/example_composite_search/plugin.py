import ckan.plugins as plugins

tk = plugins.toolkit


class ExampleCompositeSearchPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)

    # IConfigurer

    def update_config(self, config_):
        tk.add_resource('assets', 'example_composite')
        tk.add_template_directory(config_, 'templates')
