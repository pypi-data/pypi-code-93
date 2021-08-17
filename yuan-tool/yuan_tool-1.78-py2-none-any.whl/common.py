import string
import time
import re
import random
import copy
from colorama.ansi import code_to_chars
from .enums import PLACE, POST_HINT
from .difinition import DEFAULT_GET_POST_DELIMITER, DEFAULT_COOKIE_DELIMITER
from .crypto import bytes_decode, str2bytes


def check_keys(require_keys, request_keys):
    flag = True
    lost_key = None
    for key in require_keys:
        if not (key in request_keys.keys() and request_keys[key]):
            flag = False
            lost_key = key
    return flag, lost_key


def getattr_value(arr, key):
    return getattr(arr, key) if key in arr else ''


def transform_bytes_str(s: str):
    """将str型的bytes内容解码"""
    return bytes_decode(str2bytes(s))


def get_valid_filename(s):
    """
    Return the given string converted to a string that can be used for a clean filename.
    Stolen from Django I think
    """
    s = str(s).strip().replace(' ', '_')
    return re.sub(r'(?u)[^-\w.]', '', s)


def is_vars(keys, obj):
    '''
    判断对象中是否存在多个键值
    keys和obj必须都为集合
    return:
        success: Boolean 是否全部包含
        unhave: Dict    不存在keys的集合
    '''
    success = False
    try:
        result = keys.intersection(obj)
        unhave = keys - result
        dis = len(keys) - len(result)
        # 判断是否keys全部存在
        if dis == 0:
            success = True

        return success, unhave
    except AttributeError as e:
        print(e)


def format_name(name):
    name = re.sub('[\s\-]+', '_', name)

    return name.lower()


def qs_strr(s):
    data = {}
    if len(s) > 0:
        for key in s:
            data[key] = s[key][0]

    return data


# 初始化数据
def init_data(keys, value=None):
    v = {}
    for key in keys:
        v[key] = value

    return v


# 将json转化为字符串，\n分割
def json_to_warp_str(json):
    s = ''
    for key in json:
        s += f'{key}: {json[key]}\n'
    return s


# 数据过滤
def data_filter(data):
    data = re.sub(r'\s', '', data)

    return data


def list_to_dict(l):
    ''' list 转 dict类型 '''
    d = {i for i in l}
    return d


def paramToDict(parameters, place=PLACE.GET, hint=POST_HINT.NORMAL) -> dict:
    """
    Split the parameters into names and values, check if these parameters
    are within the testable parameters and return in a dictionary.
    """

    testableParameters = {}
    if place == PLACE.COOKIE:
        splitParams = parameters.split(DEFAULT_COOKIE_DELIMITER)
        for element in splitParams:
            parts = element.split("=")
            if len(parts) >= 2:
                testableParameters[parts[0]] = ''.join(parts[1:])
    elif place == PLACE.GET:
        splitParams = parameters.split(DEFAULT_GET_POST_DELIMITER)
        for element in splitParams:
            parts = element.split("=")
            if len(parts) >= 2:
                testableParameters[parts[0]] = ''.join(parts[1:])
    elif place == PLACE.POST:
        if hint == POST_HINT.NORMAL:
            splitParams = parameters.split(DEFAULT_GET_POST_DELIMITER)
            for element in splitParams:
                parts = element.split("=")
                if len(parts) >= 2:
                    testableParameters[parts[0]] = ''.join(parts[1:])
        elif hint == POST_HINT.ARRAY_LIKE:
            splitParams = parameters.split(DEFAULT_GET_POST_DELIMITER)
            for element in splitParams:
                parts = element.split("=")
                if len(parts) >= 2:
                    key = parts[0]
                    value = ''.join(parts[1:])
                    if '[' in key:
                        if key not in testableParameters:
                            testableParameters[key] = []
                        testableParameters[key].append(value)
                    else:
                        testableParameters[key] = value
    return testableParameters


