# coding:utf-8
from os import walk
from types import ModuleType
from importlib import import_module
from os.path import join, split, splitext, abspath


def import_mapping_classes(root):
    """
    :param root: 
    :return:
     导入所有映射类，保证文件名称与 文件内的类名相同
    DemoTest DemoTest
    demo_test DemoTest
    Demo_test DemoTest
    """
    root = abspath(root)
    model_dir = split(root)[-1]

    for item in [join(sub_root, file) for sub_root, dirs, files in walk(root) for file in files]:
        if item.endswith(".py") and not item.endswith("__init__.py"):
            root_path, file = split(item)
            model_name = splitext(file)[0]
            pack_path = root_path.split(model_dir, 1)[1].replace("/", " ").replace(".", " ").split(" ")
            pack_path = ".".join(filter(bool, [model_dir] + pack_path + [model_name]))
            _class_name = "".join(map(lambda item: item.capitalize(), model_name.split("_")))
            module = import_module(pack_path)
            assert isinstance(module, ModuleType)
            yield pack_path, getattr(import_module(pack_path), _class_name)


if __name__ == '__main__':
    pass
