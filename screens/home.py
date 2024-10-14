import time
from kivy.uix.screenmanager import Screen
from kivy.uix.image import Image
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.menu import MDDropdownMenu
from kivy.metrics import dp
from kivy.core.window import Window
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRectangleFlatButton
from kivy.clock import Clock, mainthread
from kivy.config import Config
import multitasking
from kivy.uix.screenmanager import Screen
from kivymd.uix.list import OneLineListItem, OneLineAvatarIconListItem
from kivy.properties import StringProperty

class Home(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
    def on_enter(self):
        self.ids.info.text = '''
###Requirements:
    - macOS 11 (Big Sur) or higher
    - A downloaded macOS installer in `.app` format. You can download macOS installers from the Mac App Store.
    - A USB drive or hard disk partition formatted as APFS or Mac OS Extended (Journaled) (for mac installer).
    - Homebrew installed, then install wimlib (brew install wimblib) for working with windows installer.
'''