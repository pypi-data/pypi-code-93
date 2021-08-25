from string import Formatter
import sys



    

# def cry(template, **addl_locals):
#     previous_frame = sys._getframe(1)
#     globals_dict = globals()
#     locals_dict = {**previous_frame.f_locals, **addl_locals}
#     result = []
#     parts = Formatter().parse(template)
#     for literal_text, field_name, format_spec, conversion in parts:
#         if literal_text:
#             result.append(literal_text)
#         if not field_name:
#             continue
#         value = eval(field_name, globals_dict, locals_dict)
#         if conversion:
#             value = {'a': ascii, 'r': repr, 's': str}[conversion](value)
#         if format_spec:
#             value = format(value, format_spec)
#         result.append(f"({value})")
#     return ''.join(result)
# 
# 
