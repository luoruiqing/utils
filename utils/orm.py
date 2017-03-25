# coding:utf-8

from functools import partial

from abc import ABCMeta, abstractmethod, abstractproperty


def gen_create_table(model_attr):
    print dir(model_attr)
    charset = getattr(model_attr, "__charset__")
    engine = getattr(model_attr, "__engine__")
    ain = getattr(model_attr, "__auto_increment_number__")
    table_name = getattr(model_attr, "__table__")
    table_comment = getattr(model_attr, "__comment__") or ''

    def get_comment(comment=None):
        return "COMMENT \'%s\'" % comment if comment else "COMMENT \'\'"

    def get_fields(item):
        name, field = item
        length = "(%s)" % field.length if field.length else  ""
        null = field.nullable and "DEFAULT NULL" or "NOT NULL"
        ain = field.autoincrement and "AUTO_INCREMENT" or ""
        pk = field.primary_key and "PRIMARY KEY" or ""
        unique = "UNIQUE" if not pk and field.unique else ""
        comment = get_comment(field.comment)
        return " ".join(filter(bool, [name, field.type, length, null, ain, unique, pk, comment]))

    mps = getattr(model_attr, "__mappings__", {})
    fields = map(get_fields, sorted(mps.iteritems(), key=lambda item: item[1]._order))
    return "CREATE TABLE `%s` (\n%s\n) ENGINE=%s AUTO_INCREMENT=%d DEFAULT CHARSET=%s %s;" % (
        table_name, ",\n".join(fields), engine, ain, charset, get_comment(table_comment))


def contrast(symbols):
    def _wrapper(self, other):
        self.symbols.append(symbols)
        self.contrast.append(other)
        print self.symbols, self.contrast
        return self

    return _wrapper


class Field(object):
    _template = "<%s: %s %s - object at %s>"
    type = "FIELD"  # 默认字段
    length = None  # 默认长度
    desc = None  # 倒序
    ase = None  # 正序

    _order = 0  # 记录当前字段在MYSQL顺序

    def __init__(self, length=None, default=None, nullable=False, unique=False, autoincrement=False, primary_key=False,
                 comment=""):
        self.length = length or self.length  # 字段长度 可以是数组
        self.default = default  # 默认值
        self.nullable = nullable  # 是否允许为空
        self.autoincrement = autoincrement  # 是否是自增字段
        self.primary_key = primary_key  # 是否是主键
        self.comment = comment  # 备注
        self.unique = unique  # 是否约束唯一/去除重复

        self.contrast = []  # 比较运算符
        self.symbols = []

        self._order = Field._order
        Field._order += 1

    @property
    def type_str(self):
        length = ("(%d)" % self.length) if self.length is not None else ""
        return self.type + length

    # def __eq__(self, field):  # 全等于是连接表或者对比
    #     if isinstance(field, Field):
    #         return setattr(field, "left", self) or field
    #     return ("==", field)
    __gt__ = contrast(">")  # 大于
    __ge__ = contrast(">=")  # 大于等于
    __lt__ = contrast("<")  # 小于
    __le__ = contrast("<=")  # 小于等于
    __eq__ = contrast("=")  # 等于 ==
    __ne__ = contrast("!=")  # 不等于

    def __str__(self):
        pk, ai, uq = self.primary_key and "PK", self.autoincrement and "AI", self.unique and "QU"
        default = "DEFAULT(%s)" % (self.default or "null") if self.nullable or self.default else "NOT NULL"
        return self._template % (self.__class__.__name__, self.type_str, ",".join(
            filter(bool, [default, ai, uq, pk])), super(Field, self).__str__().split()[-1][:-1])


class Where(dict):  # mysql or条件
    """ where条件基类 """

    @abstractmethod
    def sql(self):
        """ SQL语句 """


class Tinyint(Field):
    type = "TINYINT"


class Integet(Field):
    type = "INT"


class Varchar(Field):
    type = "VARCHAR"
    length = 255


class Text(Field):
    type = "TEXT"


class Bool(Field):
    type = "BOOL"


class DateTimeField(Field):
    type = "DATETIME"


class ModelMetaClass(type):
    def __new__(cls, name, bases, attr):
        if name in ("Model", "Join"):  # 元类的new方法是个循环方法 由上至下，每个含有或被继承的类都会执行
            return type.__new__(cls, name, bases, attr)  # 使用基类的new方法生产默认类

        mappings = dict()
        primary_key = None
        for k, v in attr.iteritems():
            if isinstance(v, Field):
                if v.primary_key:
                    if primary_key:
                        raise TypeError("Cannot define more than 1 primary key in class: %s" % name)
                    primary_key = v
                    v.nullable = False
                    v.unique = False  # 兼容创建表
                mappings[k] = v
        # [attr.pop(k) for k in mappings.keys()]
        attr["__table__"] = attr.get("__table__") or name.lower()
        attr["__primary_key__"] = primary_key
        attr["__mappings__"] = mappings
        attr["__create__"] = classmethod(gen_create_table)
        return type.__new__(cls, name, bases, attr)


