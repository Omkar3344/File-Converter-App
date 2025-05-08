import os
import sys

# Check if icons exist, create them if they don't
if not os.path.exists(os.path.join('data', 'icon.png')):
    print("Icons not found. Creating icons first...")
    try:
        # Try importing Pillow which is needed for create_icons.py
        from PIL import Image, ImageDraw
        
        # Run the icon creation code
        print("Generating app icons...")
        
        # Import the create_icons module function directly
        from create_icons import ensure_dir, create_icon
        
        # Create data directory
        data_dir = 'data'
        ensure_dir(data_dir)
        
        # Create all necessary icons
        create_icon('icon.png', size=(512, 512), icon_type='app')
        create_icon('menu_icon.png', size=(100, 100), icon_type='menu')
        create_icon('back_icon.png', size=(100, 100), icon_type='back')
        create_icon('refresh_icon.png', size=(100, 100), icon_type='refresh')
        create_icon('success_icon.png', size=(100, 100), icon_type='success')
        create_icon('error_icon.png', size=(100, 100), icon_type='error')
        create_icon('download_icon.png', size=(100, 100), icon_type='download')
        
        print("Icons created successfully!")
    except ImportError:
        print("Warning: Pillow not installed. Cannot create icons automatically.")
        print("Please install Pillow with: pip install pillow")
        print("Or run create_icons.py separately before running this app.")
        print("Continuing without icons, some visual elements may be missing.")

# Now import and run the main app
from main import FileConverterApp

if __name__ == "__main__":
    FileConverterApp().run()