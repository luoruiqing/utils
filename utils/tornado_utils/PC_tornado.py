# coding:utf-8
"""
    生产消费者模式的tornado定时任务
"""
from tornado.queues import Queue
from tornado.gen import coroutine
from abc import ABCMeta, abstractmethod
from tornado.ioloop import IOLoop, PeriodicCallback


class ProductionAndConsumptionTornado(object):
    __metaclass__ = ABCMeta

    def __init__(self, queue_maxsize=1024, production_interval=None, io_loop=None):
        """
        :param queue_maxsize_or_queue 队列的长度
        :param production_interval:  生产者工作间隔(毫秒),如果没有就会只执行一次
        :param io_loop: 使用哪一个io_loop实例
        """
        self.queue_maxsize = queue_maxsize  # 队列长度
        self.queue = Queue(maxsize=self.queue_maxsize)
        self.io_loop = io_loop or IOLoop.current()
        self.production_interval = production_interval

    @abstractmethod
    def producer(self):  # 子类实现
        raise NotImplementedError()

    @abstractmethod
    def consumer(self, item):  # 子类实现
        raise NotImplementedError()

    @coroutine
    def _consumer(self):
        while True:
            item = yield self.queue.get()
            try:
                yield self.consumer(item=item)
            finally:
                self.queue.task_done()  # 表明任务完成

    def start(self):
        self.io_loop.spawn_callback(self._consumer)  # 添加消费者回调 这里可以反复注册
        self.io_loop.add_callback(self.producer)  # 先执行一次
        if self.production_interval:  # 如果需要定时执行
            PeriodicCallback(self.producer, self.production_interval).start()  # 生产的定时任务


if __name__ == '__main__':
    class TornadoTest(ProductionAndConsumptionTornado):
        @coroutine
        def producer(self):
            for n in range(15):
                yield self.queue.put("Hello %s。" % n)

        @coroutine
        def consumer(self, item):
            print item


    TornadoTest(production_interval=500).start()
    IOLoop().current().start()
