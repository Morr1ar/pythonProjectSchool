import sys, os
import threading

from assistant_project import Assistant

from func import *

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy import Config
from kivy.properties import ObjectProperty
from kivy.clock import Clock, mainthread


class MainWidget(FloatLayout):
    text_label = ObjectProperty()
    btn_start = ObjectProperty()
    btn_reminder = ObjectProperty()
    btn_contacts = ObjectProperty()
    btn_recipes = ObjectProperty()
    btn_instruction = ObjectProperty()
    #btn_bookmarks = ObjectProperty()
    btn_finish = ObjectProperty()
    scroll = ObjectProperty()
    win_size = 100
    assistant = Assistant()
    start = False

    stop = threading.Event()

    def start_second_thread(self):
        threading.Thread(target=self.on_press_button_start).start()

    def on_press_button_start(self):
        filename = 'instruction2.txt'
        self.text_label.text = text_wrap(filename, window_size=self.win_size)
        print(self.assistant.st)
        if not self.assistant.st or self.start == False:
            print(self.assistant.st)
            self.start = True
            threading.Thread(target=self.infinite_loop).start()

    @mainthread
    def on_press_button_finish(self):
        if self.assistant.st == True or self.start == True:
            self.assistant.quite()
            self.assistant.st = False
            self.start = False
        sys.exit(0)

    @mainthread
    def on_press_button_reminder(self):
        filename = 'reminder_list.txt'

        self.text_label.text = text_wrap(filename, window_size=self.win_size)

    @mainthread
    def on_press_button_contacts(self):
        filename = 'numbers_list.txt'

        self.text_label.text = text_wrap(filename, window_size=self.win_size)

    @mainthread
    def on_press_button_recipes(self):
        filename = 'recipes_list.txt'

        self.text_label.text = text_wrap(filename, window_size=self.win_size)

    @mainthread
    def on_press_button_instruction(self):
        filename = 'instruction.txt'

        self.text_label.text = text_wrap(filename, window_size=self.win_size)

    @mainthread
    def on_press_button_googlemarks(self):
        filename = 'bookmarks.txt'
        self.text_label.text = text_wrap(filename, window_size=self.win_size)

    def infinite_loop(self):
        self.assistant.start()


class MainApp(App):
    def on_stop(self):
        self.root.stop.set()

    def build(self):
        return MainWidget()





if __name__ == '__main__':
    Config.set("graphics", "resizable", 1)
    Config.set("graphics", "width", 1024)
    Config.set("graphics", "height", 800)
    control_files()
    #Assistant().parse_bookmarks()
    app = MainApp()
    app.run()