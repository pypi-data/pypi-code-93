from wrap_enum import WrapEnum


# https://developers.google.com/protocol-buffers/docs/proto3
class Label(WrapEnum):
    OPTIONAL = 'optional'
    REQUIRED = 'required'
