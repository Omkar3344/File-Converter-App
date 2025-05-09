from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.utils import platform
from kivy.clock import Clock
from kivy.properties import StringProperty, BooleanProperty, ColorProperty
from kivy.metrics import dp
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.image import Image
from kivy.animation import Animation
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.uix.image import AsyncImage
from kivy.factory import Factory
from kivy.graphics import Color, Rectangle

import os
import threading
import shutil
import subprocess
from converters import get_available_formats, convert_file
import time
import json

# Set default window size for desktop
if platform not in ('android', 'ios'):
    Window.size = (400, 700)

class DrawerLayout(BoxLayout):
    """Custom navigation drawer implementation"""
    
    def open_drawer(self):
        """Open the drawer with animation"""
        anim = Animation(x=0, d=0.2)
        anim.start(self)
    
    def close_drawer(self):
        """Close the drawer with animation"""
        anim = Animation(x=-self.width, d=0.2)
        anim.start(self)
    
    def on_touch_down(self, touch):
        """Handle touch events to close drawer when clicking outside"""
        if self.collide_point(*touch.pos):
            return super(DrawerLayout, self).on_touch_down(touch)
        
        # Close drawer if it's open and user clicks outside
        if self.x > -self.width:
            self.close_drawer()
            return True
        
        return False

# Register DrawerLayout class with Kivy
Factory.register('DrawerLayout', cls=DrawerLayout)

class IconButton(ButtonBehavior, AsyncImage):
    """Custom button with icon"""
    def __init__(self, **kwargs):
        super(IconButton, self).__init__(**kwargs)
        self.size_hint = (None, None)
        self.size = (dp(48), dp(48))

class SuccessPopup(Popup):
    result_text = StringProperty("")
    
    def __init__(self, result_text, converted_file, **kwargs):
        super(SuccessPopup, self).__init__(**kwargs)
        self.result_text = result_text
        self.converted_file = converted_file
        self.background_color = [0.2, 0.7, 0.2, 0.9]  # Green background
    
    def download_file(self):
        if hasattr(App.get_running_app().root, 'download_converted_file'):
            App.get_running_app().root.download_converted_file(self.converted_file)
        self.dismiss()

class ErrorPopup(Popup):
    error_text = StringProperty("")
    
    def __init__(self, error_text, **kwargs):
        super(ErrorPopup, self).__init__(**kwargs)
        self.error_text = error_text
        self.background_color = [0.8, 0.2, 0.2, 0.9]  # Red background

class DownloadSuccessPopup(Popup):
    download_text = StringProperty("")
    
    def __init__(self, download_text, **kwargs):
        super(DownloadSuccessPopup, self).__init__(**kwargs)
        self.download_text = download_text
        self.background_color = [0.2, 0.5, 0.8, 0.9]  # Blue background

class SettingsScreen(Screen):
    dark_mode = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super(SettingsScreen, self).__init__(**kwargs)
        self.load_settings()
    
    def toggle_dark_mode(self):
        self.dark_mode = not self.dark_mode
        app = App.get_running_app()
        app.update_theme(self.dark_mode)
        self.save_settings()
    
    def load_settings(self):
        try:
            if os.path.exists('settings.json'):
                with open('settings.json', 'r') as f:
                    settings = json.load(f)
                    self.dark_mode = settings.get('dark_mode', False)
        except Exception:
            # If error loading settings, use defaults
            pass
    
    def save_settings(self):
        try:
            with open('settings.json', 'w') as f:
                json.dump({'dark_mode': self.dark_mode}, f)
        except Exception:
            # If error saving settings, just continue
            pass

