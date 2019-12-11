import re
from os import mkdir, makedirs

str = '<a href="https://www.meituri.com/t/1844/" target="_blank">西野七濑</a>'
reg = 'href="(\S+)"\s+target="_blank"\>'+'西野七濑'
result=re.findall(reg, str)
print(result)
dir = "images/" + "123" + "/" + "456"
#makedirs(dir)

def read_files():
    file_name = "46.txt"
    try:
        f = open(file_name, "r", encoding="utf-8")
        for line in f.readlines():
            line = line.strip('\n')
            print(line)

    finally:
        f.close()
albums=set()
albums.add("123")
albums.add("1233")
print(5//2)
#read_files()
# 打开一个文件
# f = open("46.txt", "w", encoding="utf-8")
#
# f.write("Python 是一个非常好的语言。\n是的，的确非常好!!")
#
# # 关闭打开的文件
# f.close()

#read_files()
record = "images/" + "大明/record.txt"  # 记录重复的文件夹，不再重复下载
fp = open(record, 'a+')  # 以二进制形式写文件
fp.close()