def random_str(length=10, chars=string.ascii_lowercase):
    return ''.join(random.sample(chars, length))


def get_except_dic(d: dict, *arg):
    """
    将一个字典去除自定义的key值并返回字典
    :param d: 初始字典
    :param arg: 需要去除的key
    :return: 去除指定key后的字典（原字典中没有指定的key也不会报错）
    """
    c = set(d) - (set(d) - set(arg))
    for key in c:
        del d[key]
    return d


def get_middle_text(text, prefix, suffix, index=0):
    """
    获取中间文本的简单实现

    :param text:要获取的全文本
    :param prefix:要获取文本的前部分
    :param suffix:要获取文本的后半部分
    :param index:从哪个位置获取
    :return:
    """
    try:
        index_1 = text.index(prefix, index)
        index_2 = text.index(suffix, index_1 + len(prefix))
    except ValueError:
        # logger.log(CUSTOM_LOGGING.ERROR, "text not found pro:{} suffix:{}".format(prefix, suffix))
        return ''
    return text[index_1 + len(prefix):index_2]


def isListLike(value):
    """
    Returns True if the given value is a list-like instance

    >>> isListLike([1, 2, 3])
    True
    >>> isListLike('2')
    False
    """

    return isinstance(value, (list, tuple, set))


def findMultipartPostBoundary(post):
    """
    Finds value for a boundary parameter in given multipart POST body

    >>> findMultipartPostBoundary("-----------------------------9051914041544843365972754266\\nContent-Disposition: form-data; name=text\\n\\ndefault")
    '9051914041544843365972754266'
    """

    retVal = None

    done = set()
    candidates = []

    for match in re.finditer(r"(?m)^--(.+?)(--)?$", post or ""):
        _ = match.group(1).strip().strip('-')

        if _ in done:
            continue
        else:
            candidates.append((post.count(_), _))
            done.add(_)

    if candidates:
        candidates.sort(key=lambda _: _[0], reverse=True)
        retVal = candidates[0][1]

    return retVal


def ltrim(text, left):
    num = len(left)
    if text[0:num] == left:
        return text[num:]
    return text


def random_colorama(text: str, length=4):
    '''
    在一段文本中随机加入colorama颜色
    :return:
    '''
    records = []
    start = -1
    end = -1
    index = 0
    colors = range(31, 38)
    w13scan = ()
    colornum = 5
    for char in text:
        if char.strip() == "":
            end = index
            if start >= 0 and end - start >= length:
                if text[start:end] == "w13scan":
                    w13scan = (start, end)
                else:
                    records.append(
                        (start, end)
                    )
            start = -1
            end = -1
        else:
            if start == -1 and end == -1:
                start = index
        index += 1
    if start > 0 and index - start >= length:
        records.append((start, index))
    length_records = len(records)
    if length_records < colornum:
        colornum = len(records)
    elif 3 * colornum < colornum:
        colornum = colornum + (length_records - 3 * colornum) // 2
    slice = random.sample(records, colornum)  # 从list中随机获取5个元素，作为一个片断返回
    slice2 = []
    for start, end in slice:
        _len = end - start
        rdint = random.randint(length, _len)
        # 根据rdint长度重新组织start,end
        rdint2 = _len - rdint
        if rdint != 0:
            rdint2 = random.randint(0, _len - rdint)
        new_start = rdint2 + start
        new_end = new_start + rdint
        slice2.append((new_start, new_end))
    slice2.append(w13scan)
    slice2.sort(key=lambda a: a[0])
    new_text = ""
    indent_start = 0
    indent_end = 0
    for start, end in slice2:
        indent_end = start
        new_text += text[indent_start:indent_end]
        color = random.choice(colors)
        new_text += code_to_chars(color) + text[start:end] + code_to_chars(39)
        indent_start = end
    new_text += text[indent_start:]
    return new_text


