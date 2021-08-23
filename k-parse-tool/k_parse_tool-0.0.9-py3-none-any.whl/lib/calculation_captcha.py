# encoding=utf-8
import array
import os

from PIL import Image
from paddleocr import PaddleOCR

OPERATE_LIST = ['+', 'x', 'X', '-', '—', '÷', ':']
ocr = PaddleOCR()


# 去除噪点
def del_point(img):
    pix = img.load()
    width = img.size[0]
    height = img.size[1]
    for x in range(width):
        for y in range(height):
            r, g, b = pix[x, y]
            # print(r, g, b)
            if r < 100:
                pix[x, y] = 0, 0, 0
            elif r > 100:
                pix[x, y] = 255, 255, 255
    return img


def ocr_scanner(img_path):
    ocr_result = ocr.ocr(img_path)
    ocr_result_tuples = ()
    # 9_12.png的ocr识别结果格式
    # 前四个list分别代表上下左右文本四个在原图中的二维定位点
    # 后边一个元组是识别出来的文本还有识别结果的概率。
    # [[[6.0, 6.0], [83.0, 6.0], [83.0, 27.0], [6.0, 27.0]], ('9+12=', 0.9818487)]
    for line in ocr_result:
        ocr_result_tuples = line[1]
    if len(ocr_result_tuples) <= 0:
        return None
    result = ocr_result_tuples[0]
    return result

# 数字识别
def data_ident(data_str):
    num = None
    if data_str == 'q':
        num = 9
    elif data_str == 'z' or data_str == 'Z':
        num = 2
    elif data_str == 'G':
        num = 6
    elif data_str in OPERATE_LIST:
        num = None
    else:
        try:
            num = int(data_str)
        except Exception as e:
            print("can't identify:" + data_str)
    return num


# 计算结果
def deal_img_str(img_str):
    # str_list = img_str.split(' ')
    # print(str_list)
    calculate_result = None
    char_array = array.array('u', img_str)
    first_num = 0
    last_num = 0
    operator_num = ''
    is_split = False
    for operate in char_array:
        index_num = data_ident(operate)
        if index_num is not None and not is_split:
            first_num = first_num * 10 + index_num
        elif index_num is None and not is_split:
            is_split = True
            operator_num = operate
        elif index_num is not None and is_split:
            last_num = last_num * 10 + index_num
        else:
            # = 三
            # index_num is None and is_split:
            break
    print(img_str,'--->',f'{first_num}{operator_num}{last_num}=')
    if operator_num == '+':
        calculate_result = first_num + last_num
    elif operator_num == '×' or operator_num == 'X':
        calculate_result = first_num * last_num
    elif operator_num == '÷' or operator_num == ':':
        calculate_result = first_num // last_num
    else:
        calculate_result = first_num - last_num
    return calculate_result


def get_calculate_result(img_str, temp_save_path):
    # 去除噪点,生成新的图片image_target_path
    im = Image.open(img_str)
    im = del_point(im)
    file = os.path.basename(img_str)
    image_target_path = '%s/%s' % (temp_save_path, file)
    im.save(image_target_path)
    # ocr识别生成后的图片中的字符
    captcha_content = ocr_scanner(image_target_path)
    if captcha_content is None:
        return -1
    res = deal_img_str(captcha_content)
    print(r'captcha calculate result :',res)
    if os.path.exists(image_target_path):
        os.remove(image_target_path)
    return res

if __name__ == "__main__":
    file_path = r"C:\Users\kland\Downloads\cap"
    temp_path = r'C:\Users\kland\Downloads\caps'
    file_name = os.path.join(file_path, '7_7.png')
    get_calculate_result(file_name, temp_path)
    for file in os.listdir(file_path):
        if file.endswith('.png') or file.endswith('.jpg'):
            file_name = os.path.join(file_path, file)
            get_calculate_result(file_name, temp_path)
    # 删除验证码
    print('end .............')
