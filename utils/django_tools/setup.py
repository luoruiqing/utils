import os
import sys


def setup():
    import django

    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))  # 把manage.py所在目录添加到系统目录
    os.environ['DJANGO_SETTINGS_MODULE'] = 'cube.settings'  # 设置setting文件

    django.setup()  # 初始化Django环境