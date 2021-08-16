# -*- coding: utf-8 -*-
# @Time : 2020-06-08 10:50
# @Author : xzr
# @File : validators.py
# @Software: PyCharm
# @Contact : xzregg@gmail.com
# @Desc :


from django.core.validators import RegexValidator

from .translation import _

# 字母组合
LetterValidator = RegexValidator(r'^[a-z][\d\w_]+$', _('字母组合,符合^[a-z][\d\w_]+$'))

# Apk package Name
PageckageNameValidator = RegexValidator(r'^[a-z0-9\.]+$', _('包名,符合xx.xx.xx'))

PasswordValidator = RegexValidator(r'^(?![0-9]+$)(?![a-zA-Z]+$)[0-9A-Za-z@\-_\.#]{8,16}$',
                                   _('由数字和字母组成，并且要同时含有数字和字母，且长度要在8-16位之间'))
