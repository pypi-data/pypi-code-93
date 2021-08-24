import pymysql
from sqlalchemy import create_engine






def convert_lst_2_str_tuple(lst):
    changed_lst = []
    for i in lst:
        if isinstance(i, int):
            # 如果i是int型, 需要转成str才行
            i_ = str(i)
            changed_lst.append(i_)
        elif isinstance(i, str):
            # 如果i是str型, 需要在字符串外面多添加一个''
            i_ = "'{}'".format(i)
            changed_lst.append(i_)
    s = ",".join(changed_lst)
    return "(" + s + ")"








def main():
    # pass
    print(convert_lst_2_str_tuple([2, 3, "ss", 3, "mm"]))


if __name__ == '__main__':
    print("start test!")
    main()
    print("\n\n\neverything is ok!")
