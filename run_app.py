#!/usr/bin/env python3
"""
Universal File Converter - Launcher Script
-----------------------------------------
This script launches the Universal File Converter app.
"""

import os
import sys
from kivy.resources import resource_add_path

if __name__ == '__main__':
    # Make sure we're in the right directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    # Add the current directory to the path so Kivy can find resources
    resource_add_path(os.path.abspath('.'))
    
    # Import and run the app
    from main import FileConverterApp
    FileConverterApp().run()