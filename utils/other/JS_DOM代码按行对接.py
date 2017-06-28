# coding:utf-8

join = lambda s, delimiter="'": delimiter + "{} + \n{}".format(delimiter, delimiter).join(
    [item.strip() for item in s.splitlines() if item.strip()]) + delimiter
print join('''
<form class="index-number form-inline hidden">
                    <div class="form-group">
                        <label>聚合方法<input type="text" class="form-control"></label>
                    </div>
                </form>
''')
