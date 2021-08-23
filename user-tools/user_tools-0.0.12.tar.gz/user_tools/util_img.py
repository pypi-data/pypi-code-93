#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
# @File    : util_img.py
# @Time    : 2021-07-23
# @Author  : Skypekey


"""Some functions related to image operations."""
from pathlib import Path
from typing import Union
from user_tools import util_hashlib
from user_tools import util_check
from user_tools import util_file
import imghdr


# def rename_img(img_name: Union[str, Path]) -> str:
#     """Rename the picture and return the renamed name.\n
#         The picture name is changed to %Y%m%d%H%M%S_short_bit_md5.
#         Short_bit_md5 is the first five digits of the image file md5.
#         The first five digits of md5 are represented by numbers.
#         If they are letters,
#         they will be replaced by the positions in the alphabet.
#         Example: 20200226123612_23400.png

#     :param img_name(str): the path of image which to be renamed.\n
#     :return(str): The renamed name of img_name.\n
#         If the renamed name is empty, it may be the following:\n
#             not file; not exist; is null; file type not in IMG_SUFFIX.\n"""

#     real_name = ""
#     expr1 = util_check.file_or_dir(img_name) == "file"
#     expr2 = util_check.is_not_null(img_name)
#     if expr1 and expr2:
#         status = imghdr.what(imghdr)
#         if status:
#             md5_name_prefix = util_hashlib.get_file_md5(img_name)[:5]
#             time_str = util_file.get_file_mtime(
#                 img_name, format_str="%Y%m%d%H%M%S")
#         else:
#             str1 = f"util_img [note]: {Path(img_name).parent} "
#             str2 = f"file type not in {IMG_SUFFIX}"
#             print(str1 + str2)
#     return real_name


if __name__ == "__main__":
    pass
