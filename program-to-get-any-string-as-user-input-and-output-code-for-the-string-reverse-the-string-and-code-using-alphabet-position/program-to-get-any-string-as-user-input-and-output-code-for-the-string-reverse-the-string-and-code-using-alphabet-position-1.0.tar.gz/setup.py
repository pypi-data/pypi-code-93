#!/usr/bin/env python

from distutils.core import setup

setup(name='program-to-get-any-string-as-user-input-and-output-code-for-the-string-reverse-the-string-and-code-using-alphabet-position',
    version='1.0',
    description='Program to get any string as user input and output code for the string reverse the string and code using alphabet position',
    author='Nikita Strygin',
    author_email='nikita6@bk.ru',
    url='https://gitlab.com/DCNick3/program-to-get-any-string-as-user-input-and-output-code-for-the-string-reverse-the-string-and-code-using-alphabet-position',
    packages=['program_to_get_any_string_as_user_input_and_output_code_for_the_string_reverse_the_string_and_code_using_alphabet_position'],
    entry_points = {
        'console_scripts': ['program-to-get-any-string-as-user-input-and-output-code-for-the-string-reverse-the-string-and-code-using-alphabet-position=program_to_get_any_string_as_user_input_and_output_code_for_the_string_reverse_the_string_and_code_using_alphabet_position.main:main']
    }
)