class Model(dict):  # TODO 应该添加更多特性
    __metaclass__ = ModelMetaClass  # new方法是用的将是指定元类的方法

    __table__ = None  # 表名
    __comment__ = None  # 表说明

    __charset__ = "utf8"  # 编码
    __engine__ = "InnoDB"  # 默认引擎使用 InnoDB
    __auto_increment_number__ = 1  # 自增起始位置

    def __getattr__(self, item):
        return self.get(item) or super(dict, self).__getattribute__(item)

    def __setattr__(self, key, value):
        self[key] = value

    # @classmethod
    # def find(cls):  # 未实例化可以直接查询 其他都无需实例化
    #     return "SELECT * FROM %s" % cls.__table__

    def add(self):
        (keys, values) = zip(*self.iteritems()) if self else ([], [])
        sql = "INSERT INFO %s (%s) VALUE (%s);" % (self.__table__, ",".join(keys), ",".join(["%s"] * len(keys)))
        return sql

    @classmethod
    def find(cls, *args, **kwargs):  # 直接返回
        where = ""
        for arg in args:
            print zip(*(arg.contrast, arg.symbols))
            # print "@", arg.contrast  # 比较运算符
            # print "@", arg.symbols  # 比较运算符
        print cls.__create__()
        # "" % arg.iteritems()
        # where +=

        # print args,kwargs
        # if isinstance(cls, Model):
        #     keys, values = zip(*cls.iteritems())
        # return "SELECT * FROM %s WHERE " + " AND ".join(["%s = ?" % k for k in keys]), values

        # def save(self):  # 保存后得到新的ID
        #     conn.commit()
        #     return cur.lastrowid
        #
        # @classmethod
        # def count(cls):  # 如果是实例，返回符合条件的条数 如果是类返回所有条数
        #     return


class Join(Model):
    def __init__(self, field):  # 至少俩个表相连
        join = [field]
        while field:
            field = getattr(field, "left", None)
            if not field:
                break
            join.insert(0, field)
        assert len(join) > 1


class User(Model):
    __charset__ = "unicode"
    id = Integet(primary_key=True, autoincrement=True, comment="自增ID,用户名称")
    name = Varchar(50, nullable=True)
    age = Integet(2, default=5)


class Company(Model):
    __table__ = "commpany"
    id = Integet(primary_key=True, autoincrement=True)


class D(Model):
    id = Integet(primary_key=True, autoincrement=True)


print User.id, Company.id, D.id


# UserCompany(User.id=15,Company.id=1) # 查询用户ID是15同时公司ID是1的记录

class DomeDB():
    pass


print 1 > Integet <= 5, "@@@@@@@@1"

if __name__ == "__main__":
    # user = User(id=1)
    # print user, "<<<<<"
    # print user.id
    # print user.get("name")
    # print user.__sql__
    # print user
    # User((name == "luoruiqing" & age == 15 or 1)).add()  # 插入一个对象
    User.find(1 < User.id <= 5, User.age == 22)
    print User(name="luoruiqing", age=15).add()
    # User(name="luoruiqing", age=15).setdefault(name="luoruiqing").commit()  # 设置一个默认对象 如果name=luoruiqing 不存在
    # User.setdefault(WHERE(name="luoruiqing"), User(name="luoruiqing", age=15))  # 设置一个默认对象 如果name=luoruiqing 不存在


    # User.find(name="luoruiqing").update(age=22)
    #
    # User.find(OR(name="luoruiqing", age=15))
    # print User(name="luoruiqing", age=22).first()
    # 出错自动回滚 并输出错误信息 嵌套事务 嵌套回滚
    # User(User.name > Company.id, age=22)
    # User 对象
    # User().save() 新建对象
    # User.find(name="luoruiqing")
    # User.count() # 记录条数
    # User().count()
    # User.find(name="luoruiqing")





    # job = Conn(....database="job")
    # User(name="luoruiqing", age=22) # 增
    # job.delete(User(name="luoruiqing")) # 删
    # job.update(User(name="luoruiqing"), age=21) # 改
    # job.User.find(name="luoruiqing") # 查
    # job.User.find(name="luoruiqing").join(Job.)


    # User.find(name="luoruiqing").update(age=22) # 查并改
    # User().update(age=22) # 查并插入
    # User(name="luoruiqing",age=22).add() # 写入
