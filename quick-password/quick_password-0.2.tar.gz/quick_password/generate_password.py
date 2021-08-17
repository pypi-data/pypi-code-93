# -*- coding=utf-8 -*-
import random


def set_password_str(attach_str):
    password_str = "abcdefghijklmnopqrstuvwxyz"
    password_str += password_str.upper()
    password_str += "1234567890"
    password_str += attach_str
    return password_str

def generate_password(password_len=8, attach_str=""):
    password_str = set_password_str(attach_str)
    password = "".join(random.choices(password_str, k=password_len))
    return password


if __name__ == "__main__":
    print(generate_password(16))
    print(generate_password(8, "!@#$%^&*()"))
