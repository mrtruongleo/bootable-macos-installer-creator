from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivy.uix.screenmanager import Screen


class Home(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()

    def on_enter(self):
        if self.app.is_mac:
            self.ids.info.text = """
###Requirements:
    - macOS 11 (Big Sur) or higher
    - A downloaded macOS installer in `.app` format. You can download macOS installers from the Mac App Store.
    - A USB drive or hard disk partition formatted as APFS or Mac OS Extended (Journaled) (for mac installer).
    - Homebrew installed, then install wimlib (brew install wimblib) for working with windows installer.
"""
