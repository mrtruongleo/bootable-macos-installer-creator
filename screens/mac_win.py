import os
import multitasking
import time
import subprocess
from tkinter import filedialog
from tkinter import *
from kivymd.uix.scrollview import MDScrollView
from kivymd.app import MDApp
from kivymd.uix.dialog import MDDialog
from kivymd.uix.button import MDRaisedButton
from kivymd.uix.textfield import MDTextField
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.spinner import MDSpinner
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
from kivy.clock import mainthread, Clock
from kivy.core.window import Window
from kivy.config import Config
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import Screen
# from elevate import elevate
from utils import mount as iso
from utils import func as fn
from utils import format as fm
from utils.components import SelectList
from kivy.properties import (
    BooleanProperty,
    ObjectProperty,
    StringProperty,
    ListProperty,
    DictProperty,
    NumericProperty,
    ColorProperty,
)

startupinfo = subprocess.STARTUPINFO()
startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW


class WIN(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app()
        self.output_label = None
        self.source_installer = "C:/Users/Rayac/Downloads/Win11_24H2_x64.iso"
        self.disks = []
        self.target_disk = None
        self.target_scheme = "mbr"
        self.target_size = "10000"
        self.target_volume = None
        self.target_volume_format = "fat32"
        self.target_label = "WIN"
        self.make_hybrid = True
        self.bypass_tpm = True
        self.make_boot_process_only = False
        self.target_scheme_info_text = (
            "* Use mbr to create an installer works with both Bios Legacy and UEFI mode"
        )
        self.command_thread = None
        self.dialog = None
        self.process = None

    def robofont(self):
        return "RobotoMono-Regular"

    def on_enter(self):
        self.set_default_text()
        self.get_disks()
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
        self.stage = MDLabel(
            text="Waiting...",
            size_hint=(0.9, None),
            height=dp(20),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            font_name=self.robofont(),
            font_size=dp(14),
            disabled=True,
        )
        self.progress_bar = ProgressBar(
            value=0,
            max=100,
            size_hint=(0.9, None),
            height=dp(20),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
        )
        self.progress_label = MDLabel(
            text="0%",
            size_hint=(0.9, None),
            height=dp(20),
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            font_name=self.robofont(),
            font_size=dp(12),
            disabled=True,
            padding=[0, 0, 0, 10],
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
            text="\n",
            size_hint=(1, None),
            pos_hint={"center_x": 0.5},
            font_size=dp(12),
            multiline=True,
            font_name=self.robofont(),
            line_color_normal=[1, 1, 1, 0],
            line_color_focus=[1, 1, 1, 0],
            padding=[dp(10)],
        )

        scroll_view = MDScrollView(
            self.output_label,
            size_hint=(0.9, 1),
            do_scroll_x=False,
            pos_hint={"center_x": 0.5},
        )

        self.create_btn.bind(on_press=self.main_command)

        layout = MDBoxLayout(
            # self.setting(),
            self.create,
            self.stage,
            self.progress_bar,
            self.progress_label,
            scroll_view,
            pos_hint={"center_x": 0.5, "center_y": 0.5},
            orientation="vertical",
        )
        self.ids.win_content.clear_widgets()
        self.ids.win_content.add_widget(layout)

    def main_command(self, args):
        self.update_output_label("...")
        if self.source_installer and self.target_disk:
            self.main_execute()
        else:
            self.update_output_label("Please select source installer and target volume")

    @multitasking.task
    def main_execute(self):
        self.start_cmd()
        time.sleep(1)
        self.update_output_label("Starting process...")
        try:
            if self.make_boot_process_only == False:
                drive_letter = self.format_drive()
                if drive_letter:
                    self.target_volume = drive_letter
                    self.mount_iso()
                    self.copy_process()
                    self.unmount_iso()
            self.make_boot_process()
        except Exception as e:
            self.update_output_label(f"Error: {e}")
        finally:
            self.stop_cmd()
            self.update_output_label("Process finished.\n")
            self.update_output_label(
                "Process of creating windows installer is completed.\n"
            )
            self.set_stage("Completed!")
            self.progress_label.text = " "

    @mainthread
    def set_stage(self, text):
        self.stage.text = text

    @mainthread
    def update_output_label(self, message):
        self.output_label.text += f"{message}\n"
        print(message)

    def set_hybrid(self, ins, *args):
        print(f"Make hybrid: {ins.active}")
        self.make_hybrid = ins.active

    def bypass_tpm_check(self, ins, *args):
        print(f"Bypass TPM: {ins.active}")
        self.bypass_tpm = ins.active

    def make_boot_only(self, ins, *args):
        print(f"make boot only: {ins.active}")
        self.make_boot_process_only = ins.active

    def select_disk(self):
        pass

    @multitasking.task
    def get_disks(self):
        @mainthread
        def set_disks(disks):
            self.disks = disks
            try:
                current_disk = self.disks[-1]
                if current_disk:
                    print(current_disk)
                    self.ids.target_disk.text = (
                        f'{current_disk["number"]}: {current_disk["info"]}'
                    )
                    self.target_disk = current_disk["number"]
                print(self.disks)
            except:
                pass

        disks = fn.get_disks()
        set_disks(disks)

    def select_disk(self):
        # Parse the result
        def on_choose(ins):
            self.target_disk = ins.disk_number
            self.ids.target_disk.text = ins.secondary_text
            if self.dialog:
                self.dialog.dismiss()
            print(f"selected_disk: {self.target_disk}")

        if len(self.disks) > 0:
            list_items = []
            for disk in self.disks:
                # Parse the disk info (Number and Model)
                disk_number = disk["number"]
                # Create a OneLineListItem for each disk
                item = SelectList(
                    disk_number=f"{disk_number}",
                    checked=self.target_disk == f"{disk_number}",
                    text=f"Disk {disk_number}",
                    secondary_text=f'{disk_number}: {disk["info"]}',
                    tertiary_text=" ",
                    on_release=lambda x: on_choose(x),
                )
                list_items.append(item)

            # Create and open the dialog with disk options
            self.dialog = MDDialog(
                title="Select a Disk",
                type="simple",
                size_hint=(0.7, None),
                items=list_items,
            )
            self.dialog.open()

    def set_text(self, text, target="source"):
        # print(text)
        if text is not None:
            if target == "source":
                self.source_installer = text
            elif target == "target":
                self.target_volume = text
            elif target == "format":
                self.target_volume_format = text
            elif target == "label":
                self.target_label = text

    def set_default_text(self):
        self.ids.source_installer.text = self.source_installer
        self.ids.target_scheme.text = self.target_scheme
        self.ids.target_size.text = self.target_size
        self.ids.target_label.text = self.target_label
        self.ids.target_volume_format.text = self.target_volume_format
        self.ids.target_scheme_info.text = self.target_scheme_info_text
        self.ids.bypass_tpm.active = self.bypass_tpm

    def set_path(self, target="target"):
        @staticmethod
        def get_path(target="target"):
            selected_dir = (
                filedialog.askdirectory()
                if target == "target"
                else filedialog.askopenfilename()
            )
            Window.raise_window()  # Bring Kivy window back to focus
            return selected_dir

        p = get_path(target)
        source_installer = self.ids.source_installer
        if p != "":
            if target == "source":
                self.source_installer = p
                source_installer.text = p
                source_installer.focus = True
                print(p)

    @mainthread
    def start_cmd(self):
        self.spiner.active = True
        self.create_btn.disabled = True
        self.ids.top_bar.disabled = True
        self.create.add_widget(self.cancel)
        self.update_bar_max(0)
        self.update_bar_value(0)

    @mainthread
    def stop_cmd(self):
        self.spiner.active = False
        self.create_btn.disabled = False
        self.ids.top_bar.disabled = False
        self.create.remove_widget(self.cancel)

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
    def update_bar_value(self, value):
        if value:
            self.progress_bar.value = int(value)
            self.progress_label.text = f"Progress: {int(value)}%"

    @mainthread
    def update_bar_max(self, value):
        if value:
            self.progress_bar.max = value

    def execute_command(self, command, title="Executing...", **kwargs):
        print(title)
        self.update_output_label(title)
        try:
            total_files = kwargs.get("total_files", 0)
            copied_files = 0
            self.process = subprocess.Popen(
                command,
                startupinfo=startupinfo,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            for line in self.process.stdout:
                # print(line.strip())
                if "robocopy" in command:
                    # self.update_output_label(line.strip())
                    try:
                        total_files, copied_files = self.extract_file_counts(
                            line, total_files, copied_files
                        )
                        self.update_progress(line, total_files, copied_files)
                    except:
                        pass
                else:
                    self.update_output_label(line.strip())
            # Capture the output and errors
            stdout, stderr = self.process.communicate()
            if stderr:
                print(f"error: {stderr}")
            # self.process.wait()
        except Exception as e:
            self.update_output_label(f"Error: {e}")
        finally:
            self.process = None

    def format_drive(self):
        return fm.format_drive(
            disk_number=self.target_disk,
            scheme=self.target_scheme,
            file_system=self.target_volume_format,
            volume_label=self.target_label,
            size=self.target_size,
            update_info=self.update_output_label,
        )

    def mount_iso(self):
        if self.source_installer:
            self.mounted_iso_drive = iso.mount_iso(
                self.source_installer, self.update_output_label
            )

    def unmount_iso(self):
        if self.mounted_iso_drive:
            try:
                iso.unmount_iso(self.source_installer, self.update_output_label)
            except Exception as e:
                self.update_output_label(f"Unmount iso failed: {e}")

    def extract_file_counts(self, line, total_files, copied_files):
        if "New File" in line:  # or "100%" in line:
            copied_files += 1
        return total_files, copied_files

    def update_progress(self, line, total_files, copied_files):
        if total_files > 0:
            # Calculate the overall progress percentage
            progress_percentage = (copied_files / total_files) * 100
            self.update_bar_value(progress_percentage)

    def make_boot_process(self):
        if self.target_scheme.lower() == "mbr":
            # fm.make_hybrid(self.target_volume, self.update_output_label)
            fm.make_active(self.target_volume, self.update_output_label)
        if self.bypass_tpm:
            fn.copy_file_to_drive(os.path.join(self.app.exe_path,"autounattend.xml"), self.target_volume)
        try:
            fm.make_bootable(self.target_volume, self.update_output_label)
        except Exception as e:
            print(f"Make active or make bootable error: {e}")

    def copy_process(self):
        if self.mounted_iso_drive:
            if self.target_volume_format.lower() == "fat32":
                install_wim_path = os.path.join(
                    self.mounted_iso_drive, "sources", "install.wim"
                )
                if os.path.exists(install_wim_path):
                    install_wim_size = os.path.getsize(install_wim_path) / (
                        1024 * 1024 * 1024
                    )  # GB
                    if install_wim_size < 4:
                        self.copy_files(self.mounted_iso_drive, self.target_volume)
                    else:
                        self.split_install_wim_windows(
                            self.mounted_iso_drive, self.target_volume
                        )
                        self.copy_files(
                            self.mounted_iso_drive,
                            self.target_volume,
                            exclude_wim=True,
                        )

                elif os.path.exists(
                    os.path.join(self.mounted_iso_drive, "sources", "install.swm")
                ):
                    self.copy_files(self.mounted_iso_drive, self.target_volume)
                else:
                    self.update_output_label("install.wim or install.swm not found.")
            else:
                self.copy_files(self.mounted_iso_drive, self.target_volume)

    def copy_files(self, source, target, exclude_wim=False):
        try:
            # Build the robocopy command
            robocopy_cmd = [
                "robocopy",
                f"{source[:1]}:",
                f"{target[:1]}:",
                "/E",
                "/NDL",
                "/NJH",
                "/NJS",
            ]
            # Execute the robocopy command to copy all files
            total_files = 0
            try:
                total_files, copied_files = fn.get_total_files(source, target)
                print(f"total files: {total_files}")
            except:
                pass
            # If exclude_wim is True, exclude the "install.wim" file from copying
            if exclude_wim:
                total_files = total_files - 1
                self.set_stage("Stage 2/2: Creating Installer")

                # Use /XF to exclude the install.wim file
                robocopy_cmd.extend(
                    ["/XF", os.path.join(f"{source[:1]}:\\", "sources", "install.wim")]
                )
            else:
                self.set_stage("Stage 1/1: Creating Installer")

            self.execute_command(
                command=robocopy_cmd,
                title=f"Copying files to {target}{', Exclude install.wim file' if exclude_wim else ''}...",
                total_files=total_files,
            )
            self.update_bar_max(100)
        except subprocess.CalledProcessError as e:
            self.update_output_label(f"File copy failed: {e}")

    def split_install_wim_windows(self, source, target):
        try:
            self.update_output_label(f"Splitting windows files to {target}...")
            # Elevate privileges to run the command as an administrator
            # elevate(show_console=False)  # Automatically elevates the process
            install_wim_size = 0
            install_wim_path = os.path.join(
                self.mounted_iso_drive, "sources", "install.wim"
            )
            if os.path.exists(install_wim_path):
                install_wim_size = os.path.getsize(install_wim_path)

            @multitasking.task
            def update_progress():
                target_source_path = os.path.join(
                    f"{self.target_volume[:1]}:", "sources"
                )
                if os.path.exists(target_source_path):
                    print("calculating...")
                    copied_size = fn.get_directory_size(target_source_path)
                    progress = (copied_size / install_wim_size) * 100
                    self.update_bar_value(progress)
                    print(f"Progress: {progress:.2f}%")

            self.set_stage("Stage 1/2: Preparing image.")

            split_cmd = fn.split_command(source, target)
            # Execute the split command and update the UI with progress
            # self.execute_command(
            #     split_cmd, f"Splitting install.wim from {source} to {target}"
            # )
            # Run the command and capture the output in real-time

            process = subprocess.Popen(
                split_cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1,  # Line-buffered output
            )
            clock = Clock.schedule_interval(lambda x: update_progress(), 10)
            while True:
                time.sleep(0.1)
                output = process.stdout.readline()

                if output == "" and process.poll() is not None:
                    clock.cancel()
                    break
                if output:
                    print(output.strip())  # Display DISM output

            stderr = process.communicate()[1]
            if stderr:
                print("Error:", stderr)
        except subprocess.CalledProcessError as e:
            # Handle any errors during the split process
            self.update_output_label(f"Failed to split install.wim: {e}")
