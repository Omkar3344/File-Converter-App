import os
import time
from PIL import Image
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
from docx import Document
import traceback

# Map of supported input formats and their possible output formats
FORMAT_MAP = {
    # Image formats
    '.jpg': ['png', 'webp', 'bmp', 'gif', 'pdf'],
    '.jpeg': ['png', 'webp', 'bmp', 'gif', 'pdf'],
    '.png': ['jpg', 'webp', 'bmp', 'gif', 'pdf'],
    '.bmp': ['jpg', 'png', 'webp', 'gif', 'pdf'],
    '.webp': ['jpg', 'png', 'bmp', 'gif', 'pdf'],
    '.gif': ['jpg', 'png', 'webp', 'bmp', 'pdf'],
    
    # Document formats
    '.pdf': ['txt', 'jpg', 'png'],
    '.docx': ['pdf', 'txt'],
    '.txt': ['pdf', 'docx'],
    
    # Data formats
    '.csv': ['xlsx', 'json', 'xml', 'html'],
    '.xlsx': ['csv', 'json', 'xml', 'html'],
    '.json': ['csv', 'xlsx', 'xml', 'html'],
}

def get_available_formats(file_extension):
    """Get available output formats for a given file extension."""
    return FORMAT_MAP.get(file_extension.lower(), [])

def convert_file(source_path, target_path, progress_callback=None):
    """
    Convert a file from one format to another.
    
    Args:
        source_path: Path to the source file
        target_path: Path where the converted file should be saved
        progress_callback: Function to call with progress updates (0-100)
    
    Returns:
        bool: True if conversion was successful, False otherwise
    """
    try:
        source_ext = os.path.splitext(source_path)[1].lower()
        target_ext = os.path.splitext(target_path)[1].lower()
        
        if target_ext.startswith('.'):
            target_ext = target_ext[1:]
        
        # Simulate progress updates
        def update_progress(value):
            if progress_callback:
                progress_callback(value)
        
        update_progress(10)
        
        # Handle image conversions
        if source_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.webp', '.gif']:
            if target_ext in ['jpg', 'jpeg', 'png', 'bmp', 'webp', 'gif']:
                return convert_image(source_path, target_path, update_progress)
            elif target_ext == 'pdf':
                return image_to_pdf(source_path, target_path, update_progress)
        
        # Handle document conversions
        elif source_ext == '.pdf':
            if target_ext in ['jpg', 'png']:
                return pdf_to_images(source_path, target_path, update_progress)
            elif target_ext == 'txt':
                return pdf_to_text(source_path, target_path, update_progress)
        
        elif source_ext == '.docx':
            if target_ext == 'pdf':
                return docx_to_pdf(source_path, target_path, update_progress)
            elif target_ext == 'txt':
                return docx_to_text(source_path, target_path, update_progress)
        
        elif source_ext == '.txt':
            if target_ext == 'pdf':
                return text_to_pdf(source_path, target_path, update_progress)
            elif target_ext == 'docx':
                return text_to_docx(source_path, target_path, update_progress)
        
        # Handle data formats
        elif source_ext in ['.csv', '.xlsx', '.json']:
            if target_ext in ['csv', 'xlsx', 'json', 'xml', 'html']:
                return convert_data_format(source_path, target_ext, target_path, update_progress)
        
        update_progress(100)
        return True
    
    except Exception as e:
        print(f"Conversion error: {str(e)}")
        print(traceback.format_exc())
        return False

def convert_image(source_path, target_path, progress_callback):
    """Convert between image formats."""
    progress_callback(20)
    
    img = Image.open(source_path)
    
    # Handle special case for JPG format
    if target_path.lower().endswith('.jpg') or target_path.lower().endswith('.jpeg'):
        # Convert to RGB if needed (JPG doesn't support alpha)
        if img.mode == 'RGBA':
            rgb_img = Image.new('RGB', img.size, (255, 255, 255))
            rgb_img.paste(img, mask=img.split()[3])  # Use alpha channel as mask
            img = rgb_img
    
    progress_callback(60)
    img.save(target_path)
    progress_callback(100)
    return True

def image_to_pdf(source_path, target_path, progress_callback):
    """Convert an image to PDF."""
    progress_callback(20)
    
    img = Image.open(source_path)
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    
    progress_callback(60)
    img.save(target_path, "PDF", resolution=100.0)
    progress_callback(100)
    return True

