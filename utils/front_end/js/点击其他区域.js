my_dom = $("#my_dom");
my_selecter = "#my_selecter";
$(document).mouseup(function (e) { // 当元素在文档中任意一个节点放开鼠标按钮时
    if ($(e.target).parents(my_selecter).length === 0) { // 从当前按钮向上寻找元素，如果元素不存在
        my_dom.hide() // 指定一个元素隐藏
    }
});