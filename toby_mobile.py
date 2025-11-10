from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.spinner import Spinner
from kivy.uix.popup import Popup
from kivy.uix.progressbar import ProgressBar
from kivy.core.window import Window
from kivy.garden.filebrowser import FileBrowser
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.scrollview import ScrollView
from kivy.clock import Clock
import yt_dlp
import threading
import os
from pathlib import Path

Window.size = (400, 700)

class TobyApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.download_path = os.path.join(str(Path.home()), "Downloads", "Toby")
        if not os.path.exists(self.download_path):
            os.makedirs(self.download_path)
        self.is_downloading = False

    def build(self):
        self.title = "Toby"
        
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        root_canvas = main_layout.canvas
        with root_canvas.before:
            from kivy.graphics import Color
            Color(0.96, 0.96, 0.96, 1)
            from kivy.graphics import Rectangle
            root_canvas.before.clear()

        header = BoxLayout(size_hint_y=0.15, padding=10, spacing=10)
        header.canvas.before.clear()
        with header.canvas.before:
            from kivy.graphics import Color
            Color(0.55, 0.62, 0.76, 1)
            from kivy.graphics import Rectangle
            header.canvas.before.add(Rectangle(size=header.size, pos=header.pos))
        
        title_label = Label(
            text="Toby",
            font_size="32sp",
            bold=True,
            color=(1, 1, 1, 1)
        )
        header.add_widget(title_label)
        main_layout.add_widget(header)

        scroll_view = ScrollView(size_hint=(1, 0.85))
        content_layout = BoxLayout(
            orientation='vertical',
            padding=15,
            spacing=15,
            size_hint_y=None
        )
        content_layout.bind(minimum_height=content_layout.setter('height'))

        url_label = Label(
            text="📎 Video or Music Link:",
            font_size="14sp",
            bold=True,
            size_hint_y=None,
            height=30,
            color=(0.17, 0.24, 0.31, 1)
        )
        content_layout.add_widget(url_label)

        self.url_input = TextInput(
            multiline=False,
            hint_text="https://youtube.com/watch?v=...",
            size_hint_y=None,
            height=45,
            background_color=(0.93, 0.94, 0.96, 1),
            foreground_color=(0.17, 0.24, 0.31, 1),
            hint_text_color=(0.7, 0.7, 0.7, 1)
        )
        content_layout.add_widget(self.url_input)

        type_label = Label(
            text="📥 Download Type:",
            font_size="14sp",
            bold=True,
            size_hint_y=None,
            height=30,
            color=(0.17, 0.24, 0.31, 1)
        )
        content_layout.add_widget(type_label)

        self.download_type = Spinner(
            text="Full Video",
            values=("Full Video", "Audio Only (MP3)"),
            size_hint_y=None,
            height=45,
            background_color=(0.55, 0.62, 0.76, 1),
            color=(1, 1, 1, 1)
        )
        content_layout.add_widget(self.download_type)

        folder_label = Label(
            text="📁 Download Folder:",
            font_size="14sp",
            bold=True,
            size_hint_y=None,
            height=30,
            color=(0.17, 0.24, 0.31, 1)
        )
        content_layout.add_widget(folder_label)

        folder_layout = BoxLayout(size_hint_y=None, height=50, spacing=10)
        
        self.folder_display = Label(
            text=self.download_path,
            font_size="11sp",
            size_hint_x=0.7,
            color=(0.4, 0.4, 0.4, 1),
            background_color=(0.93, 0.94, 0.96, 1)
        )
        folder_layout.add_widget(self.folder_display)

        choose_folder_btn = Button(
            text="Choose",
            size_hint_x=0.3,
            background_color=(0.42, 0.56, 0.71, 1),
            color=(1, 1, 1, 1)
        )
        choose_folder_btn.bind(on_press=self.choose_folder)
        folder_layout.add_widget(choose_folder_btn)

        content_layout.add_widget(folder_layout)

        self.status_label = Label(
            text="✓ Ready to download",
            font_size="12sp",
            size_hint_y=None,
            height=40,
            color=(0.42, 0.56, 0.71, 1),
            background_color=(0.93, 0.94, 0.96, 1)
        )
        content_layout.add_widget(self.status_label)

        self.progress_bar = ProgressBar(
            max=100,
            value=0,
            size_hint_y=None,
            height=4,
            canvas_bg_color=(0.93, 0.94, 0.96, 1)
        )
        content_layout.add_widget(self.progress_bar)

        space = Label(size_hint_y=None, height=10)
        content_layout.add_widget(space)

        scroll_view.add_widget(content_layout)
        main_layout.add_widget(scroll_view)

        button_layout = BoxLayout(size_hint_y=0.08, spacing=10, padding=5)

        self.download_btn = Button(
            text="▶ Download Now",
            background_color=(0.55, 0.62, 0.76, 1),
            color=(1, 1, 1, 1)
        )
        self.download_btn.bind(on_press=self.start_download)
        button_layout.add_widget(self.download_btn)

        self.stop_btn = Button(
            text="⏹ Stop",
            background_color=(0.78, 0.64, 0.64, 1),
            color=(1, 1, 1, 1),
            disabled=True
        )
        self.stop_btn.bind(on_press=self.cancel_download)
        button_layout.add_widget(self.stop_btn)

        main_layout.add_widget(button_layout)

        return main_layout

    def choose_folder(self, instance):
        content = BoxLayout(orientation='vertical')
        filechooser = FileChooserListView()
        content.add_widget(filechooser)

        btn_layout = BoxLayout(size_hint_y=0.1, spacing=10)
        select_btn = Button(text='Select')
        cancel_btn = Button(text='Cancel')
        btn_layout.add_widget(select_btn)
        btn_layout.add_widget(cancel_btn)
        content.add_widget(btn_layout)

        popup = Popup(title='Choose Download Folder', content=content, size_hint=(0.9, 0.9))

        def on_select(instance):
            if filechooser.selection:
                self.download_path = filechooser.selection[0]
                self.folder_display.text = self.download_path
            popup.dismiss()

        def on_cancel(instance):
            popup.dismiss()

        select_btn.bind(on_press=on_select)
        cancel_btn.bind(on_press=on_cancel)
        popup.open()

    def update_status(self, message, color=(0.42, 0.56, 0.71, 1)):
        self.status_label.text = message
        self.status_label.color = color

    def start_download(self, instance):
        url = self.url_input.text.strip()

        if not url:
            self.show_error("Please enter a video or music link")
            return

        if not url.startswith(('http://', 'https://')):
            self.show_error("Invalid link")
            return

        self.is_downloading = True
        self.download_btn.disabled = True
        self.stop_btn.disabled = False
        self.update_status("⏳ Downloading...", (0.55, 0.62, 0.76, 1))

        thread = threading.Thread(target=self.download_video, args=(url,))
        thread.daemon = True
        thread.start()

    def download_video(self, url):
        try:
            self.progress_bar.value = 30

            download_type = self.download_type.text
            
            if download_type == "Audio Only (MP3)":
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                    'quiet': False,
                    'no_warnings': False,
                    'noplaylist': True,
                }
            else:
                ydl_opts = {
                    'format': 'best',
                    'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                    'quiet': False,
                    'no_warnings': False,
                    'noplaylist': True,
                }

            self.progress_bar.value = 60

            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                if self.is_downloading:
                    ydl.download([url])

            self.progress_bar.value = 100

            if self.is_downloading:
                Clock.schedule_once(lambda dt: self.update_status("✅ Download completed!", (0.16, 0.42, 0.38, 1)), 0)
                Clock.schedule_once(lambda dt: self.url_input.__setattr__('text', ''), 0.5)
                Clock.schedule_once(lambda dt: self.update_status("✓ Ready to download", (0.42, 0.56, 0.71, 1)), 2)

        except Exception as e:
            if self.is_downloading:
                Clock.schedule_once(lambda dt: self.show_error(f"Error: {str(e)}"), 0)

        finally:
            self.is_downloading = False
            Clock.schedule_once(lambda dt: self._reset_buttons(), 0)
            Clock.schedule_once(lambda dt: self.progress_bar.__setattr__('value', 0), 2)

    def _reset_buttons(self):
        self.download_btn.disabled = False
        self.stop_btn.disabled = True

    def cancel_download(self, instance):
        self.is_downloading = False
        self.progress_bar.value = 0
        self.download_btn.disabled = False
        self.stop_btn.disabled = True
        self.update_status("⏹ Download stopped", (0.61, 0.55, 0.55, 1))
        Clock.schedule_once(lambda dt: self.update_status("✓ Ready to download", (0.42, 0.56, 0.71, 1)), 2)

    def show_error(self, message):
        content = BoxLayout(orientation='vertical', padding=10, spacing=10)
        label = Label(text=message, size_hint_y=0.8)
        content.add_widget(label)
        
        btn = Button(text='OK', size_hint_y=0.2, background_color=(0.55, 0.62, 0.76, 1))
        content.add_widget(btn)

        popup = Popup(title='Error', content=content, size_hint=(0.9, 0.4))
        btn.bind(on_press=popup.dismiss)
        popup.open()


if __name__ == '__main__':
    TobyApp().run()
