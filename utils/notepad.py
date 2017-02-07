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
        if exists(filename) and isfile(filename) and getsize(filename):
            self.file = open(filename, "a+", 0)  # 读写模式
        else:
            self.file = open(filename, "w+", 0)  # 新建模式
        self.update(loads(self.file.read() or "{}"))  # 更新进来
        super(Notepad, self).__init__()

    def __setitem__(self, key, value):
        super(Notepad, self).__setitem__(key, value)
        self.refresh()

    def _refresh(self):
        self.file.seek(0)  # 指针移动到顶部
        self.file.truncate()  # 清空指针后面所有内容
        self.file.seek(0)  # 回到顶部
        self.file.write(dumps(self, indent=4))

    def refresh(self):
        try:
            self._refresh()
        except KeyboardInterrupt:
            self._refresh()
            self.file.close() # 关闭文件后 报错
            raise

    def __del__(self):
        self.file.close()


if __name__ == '__main__':
    notepad = Notepad("test.txt")

    from time import sleep, time

    for x in range(1000):
        notepad[x] = x
        print time()
        sleep(0.01) # 在win上一定要做一些事情 例如延时 不然不成功
