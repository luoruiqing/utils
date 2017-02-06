# coding:utf-8
from __future__ import unicode_literals  # 和文件扯上关系 最好都是用unicode编码
from json import loads, dumps
from os.path import isfile, exists, getsize


class Notepad(dict):
    """ 该类的初衷是为了管理已处理任务，为了适用于各种中断程序的状况，例如手动结束脚本，已经跑过的可以记录起来
    下次启动还能继续接着，记录少量的合适 特别量大的也不适合，存成json，并格式化。
    """

    # 基本实例使用字典 关于取交集 差集使用字典的key做set来做
    def __init__(self, filename):
        if exists(filename) and isfile(filename) and getsize(filename):  # 文件存在 是个文件 同时不是空文件
            self.file = open(filename, "a+")  # 读写模式
        else:
            self.file = open(filename, "w+")  # 新建模式
        self.update(loads(self.file.read() or "{}"))  # 更新进来
        super(Notepad, self).__init__()

    def __del__(self):
        """ 这可能是我用python以来踩过最大的坑了
            当执行 __del__方法时，在外部导入的json.dumps已经被清除了
            当你执行时候并不会很显式的看到错误内容，而是：
-（Exception TypeError: "'NoneType' object is not callable" in <bound method Notepad.__del__ of {}> ignored）
            这个错误信息简直误导到我怀疑人生了。。。
            如果是后导入dumps的话 在__del__内就不可用了
            想要看到bug 就修改文件上面的导入代码
            - from os.path import isfile, exists, getsize
            - from json import loads,dumps

        """
        self.file.seek(0)  # 指针移动到顶部
        self.file.truncate()  # 清空指针后面所有内容
        self.file.seek(0)  # 回到顶部
        self.file.write(dumps(self, indent=4))
        self.file.close()



if __name__ == '__main__':
    notepad = Notepad("test1.txt")
    print notepad
    notepad["task2"] = "ok"
    notepad["task3"] = "ok"
    notepad.update({"tasks": "over~"})
    print notepad
