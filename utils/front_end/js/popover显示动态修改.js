error_info.each(function () {
    var el = $(this);
    var error_id = el.data('id');
    el.popover(
        {
            trigger: 'hover', //触发方式 鼠标
            html: true, // 为true的话，data-content里就能放html代码了
            content: '加载中...'//这里可以直接写字符串，也可以 是一个函数，该函数返回一个字符串；

        }
    ).hover(function () {
        dom = $(this).next().find("div.popover-content");
        $.ajax({
                url: "/error_crawler/err_info?id=" + error_id,
                success: function (response) {
                    var data = response.data;
                    var th = '', td = '';
                    for (var i in data) {
                        th += "<th>" + i + "</th>";
                        td += "<td>" + data[i] + "</td>";
                    }

                    dom.html("<table class='table'><tr>" + th + "</tr><tr>" + td + "</tr></table>")
                },
                error: function () {
                }
            }
        );
    });
    el.on('shown.bs.popover', function () {
        var popover_dom = $(this).next(); // popover元素
        var arrow = popover_dom.find("div[class=arrow]"); //popover箭头元素
        var popover_btn_y = $(this).offset().top + $(this).height(); // popover被触发元素的中线
        var arrow_border = parseInt(/(\d+)(?:px|)/.exec(arrow.css('border-width').split(" ")[0])[1]); // popover箭头小三角高度
        var popover_arrow_y = arrow.offset().top + arrow_border;
        popover_dom.css({"display": "table"});
        popover_dom.css({"top": popover_dom.offset().top + (popover_btn_y - popover_arrow_y)});
    })
});