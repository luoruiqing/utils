# coding:utf-8

try:
    from cPickle import *
except ImportError:
    from pickle import *

from os import path


class MyPickle:
    def __init__(self, filename=None, refresh_interval=30, setdefault=True):
        self.obj = None
        self.filename = filename
        self.setdefault = setdefault
        self.query_map = []
        self.save_time = 0
        self._file = None
        self._file_closed = True
        self.content = ""
        self.obj = None
        self.dumps = dumps
        self.get_file()

    def set(self, s):
        self.obj = s

    def get(self):
        if not self.obj:
            file = self.get_file()
            self.content = file.read()
            assert self.content
            self.obj = loads(self.content)
        return self.obj



    def get_file(self):
        if not self.setdefault and not self._file_closed:
            raise IOError("file not isexcet")
        if self._file_closed:
            tod = "r+" if path.exists(self.filename) else "w+"
            self._file = open(self.filename, tod)
            self._file_closed = False
        return self._file


if __name__ == '__main__':
    d = dict(name='Bob', age=20, score=88)
    obj = MyPickle("a.text")
    obj.set(d)
    print obj.lo
