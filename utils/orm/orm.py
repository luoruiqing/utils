# coding:utf-8

from functools import partial
from copy import copy
from abc import ABCMeta, abstractmethod, abstractproperty


class CreateTable:
    def __init__(self, model_class):
        self.charset = getattr(model_class, "__charset__")
        self.engine = getattr(model_class, "__engine__")
        self.ain = getattr(model_class, "__auto_increment_number__")
        self.table_name = getattr(model_class, "__table__")
        self.table_comment = getattr(model_class, "__comment__") or ''
        self.model_attr = model_class

    def get_field_sql(self, item):
        name, field = item
        length = self.get_length(field)
        null = self.get_null(field)
        ain = self.get_auto_increment(field.autoincrement)
        pk = self.get_primary_key(field)
        unique = self.get_unique(field)
        comment = self.get_comment(field.comment)
        return " ".join(filter(bool, [name, field.type, length, null, ain, unique, pk, comment]))

    @staticmethod
    def get_length(field):
        return "(%s)" % field.length if field.length else  ""

    @staticmethod
    def get_null(field):
        return field.nullable and "DEFAULT NULL" or "NOT NULL"

    @staticmethod
    def get_primary_key(field):
        return field.primary_key and "PRIMARY KEY" or ""

    @staticmethod
    def get_unique(field, primary_key=False):
        return "UNIQUE" if not primary_key and field.unique else ""

    @staticmethod
    def get_auto_increment(autoincrement=False, start=None):
        if autoincrement:
            f = start and "=%s" % start or ""
            return "AUTO_INCREMENT" + f
        return ""

    @staticmethod
    def get_comment(comment):
        return "COMMENT \'%s\'" % comment if comment else ""

    @staticmethod
    def get_engine(engine=None):
        return engine and "ENGINE=%s" % engine or ""

    @property
    def sql(self):
        mps = getattr(self.model_attr, "__mappings__", {})
        fields = map(self.get_field_sql, sorted(mps.iteritems(), key=lambda item: item[1]._order))
        return "CREATE TABLE `%s` (\n%s\n) %s %s %s %s;" % (
            self.table_name, ",\n".join(fields),
            self.get_engine(self.engine),
            self.ain and self.get_auto_increment(True, start=self.ain),
            self.charset and "DEFAULT CHARSET=%s" % self.charset,
            self.get_comment(self.table_comment))


class Logic:  # 逻辑
    operator = None

    def __init__(self, contrast):
        self.contrast = contrast


class AND:
    operator = "AND"

    def __init__(self, contrast):
        self.contrast = contrast


class OR:  # 逻辑
    operator = "OR"

    def __init__(self, contrast):
        self.contrast = contrast


def create_contrast(symbols):
    def _wrapper(self, other):
        return Contrast(self, symbols, other)

    return _wrapper


class SQLObject():
    def __init__(self, sql, params, *args):
        self.sql = sql.replace("?", "%s")
        self.params = params
        self.args = args

    def commit(self):
        pass

    def __str__(self):
        return self.sql % self.params


class Contrast:
    """第一个直接返回比较对象 只能俩个对象比较 不可以(!) a < b < c  """

    def __init__(self, left, symbols, right):
        self.left = left
        self.symbols = symbols
        self.right = right


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

        self.contrast = []  # 比较对象
        self.symbols = []  # 比较运算符

        self._order = Field._order
        Field._order += 1

    __gt__ = create_contrast(">")  # 大于
    __ge__ = create_contrast(">=")  # 大于等于
    __lt__ = create_contrast("<")  # 小于
    __le__ = create_contrast("<=")  # 小于等于
    __eq__ = create_contrast("=")  # 等于 ==
    __ne__ = create_contrast("!=")  # 不等于

    @property
    def type_str(self):
        length = ("(%d)" % self.length) if self.length is not None else ""
        return self.type + length

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
    cache = {}  # 缓存常用查询

    def __new__(cls, name, bases, attr):
        if name in ("Model", "Join"):  # 元类的new方法是个循环方法 由上至下，每个含有或被继承的类都会执行
            return type.__new__(cls, name, bases, attr)  # 使用基类的new方法生产默认类
        cls.subclasses = getattr(cls, 'subclasses', {})

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

        # [attr.pop(k, None) for k in mappings.keys()]
        attr["__table__"] = attr.get("__table__") or name.lower()
        attr["__primary_key__"] = primary_key
        attr["__mappings__"] = mappings
        attr["__create__"] = classmethod(lambda cls: CreateTable(cls))
        cls.subclasses.setdefault(name, mappings)  # 收集绑定关系
        return type.__new__(cls, name, bases, attr)

    @classmethod
    def get_fieldname(cls, instance):
        r = cls.cache.get(instance)
        if not r:
            for name, attr in cls.subclasses.iteritems():
                for field_name, field_instance in attr.iteritems():
                    print instance, field_instance
                    # if instance is field_instance:
                    #     print instance,'<<<<<<<<<<<'


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

    def insert(self):
        (keys, values) = zip(*self.iteritems()) if self else ([], [])
        sql = "INSERT INFO %s (%s) VALUE (%s);" % (self.__table__, ",".join(keys), ",".join(["%s"] * len(keys)))
        return sql, values

    @classmethod
    def select(cls, *contrasts):  # 直接返回
        sql = "SELECT * FROM %s "
        if contrasts:
            sql += "WHERE "
            for c in contrasts:
                if isinstance(c, Contrast):
                    l, s, r = c.left, c.symbols, c.right
                    ModelMetaClass.get_fieldname(l)
                    # print ModelMetaClass.get_fieldname(c), "1"
                    # if isinstance(l, Field):
                    #     print l, '<<<<<<<<'
                    # print "@", arg.contrast  # 比较运算符
                    # print "@", arg.symbols  # 比较运算符
        print cls.__create__()

    @classmethod
    def filter_one(self):
        pass
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


# UserCompany(User.id == 15, Company.id == 1)  # 查询用户ID是15同时公司ID是1的记录


class DomeDB():
    pass


if __name__ == "__main__":
    pass
    # user = User(id=1)
    # print user, "<<<<<"
    # print user.id
    # print user.get("name")
    # print user.__sql__
    # print user
    print ModelMetaClass.subclasses, '<<<<<<<'
    print User(name="luoruiqing", age=22).insert()
    User.select(1 < User.id, User.age == 22)
    # User((name == "luoruiqing" & age == 15 or 1)).add()  # 插入一个对象
    # User.find(1 < User.id <= 5, User.age == 22)
    # print User(name="luoruiqing", age=15).add()
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
