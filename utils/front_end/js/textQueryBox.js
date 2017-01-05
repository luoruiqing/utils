/**
 * Created by luoruiqing-PC on 2016/5/25.
 * Dome:
 *  <input class="TQBox" type="text" />
 *  <ul>
 *      <li>111</li>
 *      <li style="Display:none;">222</li>
 *      <li>333</li>
 *  </ul>
 */
var TextQueryBox = {};
TextQueryBox.className = "TQBox";
TextQueryBox.defaultStyle = {
    "background-color": "white",
    "color": "gray",
    "list-style-type": "none",
    "list-style": "none"
};
TextQueryBox.initStyle = function (styleObject) {
    $("." + TextQueryBox.className).each(function () {
        var ul = $(this).nextAll("ul").first();
        ul.css(styleObject);
        ul.css({"display": "none", "z-index": 999, "position": "absolute"})
    })
};
TextQueryBox.init = function (style, jqueryObj) {
    TextQueryBox.initStyle(style || TextQueryBox.defaultStyle);
    TextQueryBox.reload(jqueryObj || $("." + TextQueryBox.className));
    TextQueryBox.initSelected();
};
TextQueryBox.length = $("." + TextQueryBox.className).length;
TextQueryBox.initSelected = function () {
    $("." + TextQueryBox.className).each(function () {
        $(this).nextAll("ul").first().find('li[data-selected="true"]:eq(0)').trigger("mouseover");
    });
};
TextQueryBox.reload = function (jqueryObj) {
    jqueryObj.each(function () {
        var box = $(this);
        var ul = $(this).next("ul").first();
        var lis = ul.find("li");
        box.focus(function () {
            ul.css("width", box.css("width"));
            ul.slideToggle("slow");
        });
        box.blur(function () {
            ul.slideToggle("slow");
        });

        box.keyup(function (e) {
            var hit;
            var keyValue = e.which;
            var ul = $(this).nextAll("ul").first();
            var lis = ul.find("li:visible");
            var selected = lis.filter('[data-selected="true"]:eq(0)');
            var first = false;
            if (selected.length == 0) {
                lis.eq(0).trigger("mouseover");
                selected = lis.filter('[data-selected="true"]:eq(0)');
                first = true;
            }
            //lis.trigger("mouseout");  .trigger("mouseover");
            if (keyValue == 38) {
                hit = selected.prevAll(":visible").first();
                if (hit.length == 0) {
                    hit = lis.eq(lis.length - 1)
                }
            }
            if (keyValue == 40) {
                hit = selected.nextAll(":visible").first();
                hit = first ? selected : hit;
                if (hit.length == 0) {
                    hit = lis.eq(0)
                }
            }
            if (keyValue == 13) {
                selected.trigger("click");
                box.trigger("blur");
            }
            hit ? hit.trigger("mouseover") : undefined
        });
        lis.each(function () {
            $(this).mouseover(function () {
                lis.trigger("mouseout");
                $(this).attr("data-selected", "true");
                $(this).css({"background-color": ul.css("color"), "color": ul.css("background-color")});
            });
            $(this).mouseout(function () {
                $(this).removeAttr("data-selected");
                $(this).css({"background-color": ul.css("background-color"), "color": ul.css("color")})
            });
            $(this).click(function () {
                console.log($(this));
                box.val($(this).text());
            })

        });

    })
};

TextQueryBox.init();