class RecentFilesScreen(Screen):
    def __init__(self, **kwargs):
        super(RecentFilesScreen, self).__init__(**kwargs)
        self.recent_files = []
        self.load_recent_files()
    
    def load_recent_files(self):
        try:
            if os.path.exists('recent_files.json'):
                with open('recent_files.json', 'r') as f:
                    self.recent_files = json.load(f)
                    self.update_list()
        except Exception:
            # If error loading, use empty list
            self.recent_files = []
    
    def add_recent_file(self, file_path, output_path=None):
        # Add to recent files list
        file_entry = {
            'input': file_path,
            'output': output_path,
            'date': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # Remove existing entry if present
        self.recent_files = [f for f in self.recent_files if f.get('input') != file_path]
        
        # Add to the top of the list
        self.recent_files.insert(0, file_entry)
        
        # Keep only the last 20 files
        self.recent_files = self.recent_files[:20]
        
        # Save and update
        self.save_recent_files()
        self.update_list()
    
    def save_recent_files(self):
        try:
            with open('recent_files.json', 'w') as f:
                json.dump(self.recent_files, f)
        except Exception:
            # If error saving, continue
            pass
    
    def update_list(self):
        # Clear existing widgets
        list_container = self.ids.recent_files_list
        list_container.clear_widgets()
        
        if not self.recent_files:
            no_files_label = Label(
                text='No recent files',
                size_hint_y=None,
                height=dp(50)
            )
            list_container.add_widget(no_files_label)
            return
        
        # Add each recent file
        for file_entry in self.recent_files:
            file_path = file_entry.get('input', '')
            date = file_entry.get('date', '')
            
            # Create file item layout
            item = BoxLayout(
                orientation='vertical',
                size_hint_y=None,
                height=dp(80),
                padding=[dp(10), dp(5)],
                spacing=dp(2)
            )
            
            # Add filename label
            name_label = Label(
                text=os.path.basename(file_path),
                size_hint_y=None,
                height=dp(30),
                halign='left',
                valign='middle',
                text_size=(Window.width - dp(20), dp(30)),
                shorten=True,
                shorten_from='right'
            )
            item.add_widget(name_label)
            
            # Add path and date
            info_layout = BoxLayout(
                size_hint_y=None,
                height=dp(20)
            )
            
            path_label = Label(
                text=os.path.dirname(file_path),
                size_hint_x=0.7,
                font_size='12sp',
                halign='left',
                valign='middle',
                text_size=(Window.width * 0.7 - dp(20), dp(20)),
                shorten=True,
                shorten_from='right',
                color=[0.7, 0.7, 0.7, 1]
            )
            
            date_label = Label(
                text=date,
                size_hint_x=0.3,
                font_size='12sp',
                halign='right',
                valign='middle',
                text_size=(Window.width * 0.3 - dp(20), dp(20)),
                color=[0.7, 0.7, 0.7, 1]
            )
            
            info_layout.add_widget(path_label)
            info_layout.add_widget(date_label)
            item.add_widget(info_layout)
            
            # Add buttons
            button_layout = BoxLayout(
                size_hint_y=None,
                height=dp(30),
                spacing=dp(10)
            )
            
            open_btn = Button(
                text='Open again',
                size_hint_x=0.7
            )
            open_btn.bind(on_press=lambda btn, path=file_path: self.open_file(path))
            
            button_layout.add_widget(open_btn)
            
            if file_entry.get('output'):
                view_btn = Button(
                    text='View output',
                    size_hint_x=0.3
                )
                view_btn.bind(on_press=lambda btn, path=file_entry.get('output'): self.view_output(path))
                button_layout.add_widget(view_btn)
            
            item.add_widget(button_layout)
            
            # Create a proper separator
            separator = BoxLayout(
                size_hint_y=None,
                height=dp(1),
                padding=[dp(5), 0]
            )
            
            # Add color to the separator using canvas instructions
            with separator.canvas:
                Color(0.3, 0.3, 0.3, 0.2)
                Rectangle(pos=separator.pos, size=separator.size)
            
            # Add to list
            list_container.add_widget(item)
            list_container.add_widget(separator)
    
    def open_file(self, file_path):
        # Check if file exists
        if os.path.exists(file_path):
            # Send to main screen for conversion
            app = App.get_running_app()
            app.root.select_file(file_path)
            app.root.current = 'converter'
            app.update_nav_buttons('converter')
        else:
            # Show error popup
            error_popup = ErrorPopup(error_text=f"File no longer exists: {file_path}")
            error_popup.open()
    
    def view_output(self, file_path):
        # Check if file exists
        if os.path.exists(file_path):
            # Try to open the file
            if platform == 'android':
                # For Android, use Android's built-in file viewer
                from android.storage import primary_external_storage_path
                from jnius import autoclass
                Intent = autoclass('android.content.Intent')
                File = autoclass('java.io.File')
                Uri = autoclass('android.net.Uri')
                PythonActivity = autoclass('org.kivy.android.PythonActivity')
                
                file_obj = File(file_path)
                uri = Uri.fromFile(file_obj)
                intent = Intent()
                intent.setAction(Intent.ACTION_VIEW)
                intent.setDataAndType(uri, self.get_mime_type(file_path))
                
                current_activity = PythonActivity.mActivity
                current_activity.startActivity(intent)
            else:
                # For desktop, use default application
                if platform == 'win':
                    os.startfile(file_path)
                elif platform == 'macosx':
                    subprocess.call(['open', file_path])
                else:  # Linux
                    subprocess.call(['xdg-open', file_path])
        else:
            # Show error popup
            error_popup = ErrorPopup(error_text=f"Output file no longer exists: {file_path}")
            error_popup.open()
    
    def get_mime_type(self, file_path):
        """Get MIME type for file."""
        extension = os.path.splitext(file_path)[1].lower()
        
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.bmp': 'image/bmp',
            '.webp': 'image/webp',
            '.pdf': 'application/pdf',
            '.txt': 'text/plain',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.xls': 'application/vnd.ms-excel',
            '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            '.csv': 'text/csv',
            '.mp3': 'audio/mpeg',
            '.mp4': 'video/mp4',
            '.zip': 'application/zip'
        }
        
        return mime_types.get(extension, 'application/octet-stream')

