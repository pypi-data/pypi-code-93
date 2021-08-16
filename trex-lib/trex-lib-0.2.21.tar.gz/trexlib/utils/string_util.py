'''
Created on Jul 3, 2012

@author: sglok
'''
import random, re, string, logging

WHITESPACE_PATTERN  = re.compile(r'\s')
DASH_PATTERN        = re.compile(r'-')

ALPHANUMERIC_CHARS  = string.ascii_lowercase + string.ascii_uppercase + string.digits
NUMERIC_CHARS       = string.digits

HUMAN_SAFE_ALPHANUMERIC_CHARS     = 'abcdefghijkmnpqrstuvwxyzABCDEFGHJKLMNPQRSTUVWXYZ123456789'


def random_string(number_character, is_human_mistake_safe=False):
    if is_human_mistake_safe:
        if number_character and type(number_character) is int and number_character>=0:
            return ''.join(random.sample(HUMAN_SAFE_ALPHANUMERIC_CHARS, number_character))
        else:
            return ''

    else:
        if number_character and type(number_character) is int and number_character>=0:
            return ''.join(random.sample(ALPHANUMERIC_CHARS, number_character))
        else:
            return ''

def random_number(number_character):
    if number_character and type(number_character) is int and number_character>=0:
        return ''.join([random.choice(NUMERIC_CHARS) for _ in range(number_character)])
    else:
        return ''

def is_ascii(s):
    return all(ord(c) < 128 for c in s)

def str_to_bool(value):
    if value:
        if "on"==value.lower() or "true"==value.lower() or "yes"==value.lower() or "y"==value.lower():
            return True
    return False
    
def remove_whitespace(value=None, replacement='_'):
    if value is not None and len(value.strip())>0:
        modified = re.sub(WHITESPACE_PATTERN, replacement, value)
        return modified
    else:
        raise ValueError('Illegal argument exception, where restaurant name is required.')

def remove_dash(value=None, replacement=''):
    if value is not None and len(value.strip())>0:
        modified = re.sub(DASH_PATTERN, replacement, value)
        return modified
    else:
        raise ValueError('Illegal argument exception, where restaurant name is required.')
    
def boolify(val, default=False):
    if (isinstance(val, str) and bool(val)):
        return not val in ('False', '0', 'false', 'no', 'No', 'n')
    else:
        if val:
            return bool(val)
        else:
            return default
    
def to_hex(value):
    res = ""
    for c in value:
        res += "%04X" % ord(c) #at least 2 hex digits, can be more
    return res
'''
#Not support in Python3
def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)
'''

def four_digit_escape(string):
    try:
        decoded_string = string.decode('utf-8')
        #return u''.join(char if 32 <= ord(char) <= 126 else u'%04x' % ord(char) for char in decoded_string)
        return u''.join(u'%04x' % ord(char) for char in decoded_string)
    except:
        #return u''.join(char if 32 <= ord(char) <= 126 else u'%04x' % ord(char) for char in string)
        return u''.join(u'%04x' % ord(char) for char in string)

def unicode_(msg):
    new_msg = []
    for char in msg:
        try:
            char = chr(int(char, 16))
        except ValueError:
            char = '?'
        new_msg.append(char)
    return ''.join(new_msg)

def is_match(regex, val):
    logging.debug('is_match')
    if val:
        if re.match(regex, val):
            return True
        return False
    else:
        return True

def random_int_str(range_from, range_to, zero_padding):
    from random import randint
    i = randint(range_from, range_to)
    if zero_padding:
        return str(i).zfill(zero_padding)
    else:
        return str(i)

def is_empty(value):
    if isinstance(value, str):
        if value is None or value.strip()=='' or value.strip()=='null' or value.strip()=='None':
            return True
        
    elif isinstance(value,(dict,list)):
        if len(value)==0:
            return True
          
    else:
        return value is None
    
    return False

def is_not_empty(value):
    return is_empty(value)==False

def truncate_if_max_length(value, max_length):
    if value:
        return value[:max_length]

def resolve_unicode_value(unicode_value):
    if unicode_value:
        unicode_value = unicode_value.decode('utf-8')
        return unicode_value
    else:
        return unicode_value


def base64Encode(value):
    import base64
    return base64.b64encode(bytes(value, 'utf-8'))

def split_by_length(str_value, length):
    def _f(str_value, length):
        while str_value:
            yield str_value[:length]
            str_value = str_value[length:]
    return list(_f(str_value, length))
