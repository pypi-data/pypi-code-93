
from sys import exit

from rostypes import (
    HEADER, UINT8, UINT16, UINT32, CHAR, TIME, STRING,
    compatible_types, possible_types
)


def main():
    assert HEADER.type_name == 'std_msgs/Header'
    assert HEADER.is_builtin
    assert not HEADER.is_primitive
    assert HEADER.is_message
    assert not HEADER.constants
    assert HEADER.fields == {'seq': UINT32, 'stamp': TIME, 'frame_id': STRING}
    assert HEADER.fields['seq'].is_number
    assert HEADER.fields['stamp'].is_time
    assert HEADER.fields['frame_id'].is_string

    assert compatible_types(UINT8, CHAR)
    assert compatible_types(UINT16, UINT8)

    assert UINT8 in possible_types(255)
    assert UINT8 not in possible_types(256)
    return 0

if __name__ == '__main__':
    exit(main())
