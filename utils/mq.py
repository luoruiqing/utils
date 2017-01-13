# coding:utf-8

from uuid import uuid4
from time import sleep
from random import sample
from traceback import format_exc
from logging import getLogger, DEBUG
from abc import ABCMeta, abstractmethod
from pika.exceptions import ChannelClosed
from pika import PlainCredentials, BlockingConnection, ConnectionParameters

logger = getLogger()
logger.setLevel(DEBUG)

# getLogger('pika').setLevel(INFO)
get_uid = lambda: str(uuid4())


class MQError(Exception):
    pass


class ClosingContextManager(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def close(self):
        raise NotImplementedError()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()


def random_string(limit=16, base=(
        '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', ".",
        'a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm',
        'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z',
        'A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M',
        'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'X', 'Y', 'Z')):
    return "".join(sample(base, limit))


class Message(str):
    def __new__(cls, string, *args, **kwargs):
        return str.__new__(cls, string)

    def __init__(self, string, channel, method_sig):
        self.channel = channel
        self.method_sig = method_sig

    def ack(self):
        logger.info("acknowledgement message %s" % self)
        self.channel.basic_ack(self.method_sig.delivery_tag)

    acknowledgement = ack


class MessageQueueManager(ClosingContextManager):
    """
    为了更加灵活的配置和管理MQ队列 在rabbitMQ中 <键,路由,队列> 三点一线
     3个条件决定一个队列
     这个类在任何条件不满足时 直接创建相应的 <键,路由,队列> 否则在已经正常存取
     如果定义了零时属性 temporary 则会删除队列
    """

    # durable 持久是是否写硬盘 如果宕机 持久队列可以恢复 非持久不可恢复
    # auto_delete 自动删除 这里即便添加了自动删除参数 如果上次不是完整删除，本次连接也不可以删除
    # exchange_declare(exchange_type='direct') 指定路由类型

    def __init__(self, host, username, password, virtual_host="/", routing_key=None,
                 exchange=None, queue=None, port=5672, temporary=False, interval=5):
        self.host = host  # 主机
        self.port = int(port)  # 端口
        self.username = username  # 用户名
        self.password = password  # 密码
        self.routing_key = routing_key  # key
        self.exchange = exchange  # 路由
        self.queue = queue  # 队列
        self.virtual_host = virtual_host
        self._default_channel = None
        self.interval = interval
        self.connect()  # 第一次进入便是死循环
        self.temporary = temporary  # 临时队列 偶尔会保留队列，但是过一段时间mq会自行删除

    def get(self):
        # no_ack 为 True 拉取消息后服务端直接删除不需要确认
        return self._get(no_ack=True)[2]

    def _get(self, no_ack):
        # no_ack 为 True 拉取消息后服务端直接删除不需要确认
        logger.debug("Getting message...")
        while True:
            method_sig, properties, body = self.channel.basic_get(queue=self.queue, no_ack=no_ack)
            if not body:
                logger.debug("Queue is empty. sleep 5s.")
                sleep(self.interval)
            return method_sig, properties, body

    def get_message(self):
        method_sig, _, body = self._get(no_ack=False)  # properties
        return Message(body, self.channel, method_sig)

    def send(self, message):
        logger.debug("Sending message %s..." % message)
        while True:
            return self.channel.basic_publish(exchange=self.exchange, routing_key=self.routing_key, body=message)

    def connect(self, timeout=10, interval=5):
        while True:
            try:
                self.conn = BlockingConnection(ConnectionParameters(
                    host=self.host, port=self.port, virtual_host=self.virtual_host,
                    credentials=PlainCredentials(self.username, self.password),
                    socket_timeout=timeout,
                ))
                break
            except:
                logger.error(format_exc())
                sleep(interval)

    def close(self):
        if self.temporary:  # 临时队列 删除
            # self.channel.queue_delete(self.queue)
            self.channel.exchange_delete(self.exchange)  # 必须删除路由
        self.conn.close()

    @property
    def channel(self):
        if not hasattr(self, "_channel"):
            self._channel = channel = self.conn.channel()  # 建立通道
            if self.temporary:  # 是否使用临时队列
                self.queue = channel.queue_declare(exclusive=True).method.queue  # 声明临时队列 获得名称
                self.exchange = "temporary." + get_uid().replace("-", "")  # 随机的路由名称
                self.routing_key = get_uid().split("-", 1)[0]  # 随机的key

                e = None
                try:  # 路由不存在
                    channel.exchange_declare(self.exchange, passive=True)  # 临时队列
                except ChannelClosed as e:
                    logger.warning("Exchange '%s' not existent." % self.exchange)
                finally:
                    if e:
                        self._channel = channel = self.conn.channel(
                            channel_number=self._channel.channel_number)  # 重新开启刚刚的编号
                        logger.warning("Create exchange '%s'..." % self.exchange)
                        channel.exchange_declare(self.exchange, durable=False, auto_delete=True)  # 临时队列
            else:
                channel.queue_declare(queue=self.queue, durable=True)
                channel.exchange_declare(exchange=self.exchange, durable=True)
            # 绑定
            channel.queue_bind(exchange=self.exchange, routing_key=self.routing_key, queue=self.queue)
        return self._channel


def send_one_msg(host, username, password, exchange, routing_key=None, msg=None, callback=None, port=5672, timeout=5,
                 retry=3):
    assert msg
    from pika import PlainCredentials, BlockingConnection, ConnectionParameters
    for _ in range(retry):
        try:
            conn = BlockingConnection(ConnectionParameters(host, port, '/', PlainCredentials(username, password)))
            channel = conn.channel()
            channel.basic_publish(exchange=exchange, routing_key=routing_key, body=str(msg))
            channel.stop_consuming()
            conn.close()
            return True
        except:
            sleep(3)
    return False


MQ = MessageQueueManager

if __name__ == '__main__':
    from logging import basicConfig
