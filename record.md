### & 记录一些比较偏门的问题 &

### Linux
#### ssh免密登录
```
    ssh-copy-id username@remote-server
```


### JS
##### 基础类型操作库 [lodash] 简单处理JS的常用操作
```
常用方法:
    isEmpty 判断对象是否为空
```
##### 链式调用的中断
```
.then(_ => throw {})
```
#### VUE
##### 绑定方法传递多个参数

##### 事件绑定 v-on
```
<component @event="handler('arg', arguments[0], arguments[1])"/>
```

##### 属性绑定 :
```
<component @event="handler('arg', arguments[0], arguments[1])"/>
```

##### $listeners - 代理组件的事件
```
<component v-on="$listeners"/>
```


### Python
#### Pyenv 安装(一键)
```
curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash
```
#### Pyenv安装Python
```
mkdir ~/.pyenv/cache # 创建缓存目录
yum install -y wget
image=http://mirrors.sohu.com/python # https://www.python.org
v=3.6.3
wget -P ~/.pyenv/cache/ $image/$v/Python-$v.tar.xz 
pyenv install $v
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

### Git
#### 增加一个远端
```
git remote rename origin old-origin # 更改现有远端名称
git remote add origin git remote add origin git@XXX.com:XXX.git # 增加远端地址
git push -u origin --all # 提交所有分支(本地有的)
git push -u origin --tags # 提交所有标签
```