import kivy
from kivymd.app import MDApp
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.clock import Clock, mainthread
import subprocess
import threading
import multitasking


class TerminalApp(MDApp):
    def build(self):
        self.theme_cls.material_style = "M3"
        self.theme_cls.theme_style = "Dark"
        self.theme_cls.primary_palette = "Indigo"
        self.layout = BoxLayout(orientation="vertical")

        # TextInput to display output and accept input
        self.terminal_output = TextInput(
            text="Starting...",
            size_hint=(1, 0.9),
            readonly=True,
            font_name="RobotoMono-Regular",
        )
        self.terminal_input = TextInput(
            size_hint=(1, 0.1), multiline=False, font_name="RobotoMono-Regular"
        )

        # Button to send input
        send_button = Button(text="Send Command", size_hint=(1, 0.1))
        send_button.bind(on_press=self.send_command)

        self.layout.add_widget(self.terminal_output)
        self.layout.add_widget(self.terminal_input)
        self.layout.add_widget(send_button)

        # Start the gdisk64 process in a thread
        self.run_gdisk_process()

        return self.layout

    @multitasking.task
    def run_gdisk_process(self):
        """
        Run the gdisk64.exe process and capture its output.
        """
        # Start the subprocess with pipes for stdin and stdout
        self.process = subprocess.Popen(
            ["exe/gdisk64.exe", "2:"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
        )

        # Read output in a non-blocking manner and update terminal
        for line in iter(self.process.stdout.readline, ""):
            if line != "\n":
                Clock.schedule_once(lambda dt: self.update_terminal_output(line), 0)

    @mainthread
    def update_terminal_output(self, text):
        """
        Update the terminal output TextInput with new text.
        """
        self.terminal_output.text += text

    def send_command(self, instance):
        """
        Send command to gdisk64 process from the terminal_input field.
        """
        user_input = (
            self.terminal_input.text + "\n"
        )  # Add newline for command execution
        self.process.stdin.write(user_input)
        self.process.stdin.flush()

        # Clear input field
        self.update_terminal_output("")


# Run the app
if __name__ == "__main__":
    TerminalApp().run()
