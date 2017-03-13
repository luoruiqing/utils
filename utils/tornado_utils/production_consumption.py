# coding:utf-8
"""
    生产消费者模式的tornado定时任务
"""
from tornado.queues import Queue
from tornado.gen import coroutine
from tornado.ioloop import IOLoop
from logging import getLogger, DEBUG
from abc import ABCMeta, abstractmethod

logger = getLogger()
logger.setLevel(DEBUG)


class ProductionAndConsumptionTornado(object):
    __metaclass__ = ABCMeta

    def __init__(self, queue_maxsize=1024, headers=20):
        """
        :param queue_maxsize: 队列的长度
        :param leaders: 注册多少个循环回调
        """
        self.queue_maxsize = queue_maxsize
        self.queue = Queue(maxsize=self.queue_maxsize)
        self.headers = headers

    @abstractmethod
    def producer(self):  # 子类实现
        raise NotImplementedError()

    @abstractmethod
    def consumer(self, item):  # 子类实现
        raise NotImplementedError()

    @coroutine
    def _consumer(self, handler_number=None):
        logger.debug("%s start consumer." % handler_number)
        while True:
            item = yield self.queue.get()
            if item:
                try:
                    yield self.consumer(item)  # 同步执行 为了确认任务完成
                finally:
                    self.queue.task_done()  # 表明任务完成

    @coroutine
    def start(self):
        logger.debug("producer loading.")
        self.producer()
        logger.debug("consumer loading.")
        for headers in range(self.headers):
            self._consumer(headers)
        logger.debug("loaded")


if __name__ == '__main__':
    from time import time
    from tornado.httpclient import AsyncHTTPClient, HTTPError


    class TornadoTest(ProductionAndConsumptionTornado):
        @coroutine
        def producer(self):  # 请求N次百度
            global req_num
            for n in range(req_num):
                yield self.queue.put(["http://www.baidu.com", n])

        @coroutine
        def consumer(self, item):
            global timeout_number
            e, response = None, None
            try:
                response = yield AsyncHTTPClient().fetch(item[0], request_timeout=3)
                print item[1], response.code, "|"
            except HTTPError, e:
                print str(e)
            finally:
                if e or response:
                    if (e or response).code == 599:
                        yield self.queue.put(item)
                        timeout_number += 1


    start, timeout_number, req_num = time(), 0, 10000
    instance = IOLoop().current()
    instance.add_callback(TornadoTest(headers=100).start)
    instance.start()
    print "请求%d次百度共用时" % req_num, time() - start, "超时链接并重试数量", timeout_number
