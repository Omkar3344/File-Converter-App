from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.core.window import Window
from kivy.utils import platform
from kivy.clock import Clock
from kivy.properties import StringProperty

import os
import threading
import shutil
import subprocess
from converters import get_available_formats, convert_file

class SuccessPopup(Popup):
    result_text = StringProperty("")
    
    def __init__(self, result_text, converted_file, **kwargs):
        super(SuccessPopup, self).__init__(**kwargs)
        self.result_text = result_text
        self.converted_file = converted_file
    
    def download_file(self):
        if hasattr(App.get_running_app().root, 'download_converted_file'):
            App.get_running_app().root.download_converted_file(self.converted_file)
        self.dismiss()

class ErrorPopup(Popup):
    error_text = StringProperty("")
    
    def __init__(self, error_text, **kwargs):
        super(ErrorPopup, self).__init__(**kwargs)
        self.error_text = error_text

class DownloadSuccessPopup(Popup):
    download_text = StringProperty("")
    
    def __init__(self, download_text, **kwargs):
        super(DownloadSuccessPopup, self).__init__(**kwargs)
        self.download_text = download_text

class FileConverterScreen(BoxLayout):
    def __init__(self, **kwargs):
        super(FileConverterScreen, self).__init__(**kwargs)
        self.current_output_file = None
    
    def get_default_path(self):
        """Return an appropriate default path based on the platform."""
        if platform == 'android':
            return '/storage/emulated/0'  # Android's external storage
        elif platform == 'ios':
            return os.path.expanduser('~/Documents')
        else:
            return os.path.expanduser('~')  # Desktop home directory
    
    def on_file_selected(self, instance, selection):
        """Handle file selection events."""
        if selection:
            selected_file = selection[0]
            self.ids.selected_file_label.text = f'Selected: {os.path.basename(selected_file)}'
            
            # Get available output formats for this file type
            file_ext = os.path.splitext(selected_file)[1].lower()
            formats = get_available_formats(file_ext)
            
            if formats:
                self.ids.format_spinner.values = formats
                self.ids.format_spinner.text = formats[0]
                self.ids.convert_button.disabled = False
            else:
                self.ids.format_spinner.values = ['Unsupported file type']
                self.ids.format_spinner.text = 'Unsupported file type'
                self.ids.convert_button.disabled = True
            
            # Disable download button when a new file is selected
            self.ids.download_button.disabled = True
            self.current_output_file = None
    
    def on_convert_pressed(self):
        # Start conversion process
        if not self.ids.file_chooser.selection:
            self.ids.status_label.text = 'Please select a file first'
            return
        
        source_file = self.ids.file_chooser.selection[0]
        target_format = self.ids.format_spinner.text
        
        if target_format == 'Select format' or target_format == 'Unsupported file type':
            self.ids.status_label.text = 'Please select a valid output format'
            return
        
        # Start conversion in a separate thread
        self.ids.convert_button.disabled = True
        self.ids.download_button.disabled = True
        self.ids.status_label.text = 'Converting...'
        self.ids.progress_bar.value = 0
        
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
            
            # Show success popup
            result_text = f"Successfully converted to:\n{os.path.basename(output_file)}"
            popup = SuccessPopup(result_text=result_text, converted_file=output_file)
            popup.open()
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
    def build(self):
        self.title = 'Universal File Converter'
        return FileConverterScreen()

if __name__ == '__main__':
    FileConverterApp().run()