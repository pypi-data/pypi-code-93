import wrapt

#
# basic_excludes=(int,float,str,bool)
#
# def _wrap_make_out():
# 	@wrapt.decorator
# 	def wrapper(wrapped,instance,args,kwargs):
# 		return instance.make_out(wrapped(*args,**kwargs))
#
# 	return wrapper
#
# # noinspection PyAbstractClass
# class RecursiveProxy(wrapt.ObjectProxy):
# 	exclude=()
# 	wrap_only=()
#
# 	def __init__(self,wrapped,*setup_args,**setup_kwargs):
# 		super().__init__(wrapped)
# 		self._self_exclude=tuple({*basic_excludes,*self.exclude})
# 		self._self_wrap_only=tuple(self.wrap_only)
# 		self._proxy_setup(*setup_args,**setup_kwargs)
#
# 	def _proxy_setup(self,*args,**kwargs):
# 		pass
#
# 	def __call__(self,*args,**kwargs):
# 		return self.__make_out(self.__wrapped__.__call__(*args,**kwargs))
#
# 	def make_out(self,out):
# 		return out
#
# 	def inherit_out(self,out):
# 		return type(self)(out)
#
# 	@_wrap_make_out()
# 	def __make_out(self,out):
# 		if self._self_wrap_only:
# 			if isinstance(out,self._self_wrap_only):
# 				return self.inherit_out(out)
# 			else:
# 				return out
# 		elif isinstance(out,self._self_exclude):
# 			return out
# 		else:
# 			return self.inherit_out(out)
#
# 	def __getattr__(self,item):
# 		if item.startswith('_self_'):
# 			return super().__getattr__(item)
# 		else:
# 			return self.__make_out(getattr(self.__wrapped__,item))
#
# 	@property
# 	def the_obj(self):
# 		return self.__wrapped__
#
# 	def __reduce_ex__(self,protocol):
# 		args=(self.__wrapped__,)
# 		return type(self),args

basic_excludes = (int, float, str, bool)


def _wrap_make_out():
    @wrapt.decorator
    def wrapper(wrapped, instance, args, kwargs):
        return instance.make_out(wrapped(*args, **kwargs))
    
    return wrapper


def _new_obj_proxy(cls, args, kwargs):
    # logger.warning('_new_obj_proxy')
    # logger.debug('cls: %s',cls)
    # args,kwargs=args_kwargs
    # logger.debug('args: %s',args)
    # logger.debug('kwargs: %s',kwargs)
    "A function to map kwargs into cls.__new__"
    # return cls.__new__(cls,*args,**kwargs)
    return cls(*args, **kwargs)


# noinspection PyAbstractClass
class RecursiveProxy(wrapt.ObjectProxy):
    _exclude = ()
    _wrap_only = ()
    
    def __init__(self, wrapped, *setup_args, **setup_kwargs):
        super().__init__(wrapped)
        self._self_setup_args = setup_args
        self._self_setup_kwargs = setup_kwargs
        self._self_exclude = tuple({*basic_excludes, *self._exclude})
        self._self_wrap_only = tuple(self._wrap_only)
        self._proxy_setup(*setup_args, **setup_kwargs)
    
    def _proxy_setup(self, *args, **kwargs):
        pass
    
    def __call__(self, *args, **kwargs):
        return self._make_out(self.__wrapped__.__call__(*args, **kwargs))
    
    # def make_out(self,out):
    # 	return out
    
    def _make_out(self, out):
        if self._self_wrap_only:
            if isinstance(out, self._self_wrap_only):
                return type(self)(out, *self._self_setup_args, **self._self_setup_kwargs)
            else:
                return out
        elif isinstance(out, self._self_exclude):
            return out
        else:
            return type(self)(out, *self._self_setup_args, **self._self_setup_kwargs)
    
    def __getattr__(self, item):
        if item.startswith('_self_'):
            return super().__getattr__(item)
        else:
            return self._make_out(getattr(self.__wrapped__, item))
    
    @property
    def _class_(self):
        return type(self)
    
    @property
    def the_obj(self):
        return self.__wrapped__
    
    def __reduce_ex__(self, protocol):
        args = (self.__wrapped__, *self._self_setup_args)
        return _new_obj_proxy, (type(self), args, self._self_setup_kwargs)
    
    def __getitem__(self, item):
        return self._make_out(super().__getitem__(item))
