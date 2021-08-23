# bak_base.py

import base64


def encode(str1):
    message_bytes = str1.encode('utf-8')
    base64_bytes = base64.b64encode(message_bytes)
    return base64_bytes.decode('utf-8')


def decode(str1):
    base64_bytes = str1.encode('utf-8')
    message_bytes = base64.b64decode(base64_bytes)
    return message_bytes.decode('utf-8')


def encode_file(str_filename):
    f_in = open(str_filename, 'r')
    f_out = open(str_filename + '.base', 'w')
    str_encode = encode(f_in.read())
    f_out.write(str_encode)
    f_out.close()
    f_in.close()


def decode_file(str_filename):
    with open(str_filename, 'r') as f:
        str_result = decode(f.read())
    return str_result


if __name__ == '__main__':
    # encode_file('google_sheet_api.json')
    print(decode_file('google_sheet_api.base'))