class HelpScreen(Screen):
    pass

class FileConverterScreen(Screen):
    def __init__(self, **kwargs):
        super(FileConverterScreen, self).__init__(**kwargs)
        self.current_output_file = None
        self.selected_file_path = None
        # Setup drag and drop handling
        Window.bind(on_dropfile=self._on_file_drop)
    
    def _on_file_drop(self, window, file_path):
        """Handle files dropped onto the window"""
        # In Python 3, file_path is bytes, so decode it
        if isinstance(file_path, bytes):
            file_path = file_path.decode('utf-8')
        
        # Process the file
        self.select_file(file_path)
        return True
    
    def open_file_picker(self):
        """Open the native file picker dialog"""
        if platform == 'android':
            self._open_android_file_picker()
        elif platform == 'ios':
            # On iOS, this would require more complex setup
            # For now, just show info about limitation
            popup = Popup(
                title='iOS Limitation',
                content=Label(text='File picking on iOS requires additional setup. Please use a different platform.'),
                size_hint=(0.8, 0.4)
            )
            popup.open()
        else:
            self._open_desktop_file_picker()
    
    def _open_desktop_file_picker(self):
        """Open native file picker on desktop platforms"""
        try:
            import tkinter as tk
            from tkinter import filedialog
            
            # Create and hide root Tkinter window
            root = tk.Tk()
            root.withdraw()
            
            # Show file dialog and get selected file
            file_path = filedialog.askopenfilename(
                title="Select a file to convert",
                filetypes=[
                    ("All supported files", "*.*"),
                    ("Images", "*.jpg *.jpeg *.png *.bmp *.webp *.gif"),
                    ("Documents", "*.pdf *.docx *.txt"),
                    ("Data files", "*.csv *.xlsx *.json")
                ]
            )
            
            # Process the selected file
            if file_path:
                self.select_file(file_path)
            
            # Close Tkinter
            root.destroy()
        
        except Exception as e:
            self.ids.status_label.text = f"Error opening file picker: {str(e)}"
    
    def _open_android_file_picker(self):
        """Open native file picker on Android"""
        try:
            from android.storage import primary_external_storage_path
            from android import activity
            from jnius import autoclass
            
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            
            # Create intent for opening document
            intent = Intent(Intent.ACTION_OPEN_DOCUMENT)
            intent.addCategory(Intent.CATEGORY_OPENABLE)
            intent.setType("*/*")  # All file types
            
            # Set up activity result handling
            def on_activity_result(request_code, result_code, data):
                if result_code == -1:  # RESULT_OK
                    uri = data.getData()
                    # Get real file path from URI
                    file_path = self._get_file_path_from_uri(uri)
                    if file_path:
                        self.select_file(file_path)
                    else:
                        self.ids.status_label.text = "Could not access the selected file"
            
            # Register the callback
            activity.bind(on_activity_result=on_activity_result)
            
            # Start the intent activity
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            current_activity = PythonActivity.mActivity
            current_activity.startActivityForResult(intent, 0)
            
        except Exception as e:
            self.ids.status_label.text = f"Error opening file picker: {str(e)}"
    
    def _get_file_path_from_uri(self, uri):
        """Convert Android URI to file path - basic implementation"""
        try:
            from jnius import autoclass
            from android.storage import primary_external_storage_path
            
            ContentResolver = autoclass('android.content.ContentResolver')
            Cursor = autoclass('android.database.Cursor')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            
            cr = PythonActivity.mActivity.getContentResolver()
            cursor = cr.query(uri, ["_data"], None, None, None)
            
            if cursor is not None and cursor.moveToFirst():
                idx = cursor.getColumnIndex("_data")
                if idx != -1:
                    file_path = cursor.getString(idx)
                    cursor.close()
                    return file_path
                cursor.close()
            
            # Fallback: try to copy file to app's storage
            try:
                import os
                import time
                
                # Create temp directory if needed
                temp_dir = os.path.join(primary_external_storage_path(), 'temp_files')
                if not os.path.exists(temp_dir):
                    os.makedirs(temp_dir)
                
                # Generate unique filename
                file_name = f"converted_file_{int(time.time())}"
                temp_file = os.path.join(temp_dir, file_name)
                
                # Copy the file
                input_stream = cr.openInputStream(uri)
                with open(temp_file, 'wb') as f:
                    while True:
                        buffer = input_stream.read(4096)
                        if not buffer:
                            break
                        f.write(buffer)
                input_stream.close()
                
                return temp_file
            except:
                return None
                
        except Exception:
            return None
    
    def select_file(self, file_path):
        """Process the selected file"""
        if os.path.exists(file_path):
            self.selected_file_path = file_path
            self.ids.selected_file_label.text = f'Selected: {os.path.basename(file_path)}'
            
            # Animate the label
            anim = Animation(opacity=0, duration=0.1) + Animation(opacity=1, duration=0.1)
            anim.start(self.ids.selected_file_label)
            
            # Get available output formats for this file type
            file_ext = os.path.splitext(file_path)[1].lower()
            formats = get_available_formats(file_ext)
            
            if formats:
                self.ids.format_spinner.values = formats
                self.ids.format_spinner.text = formats[0]
                self.ids.convert_button.disabled = False
                
                # Enable animation when enabling the button
                anim = Animation(background_color=[0.2, 0.7, 0.3, 1], duration=0.3)
                anim.start(self.ids.convert_button)
            else:
                self.ids.format_spinner.values = ['Unsupported file type']
                self.ids.format_spinner.text = 'Unsupported file type'
                self.ids.convert_button.disabled = True
                
                # Animate the button to red to indicate disabled state
                anim = Animation(background_color=[0.7, 0.2, 0.2, 1], duration=0.3)
                anim.start(self.ids.convert_button)
            
            # Disable download button when a new file is selected
            self.ids.download_button.disabled = True
            self.current_output_file = None
            
            # Add to recent files
            if hasattr(App.get_running_app().root, 'recent_files_screen'):
                App.get_running_app().root.recent_files_screen.add_recent_file(file_path)
        else:
            self.ids.status_label.text = f"File not found: {file_path}"
    
    def on_convert_pressed(self):
        # Start conversion process
        if not self.selected_file_path:
            self.ids.status_label.text = 'Please select a file first'
            
            # Shake animation for status label
            shake = Animation(x=self.ids.status_label.x - 5, duration=0.05) + \
                   Animation(x=self.ids.status_label.x + 5, duration=0.05) + \
                   Animation(x=self.ids.status_label.x, duration=0.05)
            shake.repeat = 2
            shake.start(self.ids.status_label)
            return
        
        source_file = self.selected_file_path
        target_format = self.ids.format_spinner.text
        
        if target_format == 'Select format' or target_format == 'Unsupported file type':
            self.ids.status_label.text = 'Please select a valid output format'
            
            # Shake animation for spinner
            shake = Animation(x=self.ids.format_spinner.x - 5, duration=0.05) + \
                   Animation(x=self.ids.format_spinner.x + 5, duration=0.05) + \
                   Animation(x=self.ids.format_spinner.x, duration=0.05)
            shake.repeat = 2
            shake.start(self.ids.format_spinner)
            return
        
        # Start conversion in a separate thread
        self.ids.convert_button.disabled = True
        self.ids.download_button.disabled = True
        self.ids.status_label.text = 'Converting...'
        self.ids.progress_bar.value = 0
        
        # Animate the progress bar
        anim = Animation(opacity=1, duration=0.3)
        anim.start(self.ids.progress_bar)
        
        # Start conversion thread
        conversion_thread = threading.Thread(
            target=self.run_conversion,
            args=(source_file, target_format)
        )
        conversion_thread.daemon = True
        conversion_thread.start()
    
    def run_conversion(self, source_file, target_format):
        """Run the conversion process in a background thread."""
        try:
            # Generate output filename
            base_name = os.path.splitext(source_file)[0]
            output_file = f"{base_name}.{target_format}"
            
            # Start conversion
            success = convert_file(
                source_file, 
                output_file, 
                progress_callback=self.update_progress
            )
            
            # Update UI on main thread
            Clock.schedule_once(lambda dt: self.conversion_completed(success, output_file), 0)
        except Exception as e:
            Clock.schedule_once(lambda dt: self.conversion_failed(str(e)), 0)
    
    def update_progress(self, percent):
        """Update progress bar (called from the conversion thread)."""
        Clock.schedule_once(lambda dt: setattr(self.ids.progress_bar, 'value', percent), 0)
    
    def conversion_completed(self, success, output_file):
        """Handle conversion completion."""
        self.ids.convert_button.disabled = False
        if success:
            self.current_output_file = output_file
            self.ids.status_label.text = f'Conversion complete: {os.path.basename(output_file)}'
            self.ids.progress_bar.value = 100
            self.ids.download_button.disabled = False
            
            # Enable animation for download button
            anim = Animation(background_color=[0.2, 0.3, 0.8, 1], duration=0.3)
            anim.start(self.ids.download_button)
            
            # Show success popup
            result_text = f"Successfully converted to:\n{os.path.basename(output_file)}"
            popup = SuccessPopup(result_text=result_text, converted_file=output_file)
            popup.open()
            
            # Add to recent files with output
            if hasattr(App.get_running_app().root, 'recent_files_screen'):
                source_file = self.selected_file_path
                App.get_running_app().root.recent_files_screen.add_recent_file(source_file, output_file)
        else:
            self.ids.status_label.text = 'Conversion failed'
            self.ids.download_button.disabled = True
            self.current_output_file = None
    
    def conversion_failed(self, error_message):
        """Handle conversion failure."""
        self.ids.convert_button.disabled = False
        self.ids.status_label.text = f'Error: {error_message}'
        self.ids.download_button.disabled = True
        self.current_output_file = None
        
        # Show error popup
        popup = ErrorPopup(error_text=f"Conversion failed: {error_message}")
        popup.open()
    
    def on_download_pressed(self):
        """Handle download button press."""
        if self.current_output_file and os.path.exists(self.current_output_file):
            self.download_converted_file(self.current_output_file)
        else:
            self.ids.status_label.text = 'No converted file available'
            
            # Shake animation
            shake = Animation(x=self.ids.download_button.x - 5, duration=0.05) + \
                   Animation(x=self.ids.download_button.x + 5, duration=0.05) + \
                   Animation(x=self.ids.download_button.x, duration=0.05)
            shake.repeat = 2
            shake.start(self.ids.download_button)
    
    def download_converted_file(self, file_path):
        """Copy the converted file to the downloads directory."""
        try:
            # Determine download directory based on platform
            if platform == 'android':
                download_dir = '/storage/emulated/0/Download'
            elif platform == 'ios':
                download_dir = os.path.join(os.path.expanduser('~'), 'Documents')
            else:
                download_dir = os.path.join(os.path.expanduser('~'), 'Downloads')
            
            # Create the directory if it doesn't exist
            os.makedirs(download_dir, exist_ok=True)
            
            # Generate the destination path
            file_name = os.path.basename(file_path)
            destination = os.path.join(download_dir, file_name)
            
            # Copy the file to the download directory
            shutil.copy2(file_path, destination)
            
            # Update status
            self.ids.status_label.text = f'Downloaded to: {destination}'
            
            # Show download success popup
            download_text = f"File downloaded to:\n{destination}"
            popup = DownloadSuccessPopup(download_text=download_text)
            popup.open()
            
            # Try to open the downloads folder
            self.open_folder(download_dir)
            
        except Exception as e:
            self.ids.status_label.text = f'Download failed: {str(e)}'
            
            # Show error popup
            popup = ErrorPopup(error_text=f"Download failed: {str(e)}")
            popup.open()
    
    def open_folder(self, folder_path):
        """Open the folder containing the downloaded file."""
        try:
            if platform == 'win':
                os.startfile(folder_path)
            elif platform == 'macosx':
                subprocess.Popen(['open', folder_path])
            elif platform == 'linux':
                subprocess.Popen(['xdg-open', folder_path])
            # For mobile platforms, we don't need to do anything as the file is already in an accessible location
        except:
            # Silently ignore any errors when trying to open the folder
            pass

