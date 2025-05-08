"""
Quick icon generator for File Converter App
"""
from PIL import Image, ImageDraw
import os

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

# Create data directory
data_dir = 'data'
ensure_dir(data_dir)

# Function to create simple icons
def create_icon(filename, size=(100, 100), bg_color=(52, 152, 219), icon_type='app'):
    img = Image.new('RGBA', size, color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Draw background
    if icon_type == 'app':
        # App icon (rounded rectangle)
        draw.rectangle([(10, 10), (size[0]-10, size[1]-10)], fill=bg_color, outline=(255, 255, 255), width=3)
        # Draw document icon
        draw.rectangle([(30, 25), (size[0]-30, size[1]-35)], fill=(255, 255, 255))
        # Draw arrow
        draw.polygon([(40, size[1]//2), (size[0]-40, size[1]//2), (size[0]//2, size[1]-25)], fill=(46, 204, 113))
    
    elif icon_type == 'menu':
        # Menu icon (three lines)
        for i in range(3):
            y = 25 + i * 20
            draw.rectangle([(20, y), (80, y+10)], fill=bg_color)
    
    elif icon_type == 'back':
        # Back icon (left arrow)
        draw.polygon([(70, 20), (30, 50), (70, 80)], fill=bg_color)
    
    elif icon_type == 'refresh':
        # Refresh icon (circle with arrow)
        draw.arc([(20, 20), (80, 80)], 60, 380, fill=bg_color, width=10)
        draw.polygon([(70, 25), (85, 40), (55, 45)], fill=bg_color)
    
    elif icon_type == 'success':
        # Success icon (checkmark)
        draw.ellipse([(10, 10), (90, 90)], fill=(46, 204, 113))
        draw.line([(30, 50), (45, 65), (75, 35)], fill=(255, 255, 255), width=8)
    
    elif icon_type == 'error':
        # Error icon (X)
        draw.ellipse([(10, 10), (90, 90)], fill=(231, 76, 60))
        draw.line([(30, 30), (70, 70)], fill=(255, 255, 255), width=8)
        draw.line([(30, 70), (70, 30)], fill=(255, 255, 255), width=8)
    
    elif icon_type == 'download':
        # Download icon
        draw.ellipse([(10, 10), (90, 90)], fill=(52, 152, 219))
        draw.polygon([(50, 30), (50, 60), (35, 50), (50, 70), (65, 50), (50, 60)], fill=(255, 255, 255))
        draw.rectangle([(30, 75), (70, 85)], fill=(255, 255, 255))
    
    # Save the icon
    img.save(os.path.join(data_dir, filename))
    print(f"Created {filename}")

# Create all necessary icons
create_icon('icon.png', size=(512, 512), icon_type='app')
create_icon('menu_icon.png', size=(100, 100), icon_type='menu')
create_icon('back_icon.png', size=(100, 100), icon_type='back')
create_icon('refresh_icon.png', size=(100, 100), icon_type='refresh')
create_icon('success_icon.png', size=(100, 100), icon_type='success')
create_icon('error_icon.png', size=(100, 100), icon_type='error')
create_icon('download_icon.png', size=(100, 100), icon_type='download')

print("All icons created successfully!")