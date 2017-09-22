# coding:utf-8
from pymysql.cursors import DictCursor
from pymysql.connections import Connection
from types import StringTypes, IntType, LongType, FloatType

NumberTypes = (IntType, LongType, FloatType)


class TableStyle(object):
    """ 表格样式 """

    STYLE_TABLE = "style_flag"
    FORMULA_TABLE = "style_formula"
    CREATE_STYLE_TABLE = '''
    CREATE TABLE IF NOT EXISTS `{}` (
          `name` VARCHAR(255) NOT NULL COMMENT '颜色配置名称',
          `color` VARCHAR(255) DEFAULT NULL COMMENT '文字颜色',
          `transparent` int(2) DEFAULT 0 COMMENT '文字透明度 0-100 不透明-透明',
          `bg_color` VARCHAR(255) DEFAULT NULL COMMENT '背景颜色',
          `bg_transparent` int(2) DEFAULT 0 COMMENT '背景透明度 0-100 不透明-透明',
          `type_font` VARCHAR(255) DEFAULT NULL COMMENT '字体类型 例如:微软雅黑',
          `symbol` VARCHAR(255) DEFAULT NULL COMMENT '特殊字符或图片地址 //xxx/a.jpg 或符号 例:😁',
          `size` VARCHAR(255) DEFAULT NULL COMMENT '字体大小或图片大小 例如: 14px/14em/14*300',
          `position` ENUM('before', 'center', 'after') NOT NULL COMMENT '3种类型的配置:前中后插入图片内容',
          `type` ENUM('img', 'gif', 'font', 'other') DEFAULT 'font' COMMENT '类型: 图片或文字',
          `info` VARCHAR(255) DEFAULT NULL COMMENT '其他附加信息 代码支持等',
          `status` TINYINT(1) DEFAULT 1 COMMENT '是否启用: 0) 不启用 1）启用',
          `UPTIME` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '数据时间',
          PRIMARY KEY (`name`)
    ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT '标识信息';'''.format(STYLE_TABLE)
    CREATE_FORMULA_TABLE = '''
    CREATE TABLE IF NOT EXISTS `{}` (
          `name` VARCHAR(255) NOT NULL COMMENT '颜色配置名称',
          `flag_name` VARCHAR(255) DEFAULT NULL COMMENT '配置信息列表逗号分隔',
          `direction` ENUM('<', '<=', '==', '>=', '>') DEFAULT NULL COMMENT '前后偏移',
          `value` DECIMAL(64,2) DEFAULT NULL COMMENT '值',
          `order` INT(2)  DEFAULT 0 COMMENT '生效次序 次序高优先生效',
          `status` TINYINT(1) DEFAULT 1 COMMENT '是否启用: 0) 不启用 1）启用',
          `UPTIME` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP COMMENT '数据时间',
          PRIMARY KEY (`name`)
    ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=utf8 COMMENT '标识结构';'''.format(FORMULA_TABLE)

    # def __init__(self, *args, **kwargs):
    #     super(TableStyle, self).__init__(*args, **kwargs)
    #     self.current_cursor = self.cursor(DictCursor)
    QUERY_STYLE_TEMPLATE = "SELECT `name`, `color`, `transparent`, `bg_color`, `bg_transparent`, `type_font`, `symbol`," \
                           "`size`, `position`, `type`, `info` FROM `{}` WHERE `status` != 0 AND `name` = %s; ".format(
        STYLE_TABLE)

    def __init__(self, array, connect_kwargs=None):
        self.connect = Connection(**dict((connect_kwargs or {}), **{"charset": "utf8"}))
        self.cursor = self.connect.cursor(DictCursor)
        self.cursor.execute(self.CREATE_STYLE_TABLE)
        self.cursor.execute(self.CREATE_FORMULA_TABLE)
        self.connect.commit()
        self.array = array

    @staticmethod
    def number(object):
        try:
            return float(object)
        except:
            try:
                return int(object)
            except:
                return object

    def get_style(self, *setting_names):
        new_rows = []
        self.cursor.execute("SELECT * FROM `{}`  WHERE `name` IN ({}) ORDER BY `order`".format(
            self.FORMULA_TABLE, ", ".join(["%s"] * len(setting_names))), setting_names)
        rows = self.cursor.fetchall()

        for x, row in enumerate(self.array):
            new_row = []

            for y, item in enumerate(row):
                item, style, item_style_name = self.number(item), {}, None
                if isinstance(item, NumberTypes):  # 数字类型
                    for row in rows:  # 遍历所有的匹配器
                        if eval("%s %s %s" % (item, row["direction"], row["value"])):  # 直接对比
                            item_style_name = row["flag_name"]
                elif isinstance(item, StringTypes):  # 字符类型  日期类型
                    pass
                if item_style_name:
                    print self.QUERY_STYLE_TEMPLATE
                    self.cursor.execute(self.QUERY_STYLE_TEMPLATE, item_style_name)  # 查询数据
                    style = self.cursor.fetchone() or {}
                new_row.append(style)

            new_rows.append(new_row)
        return new_rows

    def __del__(self):
        self.cursor.close()
        if not self.connect.open:
            self.connect.close()


if __name__ == '__main__':
    from json import dumps

    print dumps(TableStyle([["日期", "消费客户数"],
                            ["2017-09-08", 1301],
                            ["2017-09-09", 1939],
                            ["2017-09-10", 1784],
                            ["2017-09-11", 1230],
                            ["2017-09-12", 1267],
                            ["2017-09-13", 1478],
                            ["2017-09-14", 1070],
                            ["2017-09-15", 1263],
                            ["2017-09-16", 1746],
                            ["2017-09-17", 1851],
                            ["2017-09-18", 1362],
                            # [
                            #     "2017-09-19",
                            #     1432
                            # ],
                            # [
                            #     "2017-09-20",
                            #     1626
                            # ],
                            # [
                            #     "2017-09-21",
                            #     938
                            # ]
                            ],
                           connect_kwargs=dict(host="127.0.0.1", port=3306, user="root", password="123456", db="test")
                           ).get_style("周报按系统-中", "周报按系统-低", "周报按系统-高"), indent=4)
