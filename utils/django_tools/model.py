'''

模型扩展


'''



from collections import Iterable
from itertools import chain

from django.db import models
from django.db.models.fields.related_descriptors import create_reverse_many_to_one_manager
from django.db.utils import Error
from django.utils.datastructures import ImmutableList
from django.utils.translation import ugettext_lazy as _
from jsonfield.fields import JSONFieldBase



class ModelFieldMayNotDelete(Error):
    """ 模型字段不可以删除 """


def str_model(self):
    """ Django Model 打印方法
    使用方式为: __str__ = __repr__ = str_model
    """
    attr_dict = self.__dict__.copy()
    attr_dict.pop("_state")
    return "%s(%r)" % (self.__class__.__name__, attr_dict)


class ModelBase(models.Model):
    class Meta:
        abstract = True


class Model(ModelBase):
    """ 提供一个附加属性用来直接存取变化结构 """

    class Meta:
        abstract = True

    _other_attr = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._other_attr = {}

    def __setitem__(self, key, value):
        if hasattr(self, key):  # 如果赋值的键是本身有的
            setattr(self, key, value)  # 直接赋值
        else:
            self._other_attr[key] = value  # 否则添加到其他对象内

    def __delitem__(self, key):
        if key in self._other_attr:
            del self._other_attr[key]
        else:
            raise ModelFieldMayNotDelete(f'model - filed {key} may not delete.')

    def __getitem__(self, item):
        if item in self._other_attr:  # 有允许为空的字段
            return self._other_attr[item]
        return getattr(self, item)

    def setdefault(self, key, value):  # 如果字典值为None不可以覆盖
        """ 重载字典方法 """
        if key not in self._other_attr and not hasattr(self, key):  # 如果在附加属性内没发现或者在自带属性内没发现
            self._other_attr[key] = value  # 设置新的key
        if key in self._other_attr:  # 开始取出结果 如果是附加属性 直接取出
            return self._other_attr[key]
        return getattr(self, key)  # model自带属性取出

    def get(self, key, default=None):
        if key in self._other_attr:
            return self._other_attr[key]
        elif key in [field.name for field in self._meta.fields]:
            return getattr(self, key)
        return default


def get_set_values(instance, level=0, max_level=1):
    """
    print(hasattr(instance_or_list.filter_set, "_apply_rel_filters"))
    # 是否是此文件下生成的 from django.db.models.fields.related_descriptors import create_reverse_many_to_one_manager
    print(hasattr(instance_or_list.filter_set, "_apply_rel_filters"))  # 是否是此文件下生成的RelatedManager类的一个方法来判定 from django.db.models.fields.related_descriptors import create_reverse_many_to_one_manager
    """
    level += 1
    set_objects = [(attr_name[:-4], getattr(instance, attr_name)) for attr_name in dir(instance) if attr_name.endswith("_set") and hasattr(getattr(instance, attr_name), "_apply_rel_filters")]  # 获得所有反外键
    for set_name, set in set_objects:  # 查询所有
        rows = set.all()
        setattr(instance, set_name, rows)
        for row in rows if level < max_level else []:  # 只进行几层的查询
            get_set_values(row, level, max_level)
    return instance


def _mtd(instance, fields=None, exclude=None):
    """ from django.forms.models import model_to_dict as _mtd """
    opts = instance._meta
    data = {}
    for f in chain(opts.concrete_fields, opts.private_fields, opts.many_to_many):
        if not getattr(f, 'editable', False):
            continue
        if fields and f.name not in fields:
            continue
        if exclude and f.name in exclude:
            continue
        if isinstance(f, JSONFieldBase):  # JSON 类型返回时不改为字符
            data[f.name] = getattr(instance, f.attname)
        else:
            data[f.name] = f.value_from_object(instance)
        if isinstance(f, models.ManyToManyField):
            data[f.name] = list(data[f.name])
    return data


def model_to_dict(instance, fields=(), exclude=()):
    """ 转换为字典 支持查询结果类型 字典类型 列表类型  XXX 后续支持多级字段去除(filters.id) """
    result = instance  # 原类型
    if isinstance(instance, dict):  # 字典类型
        for key, value in instance.items():
            if key not in exclude or key in fields:  # 去除字段
                instance[key] = model_to_dict(value, fields=fields, exclude=exclude)  # 回调更新
    elif isinstance(instance, (list, Iterable, models.QuerySet)) and not isinstance(instance, str):  # 除字符类型的任何可迭代对象包含生成器
        result = [model_to_dict(row, fields=fields, exclude=exclude) for row in instance]  # 回调更新
    elif isinstance(instance, models.Model):  # 直接更新
        result = _mtd(instance, fields=fields, exclude=exclude)
        if hasattr(instance, "_other_attr"):  # 附加属性添加到内容
            for key, value in instance._other_attr.items():
                if key not in exclude or key in fields:  # 去除字段
                    result[key] = model_to_dict(value, fields=fields, exclude=exclude)  # 回调更新
    return result


mtd = model_to_dict
