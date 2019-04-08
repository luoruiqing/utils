### & 记录一些比较偏门的问题 &

### VUE
#### 绑定方法传递多个参数

##### 事件绑定 v-on
<code>
    &lt;component @event="handler('arg', arguments[0], arguments[1])"/&gt;
</code>

##### 属性绑定 :
<code>
    &lt;component :event="(a,b) => handler(filter, a, b)"/&gt;
</code>

##### $listeners - 代理组件的事件
<code>
    &lt;component v-on="$listeners"/&gt;
</code>

### Python
<!-- #### 123 -->

### Linux
#### ssh免密登录
<code>
    ssh-copy-id username@remote-server
</code>
