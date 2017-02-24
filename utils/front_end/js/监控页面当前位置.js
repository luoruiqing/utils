$(window).scroll(function () {
    console.log($(this).scrollTop());
    if (($(".header.fixed").length > 0)) {
        if (($(this).scrollTop() > 0) && ($(window).width() > 767)) {
            $("body").addClass("fixed-header-on");
        } else {
            $("body").removeClass("fixed-header-on");
        }
    }
});