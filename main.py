import time
from tkinter import *
import traceback
root = Tk()
root.withdraw()
from kivy.resources import resource_add_path
from kivymd.app import MDApp
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.core.text import LabelBase
import os, sys
import configparser
from kivy.config import Config
from kivymd.uix.screenmanager import MDScreenManager
from screens.home import Home
from screens.mac import MAC
from screens.win import WIN
from kivy.uix.screenmanager import FallOutTransition
import os
import sys
# Disable multitouch emulation (red dot)
Config.set('input', 'mouse', 'mouse,disable_multitouch')

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller """
    try:
        # PyInstaller creates a temporary folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)

# LabelBase.register(name='en', fn_regular=resource_path('static/noto.ttf'))

class BM(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.title = "Create Bootable MacOS/Windows Installer"
        #self.icon = resource_path('static/icon.ico')  # Path to your .ico file
        self.load_all_kv_files(resource_path('kv'))
        
        self.sm = MDScreenManager(transition=FallOutTransition())
    def build(self):   
        #Window.maximize()     
        Window.size=(600,800)
        self.theme_cls.material_style = 'M3'
        self.theme_cls.theme_style = 'Dark'
        self.theme_cls.primary_palette = "Indigo"        
        return self.sm
    def robofont(self):
        return 'RobotoMono-Regular'
    @mainthread    
    def on_start(self):
        Clock.schedule_once(lambda x: self.generate_screen(), 0.2)
    
    @mainthread
    def generate_screen(self,screen_name='home',*args):
        self.sm.add_widget(Home(name='home'))
        self.sm.add_widget(MAC(name='mac'))
        self.sm.add_widget(WIN(name='win'))
        self.sm.current = screen_name
    
    def goto(self,screen_name='home', direction="left"):
        self.sm.current = screen_name
        self.sm.transition.direction=direction
        
        
if __name__ == '__main__':
    try:
        if hasattr(sys, '_MEIPASS'):            
            resource_add_path(os.path.join(sys._MEIPASS))
        app = BM()
        # Use logging
        print("Application started")
        app.run()
        
    except Exception as e:
        #logger.exception('Error')
        
        """
        If the app encounters an error it automatically saves the
        error in a file called ERROR.log.
        You can use this for BugReport purposes.
        """
        print(traceback.format_exc())
        with open('error.log', "w") as error_file:
            error_file.write(f'{e}: \n{traceback.format_exc()}')
