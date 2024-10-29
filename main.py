from tkinter import *
import traceback
root = Tk()
root.withdraw()
from kivy.resources import resource_add_path
from kivymd.app import MDApp
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivymd.uix.label import MDLabel
from kivymd.uix.button import MDFlatButton
import os, sys
from kivy.config import Config
from kivymd.uix.screenmanager import MDScreenManager
from screens.home import Home
from kivymd.uix.boxlayout import MDBoxLayout
from kivy.metrics import dp
from kivy.uix.screenmanager import FallOutTransition
from kivy.core.text import LabelBase, DEFAULT_FONT
import os
import sys
import platform
from kivy.uix.popup import Popup

# Disable multitouch emulation (red dot)
Config.set("input", "mouse", "mouse,disable_multitouch")


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and PyInstaller"""
    try:
        # PyInstaller creates a temporary folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class BM(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Create Bootable MacOS/Windows Installer"
        self.icon = resource_path("icon.ico")  # Path to your .ico file
        self.load_all_kv_files(resource_path("kv"))
        self.is_windows = platform.system() == "Windows"
        self.is_mac = platform.system() == "Darwin"
        self.exe_path = resource_path('exe')
        self.logs_file = 'error.log'
        self.sm = MDScreenManager(transition=FallOutTransition())

    def build(self):
        # Window.maximize()
        Window.size = (600, 800)
        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Indigo"
        if self.is_windows:
            import ctypes

            if not ctypes.windll.shell32.IsUserAnAdmin():
                self.require_admin_popup()
                return
        return self.sm

    def require_admin_popup(self):
        """
        Show a popup to notify the user that the app needs admin privileges.
        """
        popup = Popup(
            title="Run as Administrator Required",
            content=MDBoxLayout(
                MDLabel(
                    text="This app needs to run with admin privileges. Please close and Run as Administrator."
                ),
                MDFlatButton(
                    text="Close",
                    on_release=lambda x: sys.exit(),
                    size_hint=(0.5, None),
                    pos_hint={"center_x": 0.5, "center_y": 0.5},
                    padding=[5],
                    font_size=dp(20),
                    md_bg_color="red",
                ),
                orientation="vertical",
                padding=[20],
            ),
            size_hint=(0.7, 0.5),
            auto_dismiss=False,  # Prevent user from closing without action
        )
        popup.open()

    def robofont(self):
        return "RobotoMono-Regular"

    @mainthread
    def on_start(self):
        Clock.schedule_once(lambda x: self.generate_screen(), 0.2)

    @mainthread
    def generate_screen(self, screen_name="home", *args):
        from screens.bootcamp import Bootcamp
        self.sm.add_widget(Home(name="home"))
        if self.is_mac:
            from screens.mac import MAC
            from screens.win import WIN
            self.sm.add_widget(MAC(name="mac"))
            self.sm.add_widget(WIN(name="win"))
        elif self.is_windows:
            from screens.win_win import WIN_WIN            
            self.sm.add_widget(WIN_WIN(name="win_win"))
        self.sm.add_widget(Bootcamp(name="bootcamp"))
        self.sm.current = screen_name

    def goto(self, screen_name="home", direction="left"):
        if screen_name == "win":
            if self.is_windows:
                screen_name = "win_win"
        self.sm.current = screen_name
        self.sm.transition.direction = direction


if __name__ == "__main__":
    try:
        if hasattr(sys, "_MEIPASS"):
            resource_add_path(os.path.join(sys._MEIPASS))
        app = BM()
        # Use logging
        print("Application started")
        app.run()

    except Exception as e:
        # logger.exception('Error')

        """
        If the app encounters an error it automatically saves the
        error in a file called ERROR.log.
        You can use this for BugReport purposes.
        """
        print(traceback.format_exc())
        with open("error.log", "w") as error_file:
            error_file.write(f"{e}: \n{traceback.format_exc()}")
