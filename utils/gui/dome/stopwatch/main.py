# coding:utf-8
from kivy.app import App
from time import strftime
from kivy.clock import Clock
from kivy.core.window import Window
from kivy.core.text import LabelBase
from kivy.utils import get_color_from_hex
from kivy.properties import ObjectProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.resources import resource_find
from utils.timer import get_week, WEEK_CN_NUMBER

print resource_find('Roboto-Regular.ttf')  # 查找文件

# LabelBase.register(
#     name='Roboto',
#     fn_regular='fonts/Roboto/Roboto-Regular.ttf',
#     fn_bold='fonts/Roboto/Roboto-Bold.ttf',
#     fn_italic='fonts/Roboto/Roboto-Italic.ttf',
#     fn_bolditalic='fonts/Roboto/Roboto-BoldItalic.ttf'
# )
LabelBase.register("fzltcxhjw", r"FZLTCXHJW.TTF")


class ClockApp(App):
    sw_seconds = 0
    sw_start = False

    def on_start(self):
        Clock.schedule_interval(self.update_time, 1)  # 更新时间秒 一秒60帧作为标准
        Clock.schedule_interval(self.refresh, 0)

    def update_time(self, nap):
        self.root.ids.time.text = strftime('[b]%H[/b]:%M:%S')

    def refresh(self, nap):
        self.sw_seconds += nap
        minutes, seconds = divmod(self.sw_seconds, 60)
        if self.sw_start:
            self.root.ids.stopwatch.text = (
                '%02d:%02d.[size=40]%02d[/size]' %
                (int(minutes), int(seconds),
                 int(seconds * 100 % 100)))

    def start_stop(self):
        text = "paused" if self.sw_start else 'Start'
        self.sw_start = not self.sw_start
        self.root.ids.start_stop.text = ('Stop' if self.sw_start else text)

    def reset(self):
        if not self.sw_start:
            self.root.ids.stopwatch.text = ('%02d:%02d.[size=40]%02d[/size]' % (0, 0, 0))
            self.root.ids.start_stop.text = 'Start'
        self.sw_seconds = 0


if __name__ == '__main__':
    Window.clearcolor = get_color_from_hex('#123456')
    ClockApp().run()
