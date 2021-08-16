from rest_framework.renderers import JSONRenderer
from ..exceptions.apis import ERR_SUCCESSFUL


class DefaultJsonRenderer(JSONRenderer):

    def render(self, data, accepted_media_type=None, renderer_context=None):
        data = {
            'err': data.get('err', False),
            'err_code': data.get('err_code', ERR_SUCCESSFUL),
            'err_msg': data.get('err_msg', None),
            'data': {} if data.get('err', False) else data
        }
        return super(DefaultJsonRenderer, self).render(data, accepted_media_type, renderer_context)