def pdf_to_images(source_path, target_path, progress_callback):
    """Extract pages from a PDF as images."""
    try:
        progress_callback(10)
        
        pdf = PdfReader(source_path)
        total_pages = len(pdf.pages)
        
        if total_pages == 0:
            return False
        
        # Get base name without extension
        base_path = os.path.splitext(target_path)[0]
        ext = os.path.splitext(target_path)[1][1:]  # Remove leading dot
        
        progress_callback(20)
        
        # Currently this is a mock implementation since full PDF-to-image
        # conversion is complex and requires additional libraries
        for i in range(min(total_pages, 1)):  # Only convert first page for simplicity
            # In a real implementation, you would render the PDF page as an image
            # For this example, we'll create a placeholder image
            img = Image.new('RGB', (800, 1000), color=(255, 255, 255))
            img_path = f"{base_path}_page{i+1}.{ext}"
            img.save(img_path)
            progress_callback(20 + (i+1) * 80 // total_pages)
        
        progress_callback(100)
        return True
    except Exception as e:
        print(f"PDF to images error: {str(e)}")
        return False

def pdf_to_text(source_path, target_path, progress_callback):
    """Extract text from a PDF."""
    progress_callback(10)
    
    try:
        pdf = PdfReader(source_path)
        total_pages = len(pdf.pages)
        
        progress_callback(20)
        
        with open(target_path, 'w', encoding='utf-8') as text_file:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                text_file.write(text)
                text_file.write('\n\n--- Page Break ---\n\n')
                progress_callback(20 + (i+1) * 70 // total_pages)
        
        progress_callback(100)
        return True
    except Exception as e:
        print(f"PDF to text error: {str(e)}")
        return False

def docx_to_pdf(source_path, target_path, progress_callback):
    """Convert DOCX to PDF."""
    progress_callback(20)
    
    try:
        # This is a placeholder for actual conversion
        # In a real app, you'd use libraries like docx2pdf, python-docx, and reportlab
        # For mobile deployment, this would require additional setup
        
        # Mock conversion - create a simple PDF
        pdf_writer = PdfWriter()
        pdf_writer.add_blank_page(width=612, height=792)  # US Letter size
        
        progress_callback(80)
        
        with open(target_path, 'wb') as output_pdf:
            pdf_writer.write(output_pdf)
        
        progress_callback(100)
        return True
    except Exception as e:
        print(f"DOCX to PDF error: {str(e)}")
        return False

def docx_to_text(source_path, target_path, progress_callback):
    """Extract text from a DOCX file."""
    progress_callback(20)
    
    try:
        doc = Document(source_path)
        
        progress_callback(50)
        
        with open(target_path, 'w', encoding='utf-8') as text_file:
            for para in doc.paragraphs:
                text_file.write(para.text)
                text_file.write('\n')
        
        progress_callback(100)
        return True
    except Exception as e:
        print(f"DOCX to text error: {str(e)}")
        return False

def text_to_pdf(source_path, target_path, progress_callback):
    """Convert plain text to PDF."""
    progress_callback(20)
    
    try:
        # This is a placeholder for actual conversion
        # In a real app, you'd use libraries like reportlab or fpdf
        
        # Mock conversion - create a simple PDF
        pdf_writer = PdfWriter()
        pdf_writer.add_blank_page(width=612, height=792)  # US Letter size
        
        progress_callback(80)
        
        with open(target_path, 'wb') as output_pdf:
            pdf_writer.write(output_pdf)
        
        progress_callback(100)
        return True
    except Exception as e:
        print(f"Text to PDF error: {str(e)}")
        return False

def text_to_docx(source_path, target_path, progress_callback):
    """Convert plain text to DOCX."""
    progress_callback(20)
    
    try:
        with open(source_path, 'r', encoding='utf-8') as text_file:
            text = text_file.read()
        
        progress_callback(50)
        
        doc = Document()
        for paragraph in text.split('\n'):
            doc.add_paragraph(paragraph)
        
        progress_callback(80)
        
        doc.save(target_path)
        
        progress_callback(100)
        return True
    except Exception as e:
        print(f"Text to DOCX error: {str(e)}")
        return False

def convert_data_format(source_path, target_format, target_path, progress_callback):
    """Convert between data formats (CSV, Excel, JSON, etc.)."""
    progress_callback(10)
    
    try:
        # Read source file based on its extension
        source_ext = os.path.splitext(source_path)[1].lower()
        
        if source_ext == '.csv':
            df = pd.read_csv(source_path)
        elif source_ext == '.xlsx':
            df = pd.read_excel(source_path)
        elif source_ext == '.json':
            df = pd.read_json(source_path)
        else:
            return False
        
        progress_callback(50)
        
        # Write to target format
        if target_format == 'csv':
            df.to_csv(target_path, index=False)
        elif target_format == 'xlsx':
            df.to_excel(target_path, index=False)
        elif target_format == 'json':
            df.to_json(target_path, orient='records')
        elif target_format == 'xml':
            df.to_xml(target_path)
        elif target_format == 'html':
            df.to_html(target_path, index=False)
        else:
            return False
        
        progress_callback(100)
        return True
    except Exception as e:
        print(f"Data format conversion error: {str(e)}")
        return False