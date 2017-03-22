# coding:utf-8

from inspect import getcallargs
from types import NoneType


def field_args(default=None, nullable=False, autoincrement=False, primary_key=False, comment='', ):
    """用来对应参数"""


class Field(object):
    _template = "<%s: %s %s - object at %s>"
    type = "FIELD"
    length = None

    def __init__(self, length=None, default=None, nullable=False, unique=False, autoincrement=False, primary_key=False,
                 comment=''):
        self.length = length or self.length  # 字段长度 可以是数组
        self.default = default  # 默认值
        self.nullable = nullable  # 是否允许为空
        self.autoincrement = autoincrement  # 是否是自增字段
        self.primary_key = primary_key  # 是否是主键
        self.comment = comment  # 备注
        self.unique = unique  # 是否约束唯一
        # UNIQUE (Id_P)

    @property
    def type_str(self):
        length = ("(%d)" % self.length) if self.length is not None else ""
        return self.type + length

    def __str__(self):
        pk, ai, uq = self.primary_key and "PK", self.autoincrement and "AI", self.unique and "QU"
        default = "DEFAULT(%s)" % (self.default or "null") if self.nullable or self.default else "NOT NULL"
        return self._template % (self.__class__.__name__, self.type_str, ",".join(
            filter(bool, [default, ai, uq, pk])), super(Field, self).__str__().split()[-1][:-1])


class Tinyint(Field):
    type = "TINYINT"


class Integet(Field):
    type = "INT"
    length = 11


class Varchar(Field):
    type = "VARCHAR"
    length = 255


class Text(Field):
    type = "TEXT"


class Bool(Field):
    type = "BOOL"


class DateTimeField(Field):
    type = "DATETIME"


# FLOAT

class Model(dict):
    __tablename__ = None


class User(Model):
    id = Integet(primary_key=True, autoincrement=True)
    name = Varchar(50, nullable=True)
    age = Integet(2)


if __name__ == '__main__':
    user = User(user=1)
    print user.id
    print user.name
    print user.age
