# coding:utf-8
from time import sleep
from itertools import count
from logging import getLogger
from traceback import format_exc
from pika import BlockingConnection, ConnectionParameters, PlainCredentials

logger = getLogger(__name__)


class CallbackError(Exception):
    pass


class MQ:
    def __init__(self, host, username, password, virtual_host="/",
                 routing_key=None, exchange=None, queue=None, timeout=10,
                 declare=True, interval=5, retry=3, port=5672):
        self.routing_key = routing_key
        self.exchange = exchange
        self.queue = queue
        self.declare = declare
        self.interval = interval
        self._default_channel = None
        for attempt in count(1):
            try:
                logger.debug("Connecting... %s:%d" % (host, port))
                self.conn = BlockingConnection(ConnectionParameters(
                    host, port, virtual_host,
                    PlainCredentials(username, password),
                    socket_timeout=timeout,
                ))
                break
            except:
                logger.error(format_exc())
                if retry > 0 and attempt == retry:
                    raise
                sleep(interval)

    @property
    def channel(self):
        if not self._default_channel:
            self._default_channel = self.conn.channel()
            if self.declare:
                logger.debug("Declaring... ")
                assert self.routing_key and self.exchange and self.queue, \
                    ValueError("Params : routing_key, exchange, queue")
                self._default_channel.queue_declare(
                    queue=self.queue, durable=True, exclusive=False,
                    auto_delete=False
                )
                self._default_channel.exchange_declare(
                    exchange=self.exchange, durable=True)
                self._default_channel.queue_bind(
                    queue=self.queue, exchange=self.exchange,
                    routing_key=self.routing_key
                )
        return self._default_channel

    def put(self, message, routing_key=None, exchange=None):
        logger.debug("Putting message... %s" % message)
        self.channel.basic_publish(
            routing_key=routing_key or self.routing_key,
            exchange=exchange or self.exchange,
            body=message
        )

    def get(self, queue=None, delete=True, block=True, interval=5):
        for index in count(1):
            logger.debug("Getting message%s..." % (
                (" try %d" % index) if index != 1 else ""))
            _, _, content = self.channel.basic_get(
                queue=queue or self.queue, no_ack=delete)
            if block and not content:
                logger.debug("Queue is empty. sleep 5s.")
                sleep(interval or self.interval)
                continue
            return content

    def get_ack(self, callback, queue=None, block=True, interval=5):
        assert callable(callback), CallbackError("Unsupported callback " + `callback`)
        for index in count(1):
            logger.debug("Getting message%s..." % (
                (" try %d" % index) if index != 1 else ""))
            method_sig, args, content = self.channel.basic_get(
                queue=queue or self.queue, no_ack=False)
            if block and not method_sig:
                logger.debug("Queue is empty. sleep 5s.")
                sleep(interval or self.interval)
                continue
            callback(content)
            self.channel.basic_ack(method_sig.delivery_tag)
            break

    def close(self):
        self.channel.close()
        self.conn.close()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()


def send_msg(msg, host, username, password, routing_key, exchange,
             virtual_host="/"):
    with MQ(host=host, username=username, password=password,
            routing_key=routing_key, exchange=exchange,
            virtual_host=virtual_host, declare=False, ) as channel:
        channel.put(msg)
    return True


def one_msg(host, username, password, queue, virtual_host="/", block=False):
    with MQ(host=host, username=username, password=password, queue=queue,
            virtual_host=virtual_host, declare=False, ) as channel:
        msg = channel.get(block=block)
    return msg


if __name__ == '__main__':
    def test(msg):
        print msg


    with MQ(host="localhost", username="root", password="123456798"
            , routing_key="python_test007", exchange="python_test007", queue="python_test007",
            declare=False, ) as channel:
        channel.put("test", )  # routing_key="python_test007", exchange="python_test007"
        while True:
            channel.get_ack(callback=test)  # queue="python_test007"
    if send_msg(msg="Test", host="localhost", username="root", password="123456798",
                routing_key="python_test007", exchange="python_test007"):
        print "ok"
