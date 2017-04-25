# coding:utf-8
"""
    生产消费模型，且是固定数量的线程执行
"""
from Queue import Queue, Empty
from logging import getLogger, DEBUG
from abc import ABCMeta, abstractmethod
from threading import Thread, current_thread

logger = getLogger()
logger.setLevel(DEBUG)


class P2CThread:
    """
        1个生产者对应多个消费者
    """
    __metaclass__ = ABCMeta
    thread_num = 8
    queue_size = 256
    queue_timeout = 1

    @abstractmethod
    def producer(self, *args, **kwargs):
        raise NotImplementedError()

    def _producer(self):
        thread_name = current_thread().name
        logger.debug("%s producer start work." % thread_name)
        try:
            for item in self.producer() or []:
                logger.info("add %s to queue", str(item))
                self.queue.put(item)
        except:
            raise
        finally:
            self.producing = False
        logger.debug("%s producer end work." % thread_name)

    @abstractmethod
    def consumer(self, *args, **kwargs):
        raise NotImplementedError()

    def _consumer(self):
        thread_name = current_thread().name
        logger.debug("%s start consume." % thread_name)
        while self.producing or self.queue.qsize() > 0:
            try:
                item = self.queue.get(timeout=self.queue_timeout)
                logger.debug("%s start handle %s.", thread_name, str(item))
                self.consumer(item)
                logger.debug("%s end handle %s.", thread_name, str(item))
            except Empty:
                pass

    def start(self, thread_num=thread_num, queue_size=queue_size):
        self.queue = Queue(queue_size)
        self.threads = []
        Thread(target=self._producer).start()  # 启动一个生产者
        self.producing = True
        for consumer_number in range(thread_num or 1):  # 至少双线程
            t = Thread(target=self._consumer)
            self.threads.append(t)
            t.start()  # 启动多个消费者
        return self

    def join(self):
        for t in self.threads:
            t.join()
        logger.debug("End all work and quit.")

    def pause(self, status=True):
        raise NotImplementedError()


if __name__ == '__main__':

    class TestClass(P2CThread):
        full_sleep = 5

        @staticmethod
        def producer():
            for x in range(30):
                yield x

        @staticmethod
        def consumer(data):
            pass


    from logging import basicConfig

    basicConfig()
    TestClass().start(4).join()
