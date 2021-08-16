from rest_framework.viewsets import GenericViewSet
from ..paginations import DefaultPagination
from .mixins import CreateMixin, RetrieveMixin, UpdateMixin, ListMixin, DestroyMixin


class BaseViewSet(GenericViewSet, CreateMixin, RetrieveMixin, UpdateMixin, ListMixin, DestroyMixin):
    serializer_action_classes = {}
    permission_action_classes = {}
    page_size = 10
    page_result_key = None
    pagination_class = DefaultPagination

    def _get_request_access_token(self, request):
        current_token = request.headers.get('Authorization', None)
        if current_token != None:
            current_token = current_token.split(' ')[1]
        return current_token

    def get_serializer_class(self, *args, **kwargs):
        try:
            if self.action == 'list':
                return self.serializer_action_classes.get(self.action).get('res')
            return self.serializer_action_classes.get(self.action).get(kwargs.get('type', 'req'))
        except:
            return super().get_serializer_class()

    def get_serializer_response(self):
        return self.get_serializer_class(type='res')

    def get_permissions(self):
        try:
            return [permission() for permission in self.permission_action_classes[self.action]]
        except:
            return super().get_permissions()

    @property
    def paginator(self):
        if not hasattr(self, '_paginator'):
            if self.pagination_class is None:
                self._paginator = None
            else:
                self._paginator = self.pagination_class()
                self._paginator.page_size = self.page_size
                self._paginator.page_result_key = self.page_result_key
        return self._paginator

    def get_queryset(self):
        if self.action == 'list':
            qs = self.queryset.all()
            return qs
        else:
            return super().get_queryset()
