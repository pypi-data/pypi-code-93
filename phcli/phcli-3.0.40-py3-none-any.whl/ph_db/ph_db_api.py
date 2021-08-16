import copy


class PhDBAPI(object):
    engine = None
    session = None

    def tables(self):
        """
        列出全部数据表
        :return:
        """
        return self.engine.table_names()

    def query(self, obj, **ext):
        """
        查询数据
        :param obj: 要查询的实例信息
        :param ext: 额外查询条件，如查询空值，如 name=None
        :return:
        """
        result = self.session.query(obj.__class__)
        for k, v in obj.__dict__.items():
            if k != '_sa_instance_state' and v:
                result = result.filter(getattr(obj.__class__, k) == v)
        for k, v in ext.items():
            result = result.filter(getattr(obj.__class__, k) == v)
        result = result.all()
        return result

    def insert(self, obj):
        """
        插入数据
        :return:
        """
        self.session.add(obj)
        self.session.flush()
        return obj

    def commit(self):
        self.session.commit()

    def delete(self, obj):
        result = self.query(obj)
        for r in result:
            self.session.delete(r)
        return result

    def update(self, obj, FK='id'):
        """
        更新数据
        :param obj: 要更新的实例信息
        :param FK: 主键
        :return:
        """
        tmp = copy.deepcopy(obj.__dict__)
        tmp.pop('_sa_instance_state', None)
        obj_id = tmp.pop(FK, None)

        # 如果没有要更新的元素，直接返回
        if not obj_id or not tmp:
            return obj

        result = self.session.query(obj.__class__).filter(getattr(obj.__class__, FK) == obj_id)
        result.update(tmp)
        return obj
