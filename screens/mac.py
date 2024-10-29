try:
    import pty
except:
    pass
import sys
import time, os
from tkinter import filedialog
from tkinter import *

root = Tk()
root.withdraw()
import multitasking
import subprocess
from kivymd.uix.scrollview import MDScrollView
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.spinner import MDSpinner
from kivy.metrics import dp
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.resources import resource_add_path
import traceback
from kivy.config import Config
from kivy.uix.screenmanager import Screen

# Disable multitouch emulation (red dot)


class MAC(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.output_label = None
        self.source_installer = "/Applications/Install macOS Sonoma.app"
        self.target_volume = "/Volumes/sonoma"
        self.command_thread = None
        self.dialog = None
        self.process = None
        self.password_prompt_shown = False

    def robofont(self):
        return "RobotoMono-Regular"

    def on_enter(self):
        self.spiner = MDSpinner(
            active=False,
            size_hint=(None, None),
            size=(30, 30),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        self.create_btn = MDRaisedButton(
            text="Create",
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            padding=[10],
            font_size=dp(18),
        )
        self.cancel = MDRaisedButton(
            text="Abort",
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            padding=[10],
            font_size=dp(18),
            md_bg_color=(1, 0, 0, 1),
            on_release=lambda x: self.cancel_command(),
        )

        self.create = MDBoxLayout(
            self.create_btn,
            self.spiner,
            orientation="horizontal",
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            size_hint=(0.3, 0.2),
            spacing=dp(20),
        )
        # Create a ScrollView for the output
        self.output_label = MDTextField(
            text="Process output..\n",
            size_hint=(1, None),
            pos_hint={"center_x": 0.5},
            font_size=dp(14),
            multiline=True,
            font_name=self.robofont(),
            line_color_normal=[1, 1, 1, 0],  # Set line color to transparent
            line_color_focus=[1, 1, 1, 0],
            padding=[dp(10)],
        )

        scroll_view = MDScrollView(
            self.output_label,
            size_hint=(0.9, 1),
            do_scroll_x=False,
            pos_hint={"center_x": 0.5},
        )
        self.ids.mac_content.clear_widgets()
        self.create_btn.bind(on_press=self.show_command)

        layout = MDBoxLayout(
            self.setting(),
            self.create,
            scroll_view,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            orientation="vertical",
        )
        self.ids.mac_content.add_widget(layout)

    @mainthread
    def start_cmd(self):
        self.spiner.active = True
        self.create_btn.disabled = True
        self.ids.top_bar.disabled = True
        self.create.add_widget(self.cancel)

    @mainthread
    def stop_cmd(self):
        self.spiner.active = False
        self.create_btn.disabled = False
        self.ids.top_bar.disabled = False
        self.create.remove_widget(self.cancel)

    @multitasking.task
    def execute_command(self, command):
        self.start_cmd()
        sudo_command = ["sudo", "-S"] + command
        # print(f'Executing command: {sudo_command}')
        print(f"Executing...")
        self.update_output_label(f"Executing...")
        time.sleep(0.2)

        try:
            # Create a pseudo-terminal
            master_fd, slave_fd = pty.openpty()

            # Create the subprocess for the sudo command
            self.process = subprocess.Popen(
                sudo_command,
                stdin=slave_fd,
                stdout=slave_fd,
                stderr=slave_fd,
                close_fds=True,
                universal_newlines=True,
            )

            os.close(slave_fd)  # Close the slave_fd in the parent process

            # Read outputs
            while self.process:
                time.sleep(0.1)  # Small sleep to prevent high CPU usage
                if self.process:
                    try:
                        output = os.read(master_fd, 1024).decode()
                        if output:
                            print(output)
                            self.update_output_label(output.strip())

                            # Check if the process is asking for the sudo password
                            if (
                                "password" in output.lower()
                                and not self.password_prompt_shown
                            ):
                                # Show password dialog only when prompted
                                # print('Asking for sudo password')
                                self.password_prompt_shown = True
                                self.show_password_prompt(
                                    lambda password: self.send_sudo_password(
                                        password, master_fd
                                    )
                                )
                            if (
                                "incorrect" in output.lower()
                                or "failed" in output.lower()
                            ):
                                self.password_prompt_shown = True
                                self.show_password_prompt(
                                    lambda password: self.send_sudo_password(
                                        password, master_fd
                                    )
                                )
                            # Check if the process is asking for confirmation (yes/no)
                            if (
                                "continue" in output.lower()
                                or "yes/no" in output.lower()
                            ):
                                # print('Asking for confirmation')
                                self.send_yes(master_fd)

                        if self.process.poll() is not None:
                            break  # Exit the loop if the process has finished

                    except Exception as e:
                        print(f"Error while reading process output: {e}")
                        break
            self.password_prompt_shown = False
            os.close(master_fd)
            self.update_output_label("Process finished.\n")

            self.stop_cmd()
        except Exception as e:
            print(f"Execution error: {e}")
            self.update_output_label(f"Error: {str(e)}")

        finally:
            # Cleanup after the command completes or is canceled
            self.process = None
            self.password_prompt_shown = False  # Reset prompt flag for the next command

    @mainthread
    def send_sudo_password(self, password, master_fd):
        """Send the password to the subprocess."""
        if master_fd:
            os.write(master_fd, (password + "\n").encode())

    @mainthread
    def send_yes(self, master_fd):
        """Send 'yes' to the subprocess when required."""
        if master_fd:
            os.write(master_fd, ("yes\n").encode())

    @mainthread
    def update_output_label(self, new_text):
        """Update the output label safely from another thread."""
        self.output_label.text += new_text + "\n"  # Append output to label

    def cancel_command(self):
        """Handle the cancellation of the command process."""
        if self.process:
            print("Terminating the process...")
            self.process.terminate()  # Terminate the process
            self.process.wait()  # Wait for the process to fully terminate
            self.update_output_label("Process canceled by the user.\n")
            self.process = None  # Clear the process reference
            self.password_prompt_shown = False  # Reset the password prompt flag

    @mainthread
    def show_password_prompt(self, on_submit):
        """Show a dialog for entering the sudo password."""

        def on_submit_action(**instance):
            password = text_field.text.strip()  # Get password
            if password:
                on_submit(password)  # Call the provided callback
                if self.dialog:
                    self.dialog.dismiss()
            self.password_prompt_shown = False  # Reset the password prompt flag

        def on_cancel():
            # Terminate the process on cancel
            print("User canceled password entry.")
            self.cancel_command()

            if self.dialog:
                self.dialog.dismiss()

        text_field = MDTextField(
            id="img_directory",
            hint_text="password",
            multiline=True,
            font_name=self.robofont(),
            mode="rectangle",
            password=True,
            size_hint_y=None,
            height="40dp",
        )
        content = MDBoxLayout(
            text_field,
            orientation="vertical",
            spacing="12dp",
            padding="20dp",
            size_hint_y=None,
            adaptive_height=True,
        )
        self.dialog = MDDialog(
            title="Enter sudo password",
            type="custom",
            content_cls=content,
            buttons=[
                MDRaisedButton(
                    text="CANCEL",
                    on_release=lambda x: on_cancel(),
                    font_name=self.robofont(),
                ),
                MDRaisedButton(
                    text="Continue",
                    on_release=lambda x: on_submit_action(),
                    font_name=self.robofont(),
                ),
            ],
        )
        self.dialog.open()

    def show_command(self, instance):
        command = [
            f"{self.source_installer}/Contents/Resources/createinstallmedia",
            "--volume",
            self.target_volume,
        ]
        self.execute_command(command)

    def set_text(self, text, target="source"):
        print(text)
        if text is not None:
            if target == "source":
                self.source_installer = text
            else:
                self.target_volume = text

    def setting(self):
        """Open the settings dialog to change the image directory."""

        @staticmethod
        def get_path(target="target"):
            selected_dir = (
                filedialog.askdirectory()
                if target == "target"
                else filedialog.askopenfilename()
            )
            Window.raise_window()  # Bring Kivy window back to focus
            return selected_dir

        def set_path(target="target"):
            p = get_path(target)
            if p != "":
                if target == "target":
                    self.target_volume = p
                    target_volume.text = p
                    target_volume.focus = True
                    print(p)
                elif target == "source":
                    self.source_installer = p
                    source_installer.text = p
                    source_installer.focus = True
                    print(p)

        source_installer = MDTextField(
            id="source_installer",
            hint_text="Source Installer",
            mode="rectangle",
            font_name=self.robofont(),
            multiline=False,
            text=self.source_installer if self.source_installer else "",
            on_text=lambda x: self.set_text(x.text, "source"),
            size_hint_y=None,
            height="40dp",
        )
        choose_source_btn = MDRaisedButton(
            text="Browse",
            size_hint_y=None,
            font_name=self.robofont(),
            height="40dp",
            on_release=lambda *args: set_path("source"),
        )

        target_volume = MDTextField(
            id="target_volume",
            hint_text="Target Volume",
            mode="rectangle",
            font_name=self.robofont(),
            multiline=False,
            text=self.target_volume if self.target_volume else "",
            on_text=lambda x: self.set_text(x.text, "target"),
            size_hint_y=None,
            height="40dp",
        )
        choose_volume_btn = MDRaisedButton(
            text="Browse",
            size_hint_y=None,
            font_name=self.robofont(),
            height="40dp",
            on_release=lambda *args: set_path("target"),
        )

        content = MDBoxLayout(
            source_installer,
            choose_source_btn,
            target_volume,
            choose_volume_btn,
            orientation="vertical",
            spacing="12dp",
            padding="20dp",
            size_hint_y=None,
            adaptive_height=True,
        )
        return content
