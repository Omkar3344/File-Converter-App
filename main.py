from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.progressbar import ProgressBar
from kivy.core.window import Window
from kivy.utils import platform
from kivy.clock import Clock

import os
import threading
from converters import get_available_formats, convert_file

class FileConverterApp(App):
    def build(self):
        # Set up the main layout
        self.title = 'Universal File Converter'
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title
        title_label = Label(
            text='Universal File Converter',
            font_size='20sp',
            size_hint_y=None,
            height=50
        )
        main_layout.add_widget(title_label)
        
        # File chooser
        self.file_chooser = FileChooserListView(
            path=self.get_default_path(),
            size_hint_y=0.7
        )
        main_layout.add_widget(self.file_chooser)
        
        # Selected file info
        self.selected_file_label = Label(text='No file selected', size_hint_y=None, height=30)
        main_layout.add_widget(self.selected_file_label)
        
        # Format selection
        formats_layout = BoxLayout(size_hint_y=None, height=50)
        formats_layout.add_widget(Label(text='Convert to:'))
        self.format_spinner = Spinner(
            text='Select format',
            values=['Select a file first'],
            size_hint_x=0.7
        )
        formats_layout.add_widget(self.format_spinner)
        main_layout.add_widget(formats_layout)
        
        # Progress bar
        self.progress_bar = ProgressBar(max=100, value=0, size_hint_y=None, height=30)
        main_layout.add_widget(self.progress_bar)
        
        # Status label
        self.status_label = Label(text='Ready', size_hint_y=None, height=30)
        main_layout.add_widget(self.status_label)
        
        # Convert button
        self.convert_button = Button(
            text='Convert',
            size_hint_y=None,
            height=50,
            disabled=True
        )
        self.convert_button.bind(on_press=self.on_convert_pressed)
        main_layout.add_widget(self.convert_button)
        
        # Bind file selection
        self.file_chooser.bind(selection=self.on_file_selected)
        
        return main_layout
    
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
            self.selected_file_label.text = f'Selected: {os.path.basename(selected_file)}'
            
            # Get available output formats for this file type
            file_ext = os.path.splitext(selected_file)[1].lower()
            formats = get_available_formats(file_ext)
            
            if formats:
                self.format_spinner.values = formats
                self.format_spinner.text = formats[0]
                self.convert_button.disabled = False
            else:
                self.format_spinner.values = ['Unsupported file type']
                self.format_spinner.text = 'Unsupported file type'
                self.convert_button.disabled = True
    
    def on_convert_pressed(self, instance):
        # Start conversion process
        if not self.file_chooser.selection:
            self.status_label.text = 'Please select a file first'
            return
        
        source_file = self.file_chooser.selection[0]
        target_format = self.format_spinner.text
        
        if target_format == 'Select format' or target_format == 'Unsupported file type':
            self.status_label.text = 'Please select a valid output format'
            return
        
        # Start conversion in a separate thread
        self.convert_button.disabled = True
        self.status_label.text = 'Converting...'
        self.progress_bar.value = 0
        
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
        Clock.schedule_once(lambda dt: setattr(self.progress_bar, 'value', percent), 0)
    
    def conversion_completed(self, success, output_file):
        """Handle conversion completion."""
        self.convert_button.disabled = False
        if success:
            self.status_label.text = f'Conversion complete: {os.path.basename(output_file)}'
            self.progress_bar.value = 100
        else:
            self.status_label.text = 'Conversion failed'
    
    def conversion_failed(self, error_message):
        """Handle conversion failure."""
        self.convert_button.disabled = False
        self.status_label.text = f'Error: {error_message}'

if __name__ == '__main__':
    FileConverterApp().run()