/**
 * Created by luoruiqing on 2017/6/26.
 */
function updateObject(old_object, new_object) {
    // 如果 val 被忽略
    for (var item in new_object) {
        if (typeof new_object[item] === "undefined") {
            // 删除属性
            delete old_object[item];
        }
        else {
            // 添加 或 修改
            old_object[item] = new_object[item];
        }
        return old_object;
    }
}