#require brew, gdisk for hybrid partition
# require wimlib (brew install wimlib)
# require rsync version 3.3.0  protocol version 31
import pty
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
from kivymd.uix.label import MDLabel
from kivy.metrics import dp
from kivy.clock import Clock, mainthread
from kivy.core.window import Window
from kivy.resources import resource_add_path
import traceback
from kivy.config import Config
import re
from kivy.uix.progressbar import ProgressBar
from kivy.uix.screenmanager import Screen
# Disable multitouch emulation (red dot)
Config.set('input', 'mouse', 'mouse,disable_multitouch')
class WIN(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.app = MDApp.get_running_app() 
        self.output_label = None
        self.source_installer = '/Volumes/Libra/SW/WindowsISO/Windows10_22H2.iso'
        self.target_volume = '/Volumes/Windows10'
        self.command_thread = None
        self.dialog = None
        self.process = None
        self.password_prompt_shown = False
        

    def robofont(self):
        return 'RobotoMono-Regular'
    def on_enter(self):
        
        self.spiner = MDSpinner(active=False, size_hint=(None, None), size=(30, 30),pos_hint={'center_x':0.5, 'center_y':0.5})
        self.create_btn = MDRaisedButton(text='Create',  pos_hint={'center_x':0.5, 'center_y':0.5}, padding=[10], font_size=dp(18))
        self.cancel = MDRaisedButton(text='Abort',  pos_hint={'center_x':0.5, 'center_y':0.5}, padding=[10], font_size=dp(18),md_bg_color=(1,0,0,1), on_release=lambda x: self.cancel_command())
        self.stage = MDLabel(text="Waiting...",size_hint=(0.9, None),height=dp(20),pos_hint={'center_x':0.5, 'center_y':0.5},font_name=self.robofont(),font_size=dp(14), disabled=True)
        self.progress_bar = ProgressBar(value=0,max=100,size_hint=(0.9, None),height=dp(20),pos_hint={'center_x':0.5, 'center_y':0.5})  # Set the maximum to 100%
        self.progress_label = MDLabel(text="0%",size_hint=(0.9, None),height=dp(20),pos_hint={'center_x':0.5, 'center_y':0.5},font_name=self.robofont(),font_size=dp(12), disabled=True, padding=[0,0,0,10])
        self.create = MDBoxLayout(
            self.create_btn,
            self.spiner,
            orientation='horizontal',            
            pos_hint={'center_x':0.5, 'center_y':0.5},
            size_hint = (0.3, 0.2),            
            spacing=dp(20)
        )
        # Create a ScrollView for the output
        self.output_label = MDTextField(
            text='Process output..\n', 
            size_hint=(1, None), pos_hint={'center_x': 0.5}, 
            font_size=dp(12),
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
            pos_hint={'center_x': 0.5}
        )
        
        self.create_btn.bind(on_press=self.main_command)

        layout = MDBoxLayout(
            self.setting(),
            self.create,
            self.stage,
            self.progress_bar,
            self.progress_label,
            scroll_view,
            pos_hint={'center_x':0.5, 'center_y':0.5},
            orientation='vertical'
        )
        self.ids.win_content.clear_widgets()
        self.ids.win_content.add_widget(layout)
    @mainthread
    def start_cmd(self):
        self.spiner.active= True
        self.create_btn.disabled=True
        self.ids.top_bar.disabled=True
        self.create.add_widget(self.cancel)
    @mainthread
    def stop_cmd(self):
        self.spiner.active= False
        self.create_btn.disabled=False
        self.ids.top_bar.disabled=False
        self.create.remove_widget(self.cancel)
    #@multitasking.task
    def execute_command(self, command, title='Executing...'):
        
        #print(f'Executing command: {cmd}')
        print(title)
        self.update_output_label(title)
        
        try:
            # Create a pseudo-terminal
            master_fd, slave_fd = pty.openpty()

            # Create the subprocess for the sudo command
            self.process = subprocess.Popen(command, stdin=slave_fd, stdout=slave_fd, stderr=slave_fd, close_fds=True, universal_newlines=True)

            os.close(slave_fd)  # Close the slave_fd in the parent process
            total_files = 0
            copied_files = 0
            # Read outputs
            while self.process:
                #time.sleep(0.1)  # Small sleep to prevent high CPU usage
                if self.process:
                    try:
                        output = os.read(master_fd, 1024).decode()
                        if output:
                            print(output)
                            line = output.strip()
                            #self.update_output_label(output.strip())
                            try:
                                total_files, copied_files = self.extract_file_counts(line, total_files, copied_files)
                                self.update_progress(line, total_files, copied_files)
                            except:
                                pass
                            # Check if the process is asking for the sudo password
                            if 'password' in output.lower() and not self.password_prompt_shown:
                                # Show password dialog only when prompted
                                #print('Asking for sudo password')
                                self.password_prompt_shown = True
                                self.show_password_prompt(lambda password: self.send_sudo_password(password, master_fd))
                            if 'incorrect' in output.lower() or 'failed' in output.lower():
                                self.password_prompt_shown = True
                                self.show_password_prompt(lambda password: self.send_sudo_password(password, master_fd))
                            # Check if the process is asking for confirmation (yes/no)
                            if 'continue' in output.lower() or 'yes/no' in output.lower():
                                #print('Asking for confirmation')
                                self.send_yes(master_fd)

                        if self.process.poll() is not None:
                            break  # Exit the loop if the process has finished

                    except Exception as e:
                        print(f"Error while reading process output: {e}")
                        break
            self.password_prompt_shown = False
            os.close(master_fd)
            
            
            
        except Exception as e:
            print(f"Execution error: {e}")
            print(traceback.format_exc())
            self.update_output_label(f"Error: {str(e)}")
            

        finally:
            # Cleanup after the command completes or is canceled
            self.process = None
            self.password_prompt_shown = False  # Reset prompt flag for the next command
    def main_command(self, args):
        self.update_output_label("...")
        self.main_execute()
    @multitasking.task
    def main_execute(self):
        self.start_cmd()
        time.sleep(1)
        self.update_output_label("Starting process...")
        try:
            format_stt = self.format_volume(self.target_volume)
            #format_stt = True
            if format_stt: 
                mounted_volume = self.mount_iso(self.source_installer)
                if mounted_volume:
                    install_wim_path = os.path.join(mounted_volume, "sources", "install.wim")
                    if os.path.exists(install_wim_path):
                        install_wim_size = os.path.getsize(install_wim_path) / (1024 * 1024 * 1024)  # GB
                        if install_wim_size < 4:                            
                            self.copy_files(mounted_volume, self.target_volume)
                        else:
                            self.split_install_wim(mounted_volume, self.target_volume)
                            self.copy_files(mounted_volume, self.target_volume, exclude_wim=True)
                            
                else:
                    self.update_output_label("ISO mounting failed.")
        except Exception as e:
            self.update_output_label(f"Error: {e}")
        finally:
            self.stop_cmd()
            self.update_output_label("Process finished.\n")
            self.update_output_label("Process of creating windows installer is completed.\n")
            self.set_stage('Completed!')
    @mainthread
    def update_bar_value(self,value):
        if  value:
            self.progress_bar.value = int(value)
            self.progress_label.text = f"Progress: {int(value)}%"
    @mainthread
    def update_bar_max(self,value):
        if  value:
            self.progress_bar.max = value
    def extract_file_counts(self, line, total_files, copied_files):
        
        print(f'{copied_files}/{total_files}')
        # Look for total files to consider
        if re.search(r'\d+%', line):
            copied_files = int(re.search(r'(\d+)%', line).group(1))
            total_files = 100
        self.update_bar_max(total_files)
        return total_files, copied_files
    
    def update_progress(self, line, total_files, copied_files):
        if total_files > 0:
            # Calculate the overall progress percentage
            progress_percentage = (copied_files / total_files) * 100
            self.update_bar_value(progress_percentage)
    
    def format_volume(self, target):
        self.update_output_label(f"Formating volume: {target}")
        volume_name = self.target_volume.split('/')[-1]
        try:
            format_cmd = ["diskutil", "eraseVolume", "MS-DOS", volume_name, target ]
            #format_cmd = ["diskutil", "eraseDisk", "MS-DOS", volume_name, "MBR", 'disk5' ]
            result = subprocess.check_output(format_cmd).decode()
            self.update_output_label(f"Format result: {result}")
            #self.execute_command(format_cmd,f"formating volumes with FAT32: {target}")
            return True
        except subprocess.CalledProcessError as e:
            print(e)
            self.update_output_label(f"rsync failed: {e}")

    def get_volume_name(self, target):
        try:
            # Using diskutil to get the volume name based on the mount point
            result = subprocess.check_output(['diskutil', 'info', target]).decode()
            for line in result.splitlines():
                if 'Volume Name:' in line:
                    volume_name = line.split(":")[-1].strip()
                    return volume_name
        except subprocess.CalledProcessError as e:
            self.update_output_label(f"Error fetching volume name: {str(e)}\n")
            return None

    def mount_iso(self, iso_path):
        self.update_output_label(f"mounting ISO from: {iso_path}")
        try:
            result = subprocess.check_output(["hdiutil", "mount", iso_path]).decode()
            for line in result.splitlines():
                if '/Volumes/' in line:
                    mounted_volume = line.split("\t")[-1]
                    self.update_output_label(f"Mounted ISO at {mounted_volume}")
                    return mounted_volume
        except subprocess.CalledProcessError as e:
            self.update_output_label(f"Failed to mount ISO: {e}")
        return None
    def copy_files(self, source, target, exclude_wim=False):
        try:
            rsync_cmd = ["rsync", "-avh", "--info=progress2"]
            if exclude_wim:
                self.set_stage('Stage 2/2: Creating Installer')
                rsync_cmd.append("--exclude=sources/install.wim")
            else:
                self.set_stage('Stage 1/1: Creating Installer')
            rsync_cmd.extend([f"{source}/", target])
            print(f"rsync cmd: {rsync_cmd}")
            self.execute_command(rsync_cmd,f"Copying data from ISO to: {target} {'excluding vim file ' if exclude_wim else ''}")
        except subprocess.CalledProcessError as e:
            self.update_output_label(f"rsync failed: {e}")

    def split_install_wim(self, source, target):
        self.set_stage('Stage 1/2: Preparing image.')
        try:
            wim_source_dir = os.path.join(target,'sources')
            if not os.path.exists(wim_source_dir):
                try:
                    # Create the directory
                    os.makedirs(wim_source_dir)
                    print(f"Created directory: {wim_source_dir}")
                except Exception as e:
                    print(f"Failed to create directory: {e}")
            else:
                print(f"Directory already exists: {wim_source_dir}")
            install_wim = os.path.join(source, "sources", "install.wim")
            split_cmd = [
                "wimlib-imagex", "split", install_wim, 
                os.path.join(wim_source_dir, "install.swm"), "3800"
            ]
            print(f"split cmd: {split_cmd}")
            self.execute_command(split_cmd,f"Splitting install.wim and copied to {target}")
        except subprocess.CalledProcessError as e:
            self.update_output_label(f"Failed to split install.wim: {e}")
    @mainthread
    def set_stage(self, text):
        self.stage.text = text
    @mainthread
    def send_sudo_password(self, password, master_fd):
        """Send the password to the subprocess."""
        if master_fd:
            os.write(master_fd, (password + '\n').encode())

    @mainthread
    def send_yes(self, master_fd):
        """Send 'yes' to the subprocess when required."""
        if master_fd:
            os.write(master_fd, ('yes\n').encode())

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
            adaptive_height=True
        )
        self.dialog = MDDialog(
            title="Enter sudo password",            
            type='custom',
            content_cls=content,
            buttons=[
                MDRaisedButton(text='CANCEL', on_release=lambda x: on_cancel(),font_name=self.robofont(),),
                MDRaisedButton(text='Continue', on_release=lambda x: on_submit_action(),font_name=self.robofont(),),
            ]
        )
        self.dialog.open()


    def set_text(self, text, target='source'):
        print(text)
        if text is not None:
            if target == 'source':
                self.source_installer = text
            else:
                self.target_volume = text

    def setting(self):
        """Open the settings dialog to change the image directory."""
        @staticmethod
        def get_path(target="target"):
            selected_dir = filedialog.askdirectory() if target == "target" else filedialog.askopenfilename()
            Window.raise_window()  # Bring Kivy window back to focus
            return selected_dir

        def set_path(target="target"):
            p = get_path(target)
            if p != '':
                if target == 'target':
                    self.target_volume = p
                    target_volume.text = p
                    target_volume.focus = True
                    print(p)
                elif target == 'source':
                    self.source_installer = p
                    source_installer.text = p
                    source_installer.focus = True
                    print(p)

        source_installer = MDTextField(
            id="source_installer",
            hint_text='Source Installer',
            mode="rectangle",
            font_name=self.robofont(),
            multiline=False,
            text=self.source_installer if self.source_installer else "",
            on_text=lambda x: self.set_text(x.text, 'source'),
            size_hint_y=None,
            height="40dp",
        )
        choose_source_btn = MDRaisedButton(
            text="Browse",
            size_hint_y=None,
            font_name=self.robofont(),
            height="40dp",
            on_release=lambda *args: set_path('source')
        )

        target_volume = MDTextField(
            id="target_volume",
            hint_text="Target Volume",
            mode="rectangle",
            font_name=self.robofont(),
            multiline=False,
            text=self.target_volume if self.target_volume else "",
            on_text=lambda x: self.set_text(x.text, 'target'),
            size_hint_y=None,
            height="40dp",
        )
        choose_volume_btn = MDRaisedButton(
            text="Browse",
            size_hint_y=None,
            font_name=self.robofont(),
            height="40dp",
            on_release=lambda *args: set_path('target')
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
            adaptive_height=True
        )
        return content
# PyInstaller Configuration
# if __name__ == '__main__':
#     try:
#         if hasattr(sys, '_MEIPASS'):            
#             resource_add_path(os.path.join(sys._MEIPASS))
#         app = WIN()
#         # Use logging
#         print("Application started")
#         app.run()
#     except Exception as e:
#         #logger.exception('Error')
        
#         """
#         If the app encounters an error it automatically saves the
#         error in a file called ERROR.log.
#         You can use this for BugReport purposes.
#         """
#         print(traceback.format_exc())
#         with open('error.log', "w") as error_file:
#             error_file.write(f'{e}: \n{traceback.format_exc()}')
