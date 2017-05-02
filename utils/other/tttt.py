# -*- coding: utf-8 -*-
"""
    自动安装所有未安装的库，但是需要遍历所有代码，效率比较低
    在需要安装库的根目录下执行此文件即可
"""
from sys import path

s = """XSSAuditingEnabled	false
javascriptCanCloseWindows	true
javascriptCanOpenWindows	true
javascriptEnabled	true
loadImages	true
localToRemoteUrlAccessEnabled	false
userAgent	Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/538.1 (KHTML, like Gecko) PhantomJS/2.1.1 Safari/538.1
webSecurityEnabled	true"""
for x in s.splitlines():
    # print '"%s" : data.%s || %s,' % tuple([x.split("\t")[0].strip()] * 2)
    # print 'page.settings.%s = data.%s;' % tuple([x.split("\t")[0].strip()] * 2)
    print "%s: data.%s || %s," % tuple([x.split("\t")[0], x.split("\t")[0], x.split("\t")[1]])
exit()
from datetime import datetime

print datetime.now().strftime("%Y%m%d_%H%M")
exit()
import new
from re import compile
from os import walk, path, getcwd, popen
from sys import argv
from subprocess import Popen, PIPE

pack_name = compile(r"([\w\.,#]+)")
from_import_regex = compile("from\s+([\w_]+)")
import_regex = compile("import\s+([\w_]+)")
"pip freeze"
print getcwd()
project_path = argv[1] if len(argv) > 1 else getcwd()

files = [path.join(root, fn) for root, dirs, files in walk(project_path) for fn in files]
py_files = filter(lambda p: path.splitext(p)[1] == ".py", files)
# for x in py_files:
#     print x

for py_file in py_files:
    with open(py_file, "r") as python_file_object:
        import_list = []
        for row in python_file_object:
            import_row = []
            row = row.strip()
            if row.startswith("from ") or row.startswith("import "):
                import_row = [row]
                if "(" in row and ")" not in row:  # 圆括号导入
                    while 1:
                        next_row = next(python_file_object, '')
                        import_row.append(next_row)
                        if ")" in next_row:
                            break
                elif row.endswith("\\"):  # 续行符
                    while 1:
                        next_row = next(python_file_object, '')
                        import_row.append(next_row)
                        if not next_row.strip().endswith("\\"):
                            break

            if import_row:
                import_list.append(import_row)
        for x in import_list:
            print x
            # packs = set()
            # for import_row in import_list:
            #     import_code = "".join(filter(bool, [row.split("#", 1)[0].split("\\")[0].strip() for row in import_row]))
            #     import_code = import_code.replace("(", "").replace(")", "")
            #     if import_code.startswith("from") or import_code.startswith("import"):
            #         r = (from_import_regex.search(import_code) or import_regex.search(import_code)).group(1)
            #         packs.add(r)
            # # output = popen('pip install ')
            # for x in packs:
            #     print x
            # print output.read()


            # r =  or import_regex.search(import_code)
            # if r:
            #     print r.group(1)


            # [:min(import_code.find("."), import_code.find(" "))]
            # import_pack = import_code.split(" ", 1)[1].split(".")
            # if len(import_pack) == 1:
            #     import_pack[0].split(" ")
            # print "".join([row.split("#", 1)[0].split("\\")[0] for row in import_text])

            # print py_file, "|", row
#
#             # content = f.read()
#             # for regex in import_regex:
#             #     print regex.findall(content)
#             #
