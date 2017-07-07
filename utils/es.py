# coding:utf-8
"""
ElasticSearch 的请求body API
"""
from types import DictType
from abc import ABCMeta, abstractproperty


# Base =======================================================================
class ElasticSearchBase(object):
    """ 基类 """
    __metaclass__ = ABCMeta


class ElasticSearch(ElasticSearchBase):
    """ 实现类 """


class ElasticSearchFilter(dict, ElasticSearch):
    """ 过滤对象 """
    key = abstractproperty()
    __slots__ = ("key")


class ElasticSearchAggregation(dict, ElasticSearch):
    """ 普通字段聚合 """


class ElasticSearchBody(dict, ElasticSearchBase):
    """ body类 """


# filters =======================================================================

class Term(ElasticSearchFilter):
    key = "term"

    def __init__(self, name, value):
        super(Term, self).__init__()
        self[self.key] = {name: value}


class Match(ElasticSearchFilter):
    key = "match"


class Range(ElasticSearchFilter):
    key = "range"

    def __init__(self, name, date=False, format="yyyy-MM-dd HH:mm:ss||yyyy-MM-dd||yyyy/MM/dd||epoch_millis", **kwargs):
        super(Range, self).__init__()
        body = self.setdefault(self.key, {}).setdefault(name, {})
        for item in ("gte", "gt", "lte", "lt"):
            r = kwargs.get(item)
            if r:
                body[item] = kwargs.get(item)
        if "ae" in kwargs:
            self.clear()
            self["term"] = {name: kwargs.get("ae") or kwargs.get("value")}
        assert not isinstance(self.get(self.key), DictType) or body, "No specified range."

        if date:
            body.update({"type": "date", "format": format})


# aggs function =======================================================================
class AggregationFunction(ElasticSearchAggregation):
    """ 聚合函数对象 """
    functions = ("avg", "sum", "min", "max", "extended_stats", "cardinality", "percentiles", "percentile_ranks")

    def __init__(self, name, function, **values):
        assert function in self.functions, "Unsupported aggregate function."
        super(AggregationFunction, self).__init__()
        if function in ("avg", "sum", "min", "max", "extended_stats", "cardinality"):
            self.setdefault(function, {"filed": name})
        else:
            raise Exception("Unsupported aggregate function.")


AF = AggregationFunction

Sum = lambda name: AggregationFunction(name, function="sum")
Avg = lambda name: AggregationFunction(name, function="avg")
Min = lambda name: AggregationFunction(name, function="min")
Max = lambda name: AggregationFunction(name, function="max")
ExtendedStats = lambda name: AggregationFunction(name, function="extended_stats")
Cardinality = lambda name: AggregationFunction(name, function="cardinality")


# aggs =======================================================================

class Terms(ElasticSearchAggregation):
    key = "terms"
    __range_mapping = {True: "desc", False: "asc"}
    range = __range_mapping.values()

    def __init__(self, name, size=5, reverse=True):
        super(Terms, self).__init__()
        self.setdefault(self.key, {"field": name}).update({
            "size": int(size),
            "order": self.__range_mapping.get(reverse)
        })


class DateHistogram(ElasticSearchAggregation):
    """
    offset:"+6h" 可以设置偏移时间
    units_mappings = 
    """
    key = "date_histogram"
    units = ("y", "M", "w", "d", "h", "m", "s")

    def __init__(self, name, interval="1h", time_zone="Asia/Shanghai", offset=None,
                 min=None, max=None, min_doc_count=0):
        """
        :param name: 查询字段名称
        :param interval: 聚合间隔
        :param time_zone （"Asia/Shanghai","+6h"） 时区设置
        :param min: 只聚合一段时间内
        :param max: 只聚合一段时间内
        :param min_doc_count: 最小文档数量  0代表所有文档
        """

        super(DateHistogram, self).__init__()
        body = self.setdefault(self.key, {
            "filed": name,
            "interval": interval,  # 聚合间隔
            "time_zone": time_zone,  # 时区
        })
        if offset:
            body["offset"] = offset
        for key, item in {"max": max, "min": min}.items():
            if item:
                body.setdefault("extended_bounds", {})[key] = int(item)
        if min_doc_count:
            body["min_doc_count"] = min_doc_count


class Histogram(ElasticSearchAggregation):
    key = "histogram"

    def __init__(self, name, interval):
        super(Histogram, self).__init__()
        self.setdefault(self.key, {"field": name, interval: int(interval)})


# search =============================================================================

class Search(ElasticSearchBody):
    # body = QueryFiltered(query=Query(self.query), filter=Filter(Bool(must=filters)))
    # def __init__(self, index, type):
    #     super(Search, self).__init__()
    #     self.index = index
    #     self.type = type
    af_one = None
    afs = None

    def query(self, query="*", analyze_wildcard=True):
        self.setdefault("query", {}).setdefault("filtered", {}).setdefault("query", {}).setdefault(
            "query_string", {}).update({"query": query, "analyze_wildcard": analyze_wildcard, })
        return self

    def filter_bool(self, must=(), must_not=(), should=(), minimum_should_match="100%"):
        bool = self.setdefault("query", {}).setdefault("filtered", {}).setdefault("filter", {}).setdefault("bool", {})
        for key, wheres in {"must": must, "must_not": must_not, "should": should}.items():
            if isinstance(wheres, ElasticSearchFilter):
                wheres = [wheres]
            for where in wheres:
                bool.setdefault(key, []).append(where)
        if bool:
            bool["minimum_should_match"] = minimum_should_match
        return self

    def aggregation(self, aggname, agg):
        aggs = self.setdefault("aggs", {})

        if isinstance(agg, AggregationFunction):  # 是否是聚合函数类型
            self.afs = (self.afs or {})
            self.afs.update({aggname: agg})  # 保存所有聚合函数
            if aggs is self.afs or not aggs:  # 只存在聚合函数类型的时候
                self["aggs"] = self.afs  # 更新
            if not self.af_one:
                self.af_one = {aggname: agg}  # 保存每个普通聚合的第一个聚合函数 符合kibana的规则
        else:
            if aggs is self.afs:  # 第1次非聚合函数
                self["aggs"] = {aggname: dict({"aggs": self.afs}, **agg)}
            else:
                aggs = aggs.values()[0]  # 先取出第一层

                while not aggs.get("aggs") is self.afs:
                    aggs = filter(lambda v: "aggs" in v, aggs.get("aggs", {}).values())[0]

                aggs["aggs"] = dict({aggname: dict({"aggs": self.afs}, **agg)}, **self.af_one)
        return self

    def size(self, size=0):
        if size:
            self["size"] = size
        return self

    aggs = aggregation


if __name__ == '__main__':
    # 过滤
    s = Search().query("*").filter_bool(must=Range("adsf", gt=14, date=True), must_not=Term("666", "123"))
    # 聚合函数
    s.aggs(1, Sum("t1")).aggs(2, Avg("t2")).aggs(3, Avg("t3"))
    # 聚合字段
    s.aggs(4, Terms("2级分类")).aggs(5, Terms("3级分类")).aggs(6, Terms("4级分类")).aggs(7, Terms("5级分类"))
    from json import dumps

    print dumps(s.size(5), indent=4)
