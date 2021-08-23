class BaseArgsParsing:
    PAGE = "page"
    SIZE = "size"
    PAGESIZE = "pagesize"
    SORT = "sort"
    ASC = "asc"
    DESC = "desc"
    TOKEN = 'token'
    IGNORE_CREATOR = 'ignore_creator'
    ALL_RESULT = 'all_result'

    LIKE = "like"
    NOT = "not"
    IN = "in"
    LT = "lt"
    GT = "gt"
    LTE = "lte"
    GTE = "gte"

    RESERVED_FIELD = [PAGE, SIZE, PAGESIZE, SORT, TOKEN, IGNORE_CREATOR,ALL_RESULT]
    SUFFIX_KEYWORD = [LIKE, NOT, IN, LT, GT, LTE, GTE]

    def get_page_and_size(self, data, max_page=500, max_size=1000, max_total=10000):
        """
        获取页面和条数
        :param data:
        :return:
        """
        try:
            page = int(data.get(self.PAGE, 1))
            size = int(data.get(self.SIZE, 20))
        except Exception as e:
            raise ValueError(f"'{self.PAGE}' or '{self.SIZE}' must be int")

        if page * size > max_total:
            raise ValueError(
                f"page*size has to be less than max_total,page='{page}',size='{size}',max_total={max_total}"
            )
        if data.get(self.PAGESIZE):
            size = int(data.get(self.PAGESIZE))
        page = page if page < max_page else max_page
        size = size if size < max_size else max_size

        return page, size

    def get_sort(self, data, default_field=None, default_sort=None):
        item = data.get(self.SORT)
        field = default_field
        sort = default_sort
        assert (default_field and default_sort) or (
                (not default_field) and (not default_sort)
        ), f"default_field={default_field}, default_sort={default_sort}"
        if item:
            item = item.lower().strip().split(" ")
            if len(item) <= 1:
                raise ValueError(f"'{self.SORT}'  format like  'sort=field asc'")
            field = item[0]
            sort = item[-1].lower()
            if sort != self.ASC and sort != self.DESC:
                raise ValueError(f"'{self.SORT}' must be  '{self.ASC}'  or '{self.DESC}'")
        return field, sort
