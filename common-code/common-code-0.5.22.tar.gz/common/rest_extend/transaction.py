from common.rest_extend.response import Results


class MySQLTransaction():
    def post(self, request, obj, obj_serializer, obj_relevance: list = None, m_to_m_obj: list = None,
             mapping=None,
             m_to_m_mapping=None, data=None):
        results = Results()
        if not data:
            data = request.data
        if data.get('data'):
            data = data.get('data')
        serializer = obj_serializer(data=data)
        if obj_relevance and mapping:
            for obj in obj_relevance:
                obj_name = obj.__name__.lower()
                obj_mapping = mapping.get(obj_name)
                if not obj_mapping:
                    raise Exception(f'{obj_name}  are not mapping!!!')
                queryset = self.get_relevance_queryset(obj, obj_name, data)
                self.extend_relevance_data(data, queryset, obj_mapping)
        if m_to_m_obj and m_to_m_mapping:
            for obj in m_to_m_obj:
                pass
        try:
            valid = serializer.is_valid(raise_exception=True)
            serializer.save()
            results.describe = "add  successfully！！！"
            results.status = SUCCESS
            results.code = 200
        except Exception as e:
            results.code, results.describe = get_error_status_code(e)

        return RESTResponse(results)
