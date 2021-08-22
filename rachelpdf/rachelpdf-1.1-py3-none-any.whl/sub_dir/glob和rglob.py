from pathlib import Path
from zipfile import ZipFile
import glob


p=Path("ecommerce")

list1=[x for x in p.glob('*')]  #搜索主文件夹中的所有文件名和子文件夹名（主文件夹中有什么）
list2=[x for x in p.glob('*.*')]  #搜索主文件夹中所有的文件（只是文件，结果不包括子文件夹名）（主文件夹中有什么文件）
list3=[x for x in p.glob('*.py')]  #搜索主文件夹中所有的.py文件（主文件夹中有什么.py文件）
list4=[x for x in p.glob('**')]  #搜索主文件夹名和所有子文件夹名(包括子文件夹的子文件夹)（这个file有哪些主，子文件夹）
list5=[x for x in p.glob('**/*')]  #搜索所有子文件夹名,以及主文件夹和子文件夹中的所有文件(包括子文件夹的子文件夹)
list6=[x for x in p.rglob('*')]  #一样 （这个里面有什么）
list7=[x for x in p.rglob('*.*')]  #（这个里面有什么文件）
list8=[x for x in p.glob('**/*.py')]  #搜索所有主文件夹和子文件夹中的.py文件 (包括子文件夹的子文件夹)
list9=[x for x in p.rglob('*.py')]  #一样（这个里面有什么.py文件）
print(list5)
print(list6)
print(list7)