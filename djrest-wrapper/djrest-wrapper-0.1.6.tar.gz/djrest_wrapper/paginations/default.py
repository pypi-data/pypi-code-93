from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class DefaultPagination(PageNumberPagination):
    page_size = 10

    def get_paginated_response(self, data):
        return Response({
            'page': {
                'next': self.get_next_link(),
                'previous': self.get_previous_link(),
                'current': self.page.number,
                'count': self.page.paginator.count,
                'total_pages': self.page.paginator.num_pages,
            },
            self.page_result_key: data
        })