class FileConverterApp(App):
    theme_bg_color = ColorProperty([0.95, 0.95, 0.95, 1])
    theme_text_color = ColorProperty([0.1, 0.1, 0.1, 1])
    theme_accent_color = ColorProperty([0.2, 0.7, 0.3, 1])
    is_dark_mode = BooleanProperty(False)
    
    def build(self):
        self.title = 'Universal File Converter'
        self.icon = 'data/icon.png'
        
        # Create screen manager
        sm = ScreenManager()
        
        # Add converter screen
        converter_screen = FileConverterScreen(name='converter')
        sm.add_widget(converter_screen)
        
        # Add settings screen
        settings_screen = SettingsScreen(name='settings')
        sm.add_widget(settings_screen)
        
        # Add recent files screen
        recent_files_screen = RecentFilesScreen(name='recent')
        sm.add_widget(recent_files_screen)
        sm.recent_files_screen = recent_files_screen
        
        # Add help screen
        help_screen = HelpScreen(name='help')
        sm.add_widget(help_screen)
        
        # Apply theme based on settings
        self.update_theme(settings_screen.dark_mode)
        
        return sm
    
    def update_theme(self, dark_mode):
        self.is_dark_mode = dark_mode
        if dark_mode:
            self.theme_bg_color = [0.12, 0.12, 0.12, 1]
            self.theme_text_color = [0.95, 0.95, 0.95, 1]
            self.theme_accent_color = [0.3, 0.8, 0.4, 1]
        else:
            self.theme_bg_color = [0.95, 0.95, 0.95, 1]
            self.theme_text_color = [0.1, 0.1, 0.1, 1]
            self.theme_accent_color = [0.2, 0.7, 0.3, 1]
    
    def update_nav_buttons(self, active_screen):
        """Update navigation drawer button colors based on active screen"""
        # This method will be called after the root is initialized
        if not self.root or not hasattr(self.root.ids, 'drawer'):
            # Root not ready yet
            return
            
        try:
            drawer = self.root.ids.drawer
            if not drawer or not hasattr(drawer.ids, 'nav_content'):
                return
                
            # Get the NavigationDrawer
            nav = drawer.ids.nav_content
            
            # Set active/inactive colors
            active_color = [0.3, 0.6, 0.3, 1]
            inactive_color = [0.4, 0.4, 0.4, 1]
            
            # Update buttons 
            if hasattr(nav.ids, 'converter_btn'):
                nav.ids.converter_btn.background_color = active_color if active_screen == 'converter' else inactive_color
                
            if hasattr(nav.ids, 'recent_btn'):
                nav.ids.recent_btn.background_color = active_color if active_screen == 'recent' else inactive_color
                
            if hasattr(nav.ids, 'settings_btn'):
                nav.ids.settings_btn.background_color = active_color if active_screen == 'settings' else inactive_color
                
            if hasattr(nav.ids, 'help_btn'):
                nav.ids.help_btn.background_color = active_color if active_screen == 'help' else inactive_color
        except Exception as e:
            # Ignore any errors when trying to update nav buttons
            print(f"Error updating nav buttons: {e}")
            pass
    
    def on_start(self):
        """Called when the application is started"""
        # Initialize navigation buttons
        Clock.schedule_once(lambda dt: self.update_nav_buttons('converter'), 0.5)

if __name__ == '__main__':
    FileConverterApp().run()