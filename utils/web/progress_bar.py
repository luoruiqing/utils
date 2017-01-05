# coding:utf-8
from sys import stdout
from collections import deque
from time import strftime, gmtime, time as now
from types import IntType, LongType, FloatType

NumberType = (IntType, LongType, FloatType)

Byte = 1  # 1B
Kilobyte = 1024 * Byte  # 1KB
Megabyte = 1024 * Kilobyte  # 1MB
Gigabyte = 1024 * Megabyte  # 1GB
Terabyte = 1024 * Gigabyte  # 1TB

DISK_CAPACITY_MAP = [(Byte, "B"), (Kilobyte, "KB"), (Megabyte, "MB"), (Gigabyte, "GB"), (Terabyte, "TB")]


def get_filesize(length):
    """ 根据文件长度获得标准写法 """
    company_tuple = filter(lambda (a, _): length >= a, DISK_CAPACITY_MAP)[-1]
    return "%.2f%s" % (length / (company_tuple[0] or 1), company_tuple[1])


class ProgressBar(object):
    formatter = r" %s [%-50s] %5.2f%% %6s/%s %s %s/s"
    format_time = staticmethod(lambda s: strftime('%H:%M:%S', gmtime(s) if s <= 86400 else "more days"))

    def __init__(self, size, title='', fill_symbol="#", formatter=None):
        self.title = title  # 标题
        self.size = float(abs(size))  # 内容长度
        self.size_str = get_filesize(self.size)  # 最大长度字符
        self.fill_symbol = fill_symbol  # 进度符号
        self.loaded_length = float()  # 已经加载的长度
        self.remaining_time = None  # 剩余时间
        self.second_download_speed = None  # 每秒下载速度
        self.millisecond_download_speed = None  # 每毫秒下载速度
        self.loaded_percentage = float()  # 已经下载的比例
        self.show_bar = ''  # 显示的进度条内容
        self.formatter = formatter or self.formatter
        self._average_speed_deque = deque([float()], maxlen=20)  # 平均速度队列
        self.start_time = now()  # 开始时间
        self._last_time = self.start_time * 1000 - 1

    def refresh(self, chunk):  # chunk可以是流内容 也可以是流大小 这个东西最好越小越好
        current = now() * 1000
        interval = float(current - self._last_time)
        if not isinstance(chunk, NumberType):
            chunk = len(chunk)
        self.loaded_length += chunk  # 累加已经下载量
        self.millisecond_download_speed = chunk / interval  # 本次块大小/ 间隔时间 = 每毫秒下载速度
        self.second_download_speed = speed = self.millisecond_download_speed * 1000

        self.remaining_time = int((self.size - self.loaded_length) / speed)

        self._average_speed_deque.append(speed)

        self.loaded_percentage = (self.loaded_length / self.size)
        show_loaded_percentage = self.loaded_percentage * 100
        self.show_bar = self.fill_symbol * int(show_loaded_percentage * 0.5)

        row = self.formatter % (
            self.title,  # 文件名
            self.show_bar, show_loaded_percentage,  # 下载进度条
            get_filesize(self.loaded_length),
            self.size_str,
            self.format_time(self.remaining_time), get_filesize(speed))
        stdout.write(row + "\r")  # + "\r"
        self._last_time = current

    @property
    def ave(self):  # 平均速度
        l = self._average_speed_deque
        return (sum(l) - max(l) - min(l)) / len(l)  # 均值

    @property
    def avestr(self):  # 平均速度字符串
        return get_filesize(self.ave)

    @property
    def consumed(self):  # 已经耗时
        return now() - self.start_time

    def done(self, _print=True):  # 下载完成的打印
        stdout.write("\nTotal size: %s\tConsumed time : %s\tAverage speed: %s/s." % (
            self.size_str, self.format_time(self.consumed), self.avestr))


if __name__ == '__main__':
    from itertools import count
    from time import sleep
    from random import randint

    content_length = 1024 * 256 * 15
    pb = ProgressBar(content_length, "doc.txt")
    for chunk in count(1024 * 256):
        r = randint(1, 4) * 0.1
        sleep(r)
        pb.refresh(chunk)

        if pb.loaded_length >= content_length:
            break
    pb.done()
