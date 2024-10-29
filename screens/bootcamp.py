import os
import re
import subprocess
import time
from tkinter import filedialog
import traceback
from kivy.uix.screenmanager import Screen
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.clock import mainthread
import multitasking
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.list import MDList
from kivy.uix.screenmanager import Screen
from utils.components import ModelList
from utils.models import Models


class Bootcamp(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.model = "MacBookPro9,2"
        self.dialog = None
        self.save_to = "C:\\" if self.app.is_windows else "/Applications"
        self.process = None

    def on_enter(self):
        self.ids.model.text = self.model
        self.ids.save_to.text = self.save_to
        if self.app.is_mac:
            print("mac")
        elif self.app.is_windows:
            print("windows")

    def download(self):
        print(self.model)
        print(self.save_to)
        self.run()

    def set_model(self, model):
        print(model)
        if model is not None:
            self.model = model

    def dismiss(self):
        if self.dialog:
            self.dialog.dismiss()

    def on_select_model(self, ins):
        self.model = ins.model
        self.ids.model.text = ins.model
        self.dismiss()

    def select_model(self):
        print("select model")

        content = MDList(
            # size_hint_y=None,
            # height=dp(300),
            padding=[20, 0, 20, 0],
        )
        for m in Models:
            md = ModelList(
                model=m["model"], name=m["name"], size_hint_y=None, height=dp(20)
            )
            md.bind(on_release=lambda x: self.on_select_model(x))
            content.add_widget(md)
        # Wrap content in a scroll view
        scroll_view = MDScrollView(size_hint_y=None, height=dp(600))
        scroll_view.add_widget(content)

        self.dialog = MDDialog(
            title="Select Model",
            type="custom",
            content_cls=scroll_view,
            buttons=[
                MDRaisedButton(
                    text="CANCEL",
                    on_release=lambda x: self.dismiss(),
                )
            ],
        )
        self.dialog.open()

    def select_folder(self):
        """Set path based on the dialog selection."""
        selected_dir = filedialog.askdirectory()
        Window.raise_window()  # Bring Kivy window back to focus

        if selected_dir != "":
            self.save_to = selected_dir
            self.ids.save_to.text = selected_dir

    @mainthread
    def update_output_label(self, message):
        self.ids.output_label.text += f"{message}\n"
        print(message)

    @mainthread
    def update_progress(self, value):
        self.ids.progress_bar.value = value

    @mainthread
    def start_cmd(self):
        self.ids.spiner.active = True
        self.ids.download_btn.disabled = True

    @mainthread
    def stop_cmd(self):
        self.ids.spiner.active = False
        self.ids.download_btn.disabled = False

    def run(self):
        if self.model and self.save_to:
            self.main_execute()
        else:
            self.update_output_label("Please select model and target location.")

    def main_execute(self):
        self.start_cmd()
        # time.sleep(1)
        if self.app.is_windows:
            self.update_output_label("\nProcessing...")
            if not self.process:
                self.execute_command(
                    [
                        os.path.join(self.app.exe_path, "brigadier.exe"),
                        "-m",
                        f"{self.model}",
                        "-o",
                        f"{self.save_to}",
                    ]
                )
        else:
            self.update_output_label(
                "\nNot support this function on Mac devices yet! Using windows version please!"
            )
            self.stop_cmd()

    @multitasking.task
    def execute_command(self, command):
        downloading = None
        output_path = None
        try:
            # Debug output
            # self.update_output_label(f"Executing command: {' '.join(command)}")

            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Merge stderr into stdout
                universal_newlines=True,
                bufsize=1,
                shell=True,  # Try with shell=True to handle Windows paths better
            )

            # Read output in chunks

            while True:
                output = self.process.stdout.readline()
                if output == "" and self.process.poll() is not None:
                    break
                if output:
                    output = output.strip()

                    # Handle progress updates
                    if "%" in output:
                        if not downloading:
                            self.update_output_label("\nDownloading...")
                            downloading = True
                        match = re.search(r"(\d+\.?\d*)%", output.strip())
                        if match:
                            self.update_progress(float(match.group(1)))
                    else:
                        if "Using Mac model:" in output:
                            self.update_output_label(output.strip())
                        elif "Making directory" in output:
                            self.update_output_label(output.strip())
                            output_path = (
                                output.strip()
                                .split("Making directory ")[1]
                                .replace("..", "")
                            )
                        elif "Fetching Boot Camp product" in output:
                            self.update_output_label(output.strip())
                        elif "Extracting" in output:
                            self.update_output_label(output.strip())
                        elif "Done." in output:
                            self.update_output_label(output.strip())
                        print(f"{output}")  # Console debug output

        except Exception as e:
            self.update_output_label(f"Error: {e}")
            print(traceback.format_exc())
            with open(self.app.logs_file, "w") as error_file:
                error_file.write(f"{e}: \n{traceback.format_exc()}")
        finally:
            self.process = None
            self.stop_cmd()
            self.update_output_label("Process completed")
            if output_path:
                self.update_output_label(f"Output files located at: {output_path}")
