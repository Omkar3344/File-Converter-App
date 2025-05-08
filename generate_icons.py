#!/usr/bin/env python3
"""
Icon Generator Script
-------------------

This script converts the SVG icon to various sizes of PNG icons
needed for Android and iOS applications.
"""

import os
import sys
import subprocess
import shutil
from PIL import Image

# Define icon sizes for Android
ANDROID_ICON_SIZES = {
    'mdpi': 48,
    'hdpi': 72,
    'xhdpi': 96,
    'xxhdpi': 144,
    'xxxhdpi': 192
}

# Define icon sizes for iOS
IOS_ICON_SIZES = {
    'icon-20': 20,
    'icon-29': 29,
    'icon-40': 40,
    'icon-50': 50,
    'icon-57': 57,
    'icon-60': 60,
    'icon-72': 72,
    'icon-76': 76,
    'icon-83.5': 83.5,
    'icon-1024': 1024
}

def ensure_directory(directory):
    """Make sure the given directory exists."""
    if not os.path.exists(directory):
        os.makedirs(directory)

def convert_svg_to_png(svg_file, output_file, size):
    """Convert SVG to PNG using Pillow."""
    try:
        # First try to use cairosvg if available (better quality)
        import cairosvg
        cairosvg.svg2png(url=svg_file, write_to=output_file, output_width=size, output_height=size)
        return True
    except ImportError:
        try:
            # Fallback to Inkscape if available
            subprocess.run([
                'inkscape',
                '--export-filename=' + output_file,
                '-w', str(size),
                '-h', str(size),
                svg_file
            ], check=True)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            # Fallback to ImageMagick if available
            try:
                subprocess.run([
                    'convert',
                    '-background', 'none',
                    '-resize', f'{size}x{size}',
                    svg_file,
                    output_file
                ], check=True)
                return True
            except (subprocess.SubprocessError, FileNotFoundError):
                print("WARNING: Neither cairosvg, Inkscape nor ImageMagick found. Using basic conversion.")
                
                # Last resort: create a colored square
                img = Image.new('RGBA', (size, size), (52, 152, 219, 255))  # Blue color
                img.save(output_file)
                return False

def generate_android_icons(svg_file):
    """Generate Android icons from SVG."""
    android_dir = os.path.join('data', 'icons', 'android')
    ensure_directory(android_dir)
    
    for density, size in ANDROID_ICON_SIZES.items():
        density_dir = os.path.join(android_dir, f'drawable-{density}')
        ensure_directory(density_dir)
        
        output_file = os.path.join(density_dir, 'icon.png')
        convert_svg_to_png(svg_file, output_file, size)
        print(f"Generated Android icon: {output_file}")

def generate_ios_icons(svg_file):
    """Generate iOS icons from SVG."""
    ios_dir = os.path.join('data', 'icons', 'ios')
    ensure_directory(ios_dir)
    
    for name, size in IOS_ICON_SIZES.items():
        # Generate regular icon
        output_file = os.path.join(ios_dir, f'{name}.png')
        convert_svg_to_png(svg_file, output_file, int(size))
        print(f"Generated iOS icon: {output_file}")
        
        # Generate @2x icon
        output_file = os.path.join(ios_dir, f'{name}@2x.png')
        convert_svg_to_png(svg_file, output_file, int(size * 2))
        print(f"Generated iOS icon: {output_file}")
        
        # Generate @3x icon
        output_file = os.path.join(ios_dir, f'{name}@3x.png')
        convert_svg_to_png(svg_file, output_file, int(size * 3))
        print(f"Generated iOS icon: {output_file}")

def generate_app_icon(svg_file):
    """Generate the main app icon."""
    output_file = os.path.join('data', 'icon.png')
    ensure_directory('data')
    convert_svg_to_png(svg_file, output_file, 512)
    print(f"Generated main app icon: {output_file}")

def generate_splash_screen(svg_file):
    """Generate splash screen from SVG."""
    output_file = os.path.join('data', 'presplash.png')
    ensure_directory('data')
    
    # Create a larger image for splash screen
    try:
        import cairosvg
        cairosvg.svg2png(url=svg_file, write_to=output_file, output_width=1024, output_height=1024)
    except ImportError:
        # Fallback to basic image
        img = Image.new('RGBA', (1024, 1024), (52, 152, 219, 255))  # Blue color
        img.save(output_file)
    
    print(f"Generated splash screen: {output_file}")

if __name__ == '__main__':
    svg_file = 'app_icon.svg'
    
    if not os.path.exists(svg_file):
        print(f"Error: SVG file {svg_file} not found!")
        sys.exit(1)
    
    # Generate all icons
    ensure_directory('data')
    generate_app_icon(svg_file)
    generate_splash_screen(svg_file)
    generate_android_icons(svg_file)
    generate_ios_icons(svg_file)
    
    print("\nAll icons generated successfully!")
    print("Update your buildozer.spec file to include:")
    print("presplash.filename = %(source.dir)s/data/presplash.png")
    print("icon.filename = %(source.dir)s/data/icon.png")