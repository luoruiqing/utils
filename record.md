### & 记录一些常见或偏门的问题 &

### & Linux
#### ssh免密登录
```
ssh-copy-id username@remote-server
```
#### nginx文件夹软链
```
ln -s [目标目录] [代理目录] # ln -s /etc/nginx/conf.d/ ./nginx
```

### & JS
##### 基础类型操作库 [lodash] 简单处理JS的常用操作
```
_.isEmpty 判断对象是否为空
_.includes(collection, value, [fromIndex=0]) 值是否存在这个集合中 
_.keyBy(collection, [iteratee=_.identity]) 根据key列表转对象 _.keyBy(array, 'dir') -> {'dir':{}}
```
##### throw 链式调用的中断 
```
.then(_ => throw {})
```
#### & VUE
##### 绑定方法传递多个参数

##### 事件绑定 v-on
```
<component @event="handler('arg', arguments[0], arguments[1])"/>
```

##### 属性绑定 :
```
<component :event="handler('arg', arguments[0], arguments[1])"/>
```

##### $listeners - 代理组件的事件
```
<component v-on="$listeners"/>
```


### & Python
#### Pyenv 安装(一键)
```
curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash
```
#### Pyenv安装Python
```
# curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash
mkdir ~/.pyenv/cache # 创建缓存目录
yum install -y wget
image=http://mirrors.sohu.com/python # https://www.python.org
v=3.6.3
wget -P ~/.pyenv/cache/ $image/$v/Python-$v.tar.xz 
pyenv install $v
```
#### 库
```
import bisect # 二分法库

from itertools import product # 压平多层同时遍历 for x, y in product(xl, yl): ...
import wrapt # 装饰器简化方法
import pathlib # 路径操作的库

```
#### 三引号对齐问题
```
from textwrap import dedent
def test():
    # 这是个完整对齐的例子, 为了保证左侧对齐

    string = """Welcome, today's movie list:
- Jaw (1975)
- The Shining (1980)
- Saw (2004)"""

    # dedent 将会缩进掉整段文字最左边的空字符串
    string = dedent("""\
            Welcome, today's movie list:
            - Jaw (1975)
            - The Shining (1980)
            - Saw (2004)""")
```
#### 无穷
```
infinity = -float('inf')
Infinitesimal = float('-inf')
```

#### 块文件循环
```
from functools import partial
for chunk in iter(partial(file.read, block_size), ''):
    yield chunk
```
#### pandas的to_dict转字典
```
import pandas
# to_dict的orient参数 对应的结构如下
# records ->              [ {column: value}]     # 标准列表嵌套字典
# dict    ->              {column : {index : value}}
# list    ->              {column : [values]} 
# series  ->              {column : series(values)} 
# split   ->              {index : [index], columns : [columns], data : [values]} # pandas结构
# index   ->              {index : {column: value}}
pandas.read_csv('./test.csv').to_dict(orient='records')
```

### & Git
#### 增加一个远端
```
git remote rename origin old-origin # 更改现有远端名称
git remote add origin git remote add origin git@XXX.com:XXX.git # 增加远端地址
git push -u origin --all # 提交所有分支(本地有的)
git push -u origin --tags # 提交所有标签
```