def updateJsonObjectFromStr(base_obj, update_str: str):
    assert (type(base_obj) in (list, dict))
    base_obj = copy.deepcopy(base_obj)
    # 存储上一个value是str的对象，为的是更新当前值之前，将上一个值还原
    last_obj = None
    # 如果last_obj是dict，则为字符串，如果是list，则为int，为的是last_obj[last_key]执行合法
    last_key = None
    last_value = None
    # 存储当前层的对象，只有list或者dict类型的对象，才会被添加进来
    curr_list = [base_obj]
    # 只要当前层还存在dict或list类型的对象，就会一直循环下去
    while len(curr_list) > 0:
        # 用于临时存储当前层的子层的list和dict对象，用来替换下一轮的当前层
        tmp_list = []
        for obj in curr_list:
            # 对于字典的情况
            if type(obj) is dict:
                for k, v in obj.items():
                    # 如果不是list, dict, str类型，直接跳过
                    if type(v) not in (list, dict, str, int):
                        continue
                    # list, dict类型，直接存储，放到下一轮
                    if type(v) in (list, dict):
                        tmp_list.append(v)
                    # 字符串类型的处理
                    else:
                        # 如果上一个对象不是None的，先更新回上个对象的值
                        if last_obj is not None:
                            last_obj[last_key] = last_value
                        # 重新绑定上一个对象的信息
                        last_obj = obj
                        last_key, last_value = k, v
                        # 执行更新
                        obj[k] = update_str
                        # 生成器的形式，返回整个字典
                        yield base_obj

            # 列表类型和字典差不多
            elif type(obj) is list:
                for i in range(len(obj)):
                    # 为了和字典的逻辑统一，也写成k，v的形式，下面就和字典的逻辑一样了，可以把下面的逻辑抽象成函数
                    k, v = i, obj[i]
                    if type(v) not in (list, dict, str, int):
                        continue
                    if type(v) in (list, dict):
                        tmp_list.append(v)
                    else:
                        if last_obj is not None:
                            last_obj[last_key] = last_value
                        last_obj = obj
                        last_key, last_value = k, v
                        obj[k] = update_str
                        yield base_obj
        curr_list = tmp_list


def prepare_targets(targets):
    """
    对于逗号分隔的targets（ip或域名）
    从str型转为每个target以字典的key形式返回
    :param targets:
    :return:
    """
    if isinstance(targets, dict):
        return targets
    else:
        target_dict = {}
        keys = targets.split(',')
        for key in keys:
            d = {'status': 0, 'data': {}}
            target_dict.update({key: d})
        return target_dict


def current_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def timestamp():
    return time.time()


def contain(s1, s2):
    ''' 判断s2是否包含s1 '''
    is_contain = False
    row = re.findall(str(s1), s2)

    if len(row) > 0:
        is_contain = True

    return is_contain, row


def randomStr(dig=6):
    """
    生成随机字符串
    :param dig: 几个字符
    :return:
    """
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=k))


def randomInt(start=0, end=10):
    ''' 生成随机整数 '''

    return random.randint(start, end)


def clean(s):
    # Remove invalid characters
    s = re.sub('[^0-9a-zA-Z_]', '', s)
    # Remove leading characters until we find a letter or underscore
    s = re.sub('^[^a-zA-Z_]+', '', s)
    if s.isnumeric(): s = '_' + s
    return s


def compare_func2func(fun1, fun2, test_list=[], times=100, *arg, **kwarg):
    import time
    result = {}

    a = time.time()
    res1 = []
    for i in range(times):
        for example in test_list:
            res1.append(fun1(example, *arg, **kwarg))
    result['fun1_time'] = time.time() - a
    result['fun1_res'] = res1

    a = time.time()
    res2 = []
    for i in range(times):
        for example in test_list:
            res2.append(fun2(example, *arg, **kwarg))
    result['fun2_time'] = time.time() - a
    result['fun2_res'] = res2

    return result

def substr(s: str, start: int, end: int):
    return s[start: end]
