# coding:utf-8
from uuid import uuid4
from datetime import datetime
from pymysql.connections import Connection


class ProcessLog(Connection):
    """ 管理日志刷新 
    with ProcessLog() as log:
        log.refresh(message="进度1")
        log.refresh(message="进度2")
        sleep(1000000) # 超时连接断开
        log.reload().refresh(message="结束任务中..")

    """
    INITIALIZATION = "INITIALIZATION"  # 初始化
    RUNNING = "RUNNING"  # 运行中
    ERROR = "ERROR"  # 错误
    DONE = "DONE"  # 完成
    PASS = "PASS"  # 忽略
    status = INITIALIZATION

    CREATE_TABLE_TEMPLATE = '''
    CREATE TABLE IF NOT EXISTS `_process_log` (
      `name` VARCHAR(255) NOT NULL COMMENT '过程名称',
      `status` VARCHAR(50) DEFAULT '无' COMMENT '任务状态',
      `start_time` DATETIME DEFAULT NULL COMMENT '任务开始时间',
      `end_time` DATETIME DEFAULT NULL COMMENT '任务结束时间',
      `message` VARCHAR(255) DEFAULT NULL COMMENT '实时信息反馈',
      `info` TEXT DEFAULT NULL COMMENT '附加信息',
      `UPTIME` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '数据时间',
      PRIMARY KEY (`name`)
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8 COMMENT '运行过程表';
    '''
    REFRESH_TEMPLATE = "UPDATE `_process_log` SET `status` =%s, `end_time`=%s, `message`=%s, `info`=%s WHERE `name` = %s; "

    def __init__(self, name=None, *args, **kwargs):  # 可以提前不同进程内创建日志
        self.name = name or uuid4()
        charset = kwargs.pop("charset", None) or "utf8"
        self.connect_object = kwargs.pop("connect_object", None)
        self.message = None
        super(self.__class__, self).__init__(charset=charset, *args, **kwargs)

    def _execute(self, *args, **kwargs):
        cur = self.cursor()
        cur.execute(*args, **kwargs)
        self.commit()
        cur.close()

    def reload(self):
        """ 不使用旧连接 直接刷新 """
        self.close()
        self.ping()
        self.refresh(status=self.PASS)
        return self

    def refresh(self, message=None, end_time=None, status=RUNNING, info=None):
        """ 每次刷新都是运行中 """
        self.message = message
        self._execute(self.REFRESH_TEMPLATE, (status, end_time, message, info, self.name))
        return self

    def __del__(self):
        self.close()

    def __enter__(self):
        self._execute(self.CREATE_TABLE_TEMPLATE)
        self._execute("REPLACE INTO `_process_log` (`name`, `status`, `start_time`) VALUES (%s, %s, %s); ",
                      (self.name, self.status, datetime.now()))
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.message = "{}: {}".format(exc_type.__name__, str(exc_val)) if exc_type else self.message
        self.refresh(message=self.message, end_time=datetime.now(), status=self.ERROR if exc_type else self.DONE)


if __name__ == '__main__':
    from time import sleep


    # pl.reload()
    #

    def test():
        with ProcessLog("测试", host="127.0.0.1", user="root", password="123456", database="test") as pl:
            print "运行中"
            pl.refresh(message="执行1")
            pl.close()
            print "正常"
            pl.reload() # TODO 这里没完成
            pl.refresh(message="执行2")


    test()
    print "释放了吗?"
