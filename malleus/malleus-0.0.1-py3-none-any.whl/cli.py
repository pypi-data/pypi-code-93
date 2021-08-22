import sys
import argparse
import datetime
import re
import os
import base64
import random
from datetime import datetime

parser = argparse.ArgumentParser(description='Tool suite')
parser.add_argument('-b', '--base64', required=False,
        help='Base64 decoding; prompts for string', nargs='*')
parser.add_argument('-u', '--useragent', required=False,
        help='Generate a random UA string', nargs='*')
args = vars(parser.parse_args())

def b64_function():
    b64_d_string = input('Input string to decode:')
    output = base64.b64decode(b64_d_string)
    print(output)
    exit

def user_agents():
    ua_list = ['Mozilla/5.0 (iPhone; CPU iPhone OS 12_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12. Mobile/15E148 Safari/604.1','Mozilla/5.0 (iPhone; CPU iPhone OS 11_1_2 like Mac OS X) AppleWebKit/604.3.5 (KHTML, like Gecko) Version/11.0 Mobile/15B202 Safari/604.1','Mozilla/5.0 (Linux; Android 7.0) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Focus/1.0 Chrome/59.0.3029.83 Safari/537.36','Mozilla/5.0 (Linux; Android 7.0; SM-G930VC Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/58.0.3029.83 Mobile Safari/537.36','Mozilla/5.0 (Linux; Android 6.0.1; SM-G920V Build/MMB29K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.98 Mobile Safari/537.36']
    ua = random.choice(ua_list)
    print(ua)
    exit


def main():
    if args['base64'] is not None:
        b64_function()
    if args['useragent'] is not None:
        user_agents()
if __name__ == '__main__':
    main()
