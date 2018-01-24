from collections import Iterable
from json import dumps, loads
from traceback import format_exc

# from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Model, QuerySet
from django.http import QueryDict
from django.http.response import HttpResponse, HttpResponseBase
from django_redis import get_redis_connection
from rest_framework.authentication import BasicAuthentication
# from rest_framework.exceptions import APIException
from rest_framework.response import Response
from rest_framework.views import APIView as RestFrameworkAPIView

from utils.base.authentication import WithoutCsrfValidationSessionAuthentication
from utils.base.model import mtd
from utils.error import ErrorCodeBase



class DjangoJsonResponseBase(HttpResponse):
    """ Django 原生response定制  """

    def __init__(self, data, ensure_ascii=False, **kwargs):
        try:
            content = dumps(data, ensure_ascii=ensure_ascii, cls=DjangoJSONEncoder)
        except Exception as err:
            content = '{0} can\'t be jsonlized, due to {1}'.format(data, err)

        super().__init__(
            content=content,
            content_type='application/json;charset=UTF-8',
            **kwargs,
        )


class ProcessAPIViewBase(object):
    '''  基础流程视图  类似优先级最低的中间件 '''

    def process_request(self, request, *args, **kwargs):
        """ 请求进来前 request对象 与 url过滤参数 """
        pass

    def process_response(self, response):
        """ 请求结束 """
        pass

    def process_exception(self, error, request, *args, **kwargs):
        """ 错误处理 """
        pass


class ProcessAPIView(ProcessAPIViewBase):
    ''' 流程视图 '''
    NONE_DICT = {}

    def process_request(self, request, *args, **kwargs):
        body = request.body
        # 只去除左侧空格 同时只检测一个字符  # 这里新建字典 以防代码内更新字典导致的多线程变量污染
        request.json = loads(body) if body and body.lstrip().startswith(b"{") else {}
        request.params = request.GET  # URL地址栏参数
        request.form = QueryDict(request.body).dict()  # 带有请求体的请求体内参数

    def process_response(self, response):
        if isinstance(response, ErrorCodeBase):  # 自定义错误返回
            raise response  # 交给 process_exception 处理
        elif isinstance(response, str):
            response = HttpResponse(response)  # 字符类型的返回
        elif not isinstance(response, HttpResponseBase):  # 如果不是响应对象
            if isinstance(response, (QuerySet, Model, Iterable)):  # 模型对象或者查询结果对象 转字典
                response = mtd(response)
            response = Response({
                "status": 200,
                'message': "完成",
                "description": "success",
                "data": response or self.NONE_DICT,  # 这里的引用会节省内存开销
            })  # 其他类型的返回
        return response

    def process_exception(self, error, request, *args, **kwargs):
        logger.error(format_exc())  # 输出错误信息
        if isinstance(error, ObjectDoesNotExist):  # 模型根据id get方法报错整体处理
            error_message = error.args[0]
            return Response({
                "status": 0,
                'message': f'{error_message.split(" ",1)[0]} 数据不存在.',
                "description": error_message,  # 错误信息
                "data": self.NONE_DICT,
            }, status=400)  # 默认400错误
        elif isinstance(error, (ErrorCodeBase, AssertionError)):  # 已知错误
            message = getattr(error, 'message', str(error) if isinstance(error, AssertionError) else '')
            if error.args and isinstance(error.args[0], ErrorCodeBase):  # 断言抛出的已知错误
                error = error.args[0]
            return Response({
                "status": getattr(error, 'code', 0),
                'message': message,
                "description": getattr(error, 'description', None) or message,
                "data": getattr(error, 'data', self.NONE_DICT),
            }, status=getattr(error, 'status', 400))  # 默认400错误

        if settings.DEBUG:  # 所有错误直接抛出
            raise error
        else:  # 线上不暴露错误 但依旧是JSON返回
            return Response({
                "status": 500,
                'message': '服务器错误.',
                "description": 'server error.',
                "data": self.NONE_DICT,
            }, status=500)  # 状态码为500


class APIView(RestFrameworkAPIView, ProcessAPIView):
    ''' 默认流程视图与 rest framework 视图'''
    authentication_classes = (WithoutCsrfValidationSessionAuthentication, BasicAuthentication)

    if not settings.DEBUG:
        @property
        def default_response_headers(self):
            headers = {}
            if len(self.renderer_classes) > 1:
                headers['Vary'] = 'Accept'
            return headers

    def dispatch(self, request, *args, **kwargs):
        """
        `.dispatch()` is pretty much the same as Django's regular dispatch,
        but with extra hooks for startup, finalize, and exception handling.
        """
        self.args = args
        self.kwargs = kwargs
        self.request = request = self.initialize_request(request, *args, **kwargs)
        self.headers = self.default_response_headers  # deprecate?

        try:
            self.initial(request, *args, **kwargs)

            # Get the appropriate handler method
            if request.method.lower() in self.http_method_names:
                handler = getattr(self, request.method.lower(),
                                  self.http_method_not_allowed)
            else:
                handler = self.http_method_not_allowed
            # **************************************************************************************

            try:
                response = self.process_request(request, *args, **kwargs)  # 从"请求前"获得响应
                if not response:  # 没有响应
                    response = handler(request, *args, **kwargs)  # 正常处理
                    response = self.process_response(response)  # 处理完成 处理结束响应
            except Exception as error:
                response = self.process_exception(error, request, *args, **kwargs)
                if not response:  # 如果错误处理依然没有响应
                    raise  # 抛出

                    # **************************************************************

        except Exception as exc:
            response = self.handle_exception(exc)

        self.response = self.finalize_response(request, response, *args, **kwargs)
        return self.response


MethodView = APIView


class AuthMethodViewBase(MethodView):
    """ 认证视图根  """

    def process_request(self, request, *args, **kwargs):
        # 记录所有认证视图的 接口访问量
        # InterfaceTrafficRecord(self.request).interface_traffic_save()
        pass


class AuthMethodView(AuthMethodViewBase):
    """ 本平台认证 """


class OtherAuthMethodView(AuthMethodViewBase):
    """ 其他平台认证 """

