from cubicweb.predicates import ExpectedValuePredicate


class match_all_http_headers(ExpectedValuePredicate):
    """Return non-zero score if all HTTP headers are present"""

    def __call__(self, cls, request, **kwargs):
        for value in self.expected:
            if not request.get_header(value):
                return 0

        return 1
