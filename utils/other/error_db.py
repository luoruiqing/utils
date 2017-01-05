# coding:utf-8
import pymysql
from sys import exc_info
from functools import wraps
from time import time as now
from socket import gethostname
from logging import getLogger, DEBUG
from DBUtils.PooledDB import PooledDB
from pymysql.cursors import DictCursor
from traceback import extract_tb, format_exc

from urlparse import urlparse

"""
/*
需要写入数据库的日志方法
*/

SET FOREIGN_KEY_CHECKS=0;
DROP DATABASE IF EXISTS error_record;
CREATE SCHEMA `error_record` DEFAULT CHARACTER SET utf8 ;
use error_record;
-- ----------------------------
-- Table structure for app_base
# exc_type, exc_reason, file_path, line, func_name, err_line_content
-- ----------------------------
DROP TABLE IF EXISTS `error_base`;
CREATE TABLE `error_base` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `exc_type` varchar(255) NOT NULL COMMENT '错误类型',
  `exc_reason` varchar(1024) NOT NULL COMMENT '错误原因',
  `file_path` varchar(255) NOT NULL COMMENT '错误文件地址',
  `line` INT(11) NOT NULL COMMENT '错误行数',
  `func_name` varchar(255) NOT NULL COMMENT '错误方法名',
  `err_line_content` VARCHAR(1024) NOT NULL COMMENT '错误行内容',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;
# ALTER TABLE errors ADD index plt_pname(platform,pack_name);

DROP TABLE IF EXISTS `consumer_error`;
CREATE TABLE `consumer_error` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `error_id` int(11) NOT NULL COMMENT '错误ID(error_base)',
  `host_name` varchar(255) NOT NULL COMMENT '机器名称',
  `domain` varchar(127) NOT NULL COMMENT '域名',
  `features` varchar(255) NOT NULL COMMENT 'url特征',
  `url` varchar(255) NOT NULL COMMENT '错误url',
  `wid` varchar(255) DEFAULT NULL COMMENT '错误wid',
  `cs_id` varchar(255) NOT NULL COMMENT '对应内容源',
  `queue` varchar(255) DEFAULT NULL COMMENT '队列名称',
  `time` int(11) NOT NULL COMMENT '错误时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

DROP TABLE IF EXISTS `producer_error`;
CREATE TABLE `producer_error` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `error_id` int(11) NOT NULL COMMENT '错误ID(error_base)',
  `host_name` varchar(255) NOT NULL COMMENT '机器名称',
  `domain` varchar(127) NOT NULL COMMENT '域名',
  `cs_type` varchar(2) DEFAULT NULL COMMENT '内容源类型',
  `regex` varchar(255) DEFAULT NULL COMMENT 'url对应的正则',
  `url` varchar(255) NOT NULL COMMENT '错误url',
  `time` int(11) NOT NULL COMMENT '错误时间',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8;

"""
logger = getLogger()
logger.setLevel(DEBUG)
POOL_DB = PooledDB(pymysql, host="127.0.0.1", user="root", password="123456", database='error_record')  # TODO 链接池参数


# url特征还是使用定时脚本 根据url分组 处理




class ErrorRecord:
    conn = None
    cur = None
    host_name = gethostname()

    def get_error_info(self):
        """获得错误信息 返回的信息依次为 错误类型，错误原因，错误文件路径，错误文件行号，错误方法名称，错误行的代码内容"""
        err_str = format_exc()
        if 'None' == err_str.strip() or err_str is None:  # 必须有报错
            raise Exception()
        exc_type, exc_reason, exc_tb = exc_info()
        file_path, line, func_name, err_line_content = extract_tb(exc_tb)[-1]
        return exc_type, exc_reason, file_path, line, func_name, err_line_content

    def get_error_id(self, *error_info):
        exc_type, exc_reason, file_path, line, func_name, err_line_content = error_info
        self.cur.execute("SELECT `id` FROM `error_base` WHERE `file_path` = %s AND `func_name` = %s AND "
                         "`err_line_content` = %s", (file_path, func_name, err_line_content))
        error_id = (self.cur.fetchall() or [{}, ])[0].get("id")

        if error_id is None:
            self.cur.execute("INSERT INTO `error_base` (`exc_type`, `exc_reason`, `file_path`, `line`, `func_name`, "
                             "`err_line_content`) VALUES (%s, %s, %s, %s, %s, %s );",
                             (str(exc_type), str(exc_reason), file_path, line, func_name, err_line_content))
            error_id = self.cur.lastrowid
            self.conn.commit()
        return error_id

    def write_consumer_info(self, error_id, domain, features, url, wid, cs_id, queue_name):
        self.cur.execute("SELECT 1 FROM `consumer_error` WHERE url = %s", url)
        if not self.cur.fetchall():
            self.cur.execute("INSERT INTO `consumer_error` (`error_id`, `host_name`, `domain`, `features`, `url`, "
                             "`wid`, `cs_id`, `queue`, `time`) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);",
                             (error_id, self.host_name, domain, features, url, wid, cs_id, queue_name, now()))
            consumer_error_id = self.cur.lastrowid
            self.conn.commit()
            return consumer_error_id

    get_url_path_features = staticmethod(lambda url: url[:url.rfind("/") + 1])
    get_url_domain = staticmethod(lambda url: urlparse(url).netloc)

    @conn_managers(POOL_DB)
    def record_consumer_error(self, url, wid=None, cs_id=None, queue_name=None, delete=False):
        try:
            if delete:  # 未报错则删除错误记录
                self.cur.execute("DELETE FROM `consumer_error` WHERE url = %s", url)
                self.conn.commit()
            else:  # 发生错误插入错误
                domain = self.get_url_domain(url)
                features = self.get_url_path_features(url)
                error_info = self.get_error_info()
                error_id = self.get_error_id(*error_info)
                self.write_consumer_info(error_id, domain, features, url, wid, cs_id, queue_name)
            return True
        except:
            logger.error(format_exc())
            return False

    @conn_managers(POOL_DB)
    def record_producer_error(self, url, delete=False):
        try:
            if delete:  # 未报错则删除错误记录
                self.cur.execute("DELETE FROM `producer_error` WHERE url = %s", url)
                self.conn.commit()
            else:  # 发生错误插入错误
                domain = self.get_url_domain(url)

                error_info = self.get_error_info()
                error_id = self.get_error_id(*error_info)
                self.write_consumer_info(error_id, domain, features, url, wid, cs_id, queue_name)
            return True
        except:
            logger.error(format_exc())
            return False


err_record = ErrorRecord()

if __name__ == '__main__':
    from logging import basicConfig

    basicConfig()


    def func1():
        for x in range(1):
            try:
                5 / 0
                1 + "s" + "111"
            except TypeError, e:
                pass
                # print err_record.record_consumer_error(
                #     "http://v.youku.com/v_show/id_XMTUwNTgwNTY2NA==.html",
                #     "sdafkldjsaflk", ";;;;;;;;;;;;;;;;;;;",
                #     "qudna")
                # print err_record.record_consumer_error("http://v.youku.com/v_show/id_XMTUwNTgwNTY2NA==.html",
                #
                #                                       delete=True)
            except ZeroDivisionError, e:
                pass
            finally:
                if e:
                    from traceback import print_exc
                    logger.error(123123123123123)
                    print_exc()
                    print err_record.record_producer_error("http://v.youku.com/v_show/id_XMTUwNTgwNTY2NA==.html")


    func1()
