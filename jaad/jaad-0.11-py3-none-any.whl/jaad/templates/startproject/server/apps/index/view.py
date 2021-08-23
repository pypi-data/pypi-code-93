from jaad.renderers import PrettyJsonRenderer, renderer
from jaad.view import JaadView, with_parameters

from index.parameters import HelloWorldParameters


@renderer(PrettyJsonRenderer)
class Index(JaadView):
    @with_parameters("GET", HelloWorldParameters)
    def get(self, request, parameters):
        if parameters["name"]:
            return "Hello {}".format(parameters["name"])
        else:
            return "Hello World"
