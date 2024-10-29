import re
import subprocess
import time
from kivy.clock import mainthread
from kivymd.uix.textfield import MDTextField
from kivymd.uix.label import MDLabel
from kivy.uix.button import Button
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.app import MDApp
import multitasking

class MyApp(MDApp):
    def build(self):
        self.layout = MDBoxLayout(orientation='vertical')
        self.output_label = MDTextField(
            text="Output will appear here...\n",
            multiline=True,
            size_hint_y=0.5
        )
        self.progress_label = MDLabel(
            text="",
            size_hint_y=0.2
        )
        self.start_button = Button(text="Start Command")
        self.start_button.bind(on_release=lambda x: self.start_command())
        
        self.layout.add_widget(self.output_label)
        self.layout.add_widget(self.progress_label)
        self.layout.add_widget(self.start_button)
        return self.layout

    def start_command(self):
        self.run_command_in_thread()

    @multitasking.task
    def run_command_in_thread(self):
        self.update_output("Starting process...")
        
        try:
            command = ["exe\\brigadier.exe", "-m", "MacBookPro8,1", "-o", "C:\\"]
            
            # Debug output
            self.update_output(f"Executing command: {' '.join(command)}")
            
            self.process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,  # Merge stderr into stdout
                universal_newlines=True,
                bufsize=1,
                shell=True  # Try with shell=True to handle Windows paths better
            )

            # Read output in chunks
            while True:
                output = self.process.stdout.readline()
                if output == '' and self.process.poll() is not None:
                    break
                if output:
                    output = output.strip()
                    print(f"Debug: {output}")  # Console debug output
                    
                    # Handle progress updates
                    if '%' in output:
                        self.update_progress(output)
                    else:
                        self.update_output(output)

            # Get the return code
            return_code = self.process.poll()
            self.update_output(f"Process finished with return code: {return_code}")

        except Exception as e:
            error_msg = f"Error occurred: {str(e)}"
            print(error_msg)  # Console debug output
            self.update_output(error_msg)

    @mainthread
    def update_output(self, text):
        current_text = self.output_label.text
        self.output_label.text = f"{current_text}{text}\n"
        # Scroll to the bottom
        self.output_label.cursor = (0, 0)
        self.output_label.do_cursor_movement('cursor_end')

    @mainthread
    def update_progress(self, text):
        self.progress_label.text = text

if __name__ == '__main__':
    MyApp().run()
