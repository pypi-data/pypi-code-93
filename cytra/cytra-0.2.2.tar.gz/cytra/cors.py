from gongish import HTTPNoContent


class CORSAppMixin:
    def _set_cors(self):
        for key, val in self._cors_headers:
            self.response.headers[key] = val

    def dispatch(self, path, verb):
        if verb == "options":

            def handler():
                raise HTTPNoContent

            return handler, ()

        return super().dispatch(path, verb)

    def on_begin_response(self):
        self._set_cors()
        return super().on_begin_response()

    def on_error(self, exc):
        self._set_cors()
        return super().on_error(exc)

    def setup(self):
        super().setup()
        self._cors_headers = (
            ("Access-Control-Allow-Origin", "*"),
            ("Access-Control-Allow-Credentials", "true"),
            (
                "Access-Control-Allow-Methods",
                ",".join(self.__cors_allow_methods__),
            ),
            (
                "Access-Control-Allow-Headers",
                ",".join(self.__cors_allow_headers__),
            ),
            (
                "Access-Control-Expose-Headers",
                ",".join(self.__cors_expose_headers__),
            ),
        )
