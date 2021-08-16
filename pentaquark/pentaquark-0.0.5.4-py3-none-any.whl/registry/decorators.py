# from . import node_registry, RegistryConstants
#
#
# def register_node(name=None, if_exists=RegistryConstants.RAISE):
#     def wrapper(klass):
#         key = name or klass.get_label()
#         node_registry.add(
#             key,
#             klass,
#             if_exists=if_exists,
#         )
#         return klass
#     return wrapper
