# coding:utf-8
from copy import copy
from kivy.app import App
from kivy.config import Config
from kivy.graphics import Color, Line
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex, get_hex_from_color
from kivy.uix.behaviors import ToggleButtonBehavior
from kivy.uix.togglebutton import ToggleButton


class RadioButton(ToggleButton):
    def _do_press(self):
        if self.state == 'normal':
            ToggleButtonBehavior._do_press(self)


# Label 的属性
# 'text', 'font_size', 'font_name', 'bold', 'italic',
# 'halign', 'valign', 'padding_x', 'padding_y',
# 'text_size', 'shorten', 'mipmap', 'markup',
# 'line_height', 'max_lines', 'strip', 'shorten_from',
# 'split_str', 'unicode_errors'


class CanvasWidget(Widget):  # 创建画布对象
    points_width = 2
    tools = ("circle")  # 所有工具
    current_color = get_color_from_hex('#2c3e50')

    def set_color(self, new_color=None):
        if new_color:
            self.current_color = new_color
        self.canvas.add(Color(*self.current_color))

    def on_touch_down(self, touch):  # 触摸时按下
        if Widget.on_touch_down(self, touch):  # 如果当前触摸点有别的插件
            return  # 直接返回 抛给上层
        with self.canvas:  # 如果没有别的插件 打开画布 # circle 圈子
            touch.ud['current_line'] = Line(
                # circle=(touch.x, touch.y, 15), width=2
                points=(touch.x, touch.y), width=self.points_width
            )  # 在xy轴 画一个圆圈，大小为15 宽度为2

    def on_touch_move(self, touch):
        if 'current_line' in touch.ud:
            touch.ud['current_line'].points += (
                touch.x, touch.y)

    def clear_canvas(self):
        not_clear = copy(self.children)  # copy不需要清除且实例化的部件
        self.clear_widgets()  # 清除部件
        self.canvas.clear()  # 清除画布上所有的样式（包含了子部件的样式）
        for widget in not_clear:
            self.add_widget(widget)
        self.set_color()


class PaintApp(App):
    def build(self):
        self.canvas_widget = CanvasWidget()
        self.canvas_widget.clear_canvas()
        return self.canvas_widget

    def canvas_widget(self):
        pass


if __name__ == '__main__':
    Config.set('graphics', 'width', '400')
    Config.set('graphics', 'height', '400')
    Config.set('input', 'mouse', 'mouse,disable_multitouch')

    from kivy.core.window import Window

    Window.clearcolor = get_color_from_hex('#FFFFFF')
    PaintApp().run()
