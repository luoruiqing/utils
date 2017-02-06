# coding:utf-8

from uuid import uuid4
from time import sleep
from traceback import format_exc
from logging import getLogger, DEBUG
from abc import ABCMeta, abstractmethod
from pika.exceptions import ChannelClosed
from pika import PlainCredentials, BlockingConnection, ConnectionParameters

logger = getLogger()
logger.setLevel(DEBUG)

# getLogger('pika').setLevel(INFO)
get_uid = lambda: str(uuid4())


class ClosingContextManager(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def close(self):
        raise NotImplementedError()

    def __enter__(self):
        return self

    def __exit__(self, type, value, traceback):
        self.close()


class Message(str):
    def __new__(cls, string, *args, **kwargs):
        return str.__new__(cls, string)

    def __init__(self, string, channel, method_sig):
        """字符 管道 这条消息的信号"""
        self.string = string
        self.channel = channel
        self.method_sig = method_sig
        self.acked = False
        super(Message, self).__init__(string)

    def acknowledgement(self):
        logger.debug("Acknowledgement message: %s." % self)
        self.channel.basic_ack(self.method_sig.delivery_tag)
        self.acked = True

    def __del__(self):
        if not self.acked:
            logger.debug("Not acknowledgement message: %s." % self.string)

    ack = acknowledgement


class MessageQueueManager(ClosingContextManager):
    """
    为了更加灵活的配置和管理MQ队列 在rabbitMQ中 <键,路由,队列> 三点一线
     3个条件决定一个队列
     这个类在任何条件不满足时 直接创建相应的 <键,路由,队列> 否则在已经正常存取
     如果定义了临时属性 temporary 则会删除队列
    """

    # durable 持久是是否写硬盘 如果宕机 持久队列可以恢复 非持久不可恢复
    # auto_delete 自动删除 这里即便添加了自动删除参数 如果上次不是完整删除，本次连接也不可以删除
    # exchange_declare(exchange_type='direct') 指定路由类型

    def __init__(self, host, username, password, virtual_host="/", routing_key=None,
                 exchange=None, queue=None, port=5672, arguments=None, temporary=False, interval=5):
        self.host = host  # 主机
        self.port = int(port)  # 端口
        self.username = username  # 用户名
        self.password = password  # 密码
        self.routing_key = routing_key  # key
        self.exchange_name = exchange  # 路由
        self.queue_name = queue  # 队列
        self.virtual_host = virtual_host
        self.arguments = arguments  # 队列是键值对形式的参数
        self.interval = interval  # 重试间隔时间
        self.temporary = temporary  # 临时队列 偶尔会保留队列，但是过一段时间mq会自行删除
        self.surplus = None  # 剩余的个数
        self.connect()  # 第一次进入便是死循环

    def get(self):
        # no_ack 为 True 拉取消息后服务端直接删除不需要确认
        return self._get(no_ack=True)[2]

    def get_message(self):
        method_sig, _, body = self._get(no_ack=False)  # properties
        return Message(body, self.channel, method_sig)

    def send(self, message):
        logger.debug("Sending message %s..." % message)
        for retry in range(1, 4):
            try:
                self.channel.basic_publish(exchange=self.exchange_name, routing_key=self.routing_key, body=message)
            except Exception, e:
                logger.error(str(e))
                sleep(self.interval)
            else:
                return True
            finally:
                if retry >= 3:
                    raise e

    def connect(self, timeout=10, interval=5):
        while True:
            try:
                self.conn = BlockingConnection(ConnectionParameters(
                    host=self.host, port=self.port, virtual_host=self.virtual_host,
                    credentials=PlainCredentials(self.username, self.password),
                    socket_timeout=timeout,
                ))
                break
            except Exception:
                logger.error(format_exc())
                sleep(interval)

    def close(self):
        if self.temporary:  # 临时队列 删除
            # self.channel.queue_delete(self.queue)
            self.channel.exchange_delete(self.exchange_name)  # 必须删除路由
        self.conn.close()

    def _get(self, no_ack):
        # no_ack 为 True 拉取消息后服务端直接删除不需要确认
        logger.debug("Getting message...")
        while True:
            method_sig, properties, body = self.channel.basic_get(queue=self.queue_name, no_ack=no_ack)
            self.surplus = method_sig.message_count
            if body:
                return method_sig, properties, body
            else:
                logger.debug("Queue is empty. sleep 5s.")
                sleep(self.interval)

    @property
    def channel(self):
        if not hasattr(self, "_channel"):
            self._channel = channel = self.conn.channel()  # 建立通道
            if self.temporary:  # 是否使用临时队列
                self.queue = channel.queue_declare(exclusive=True, arguments=self.arguments)  # 声明临时队列
                self.queue_name = self.queue.method.queue  # 获得名称
                self.exchange_name = "temporary." + get_uid().replace("-", "")  # 随机的路由名称
                self.routing_key = get_uid().split("-", 1)[0]  # 随机的key

                e = None
                try:  # 路由不存在
                    self.exchange = channel.exchange_declare(self.exchange_name, passive=True)  # 临时队列
                except ChannelClosed as e:
                    logger.warning("Exchange '%s' not existent." % self.exchange_name)
                finally:
                    if e:
                        self._channel = channel = self.conn.channel(
                            channel_number=self._channel.channel_number)  # 重新开启刚刚的编号
                        logger.warning("Create exchange '%s'..." % self.exchange_name)
                        self.exchange = channel.exchange_declare(
                            self.exchange_name, durable=False, auto_delete=True)  # 临时队列
            else:
                self.queue = channel.queue_declare(queue=self.queue_name, durable=True, arguments=self.arguments)
                self.exchange = channel.exchange_declare(exchange=self.exchange, durable=True)
            # 绑定
            self.bind = channel.queue_bind(exchange=self.exchange_name, routing_key=self.routing_key,
                                           queue=self.queue_name)

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
    pass
