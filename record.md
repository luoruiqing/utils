### & 记录一些比较偏门的问题 &

## VUE
### 绑定传递多个参数

##### 事件绑定 v-on
<code>
    &lt;component @event="handler('arg', arguments[0], arguments[1])"/&gt;
</code>

##### 属性绑定 :
<code>
    &lt;component :event="(a,b) => querySearch(filter, a, b)"/&gt;
</code>

## Python

