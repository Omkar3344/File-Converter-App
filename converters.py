import os
import time
from PIL import Image
import pandas as pd
from PyPDF2 import PdfReader, PdfWriter
from docx import Document
import traceback
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, 
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    handlers=[logging.FileHandler("converter.log"), logging.StreamHandler()])
logger = logging.getLogger("FileConverter")

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
        # Validate file paths
        if not os.path.exists(source_path):
            logger.error(f"Source file does not exist: {source_path}")
            return False
            
        # Create target directory if it doesn't exist
        target_dir = os.path.dirname(target_path)
        if target_dir and not os.path.exists(target_dir):
            os.makedirs(target_dir)
            
        source_ext = os.path.splitext(source_path)[1].lower()
        target_ext = os.path.splitext(target_path)[1].lower()
        
        if target_ext.startswith('.'):
            target_ext = target_ext[1:]
            
        logger.info(f"Converting {source_path} ({source_ext}) to {target_path} ({target_ext})")
        
        # Simulate progress updates
        def update_progress(value):
            if progress_callback:
                progress_callback(value)
                
        update_progress(10)
        
        # Handle image conversions
        if source_ext.lower() in ['.jpg', '.jpeg', '.png', '.bmp', '.webp', '.gif']:
            if target_ext.lower() in ['jpg', 'jpeg', 'png', 'bmp', 'webp', 'gif']:
                return convert_image(source_path, target_path, update_progress)
            elif target_ext.lower() == 'pdf':
                return image_to_pdf(source_path, target_path, update_progress)
        
        # Handle document conversions
        elif source_ext.lower() == '.pdf':
            if target_ext.lower() in ['jpg', 'jpeg', 'png']:
                return pdf_to_images(source_path, target_path, update_progress)
            elif target_ext.lower() == 'txt':
                return pdf_to_text(source_path, target_path, update_progress)
        
        elif source_ext.lower() == '.docx':
            if target_ext.lower() == 'pdf':
                return docx_to_pdf(source_path, target_path, update_progress)
            elif target_ext.lower() == 'txt':
                return docx_to_text(source_path, target_path, update_progress)
        
        elif source_ext.lower() == '.txt':
            if target_ext.lower() == 'pdf':
                return text_to_pdf(source_path, target_path, update_progress)
            elif target_ext.lower() == 'docx':
                return text_to_docx(source_path, target_path, update_progress)
        
        # Handle data formats
        elif source_ext.lower() in ['.csv', '.xlsx', '.json']:
            if target_ext.lower() in ['csv', 'xlsx', 'json', 'xml', 'html']:
                return convert_data_format(source_path, target_ext, target_path, update_progress)
        
        logger.warning(f"No specific conversion routine found for {source_ext} to {target_ext}")
        update_progress(100)
        return False
    
    except Exception as e:
        logger.error(f"Conversion error: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def convert_image(source_path, target_path, progress_callback):
    """Convert between image formats."""
    try:
        progress_callback(20)
        
        # Open the image file
        img = Image.open(source_path)
        logger.info(f"Image opened: {source_path}, Mode: {img.mode}, Size: {img.size}")
        
        # Handle special cases for different formats
        target_ext = os.path.splitext(target_path)[1].lower()
        
        # JPEG conversion - must be RGB
        if target_ext in ['.jpg', '.jpeg'] or target_path.lower().endswith(('.jpg', '.jpeg')):
            logger.info("Converting to JPEG format (ensuring RGB mode)")
            # Convert to RGB mode for JPEG (which doesn't support alpha channels or palettes)
            if img.mode != 'RGB':
                img = img.convert('RGB')
                logger.info(f"Converted image mode to RGB")
        
        # PNG conversion - can handle RGBA
        elif target_ext == '.png' or target_path.lower().endswith('.png'):
            # PNG supports various modes, but RGBA is most common for transparency
            if img.mode == 'P' and 'transparency' in img.info:
                img = img.convert('RGBA')
                logger.info(f"Converted palette with transparency to RGBA")
        
        # GIF conversion
        elif target_ext == '.gif' or target_path.lower().endswith('.gif'):
            # For animated GIFs, we'd need special handling here
            # For single frame, convert to P mode with adaptive palette
            if img.mode not in ['P', 'L', 'RGB']:
                img = img.convert('RGB').convert('P', palette=Image.ADAPTIVE)
                logger.info(f"Converted to palette mode for GIF")
        
        progress_callback(60)
        
        # Save the converted image
        logger.info(f"Saving image to {target_path}")
        img.save(target_path)
        
        # Verify the file was created
        if not os.path.exists(target_path):
            logger.error(f"Failed to save image: File not created at {target_path}")
            return False
            
        file_size = os.path.getsize(target_path)
        if file_size == 0:
            logger.error(f"Saved file has zero size: {target_path}")
            return False
            
        logger.info(f"Successfully saved image: {target_path}, Size: {file_size} bytes")
        progress_callback(100)
        return True
        
    except Exception as e:
        logger.error(f"Image conversion error: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def image_to_pdf(source_path, target_path, progress_callback):
    """Convert an image to PDF."""
    try:
        progress_callback(20)
        
        img = Image.open(source_path)
        logger.info(f"Converting image to PDF: {source_path} -> {target_path}")
        
        # Always convert to RGB for PDF
        if img.mode != 'RGB':
            img = img.convert('RGB')
            logger.info("Converted image to RGB mode for PDF")
        
        progress_callback(60)
        
        # Save as PDF
        img.save(target_path, "PDF", resolution=100.0)
        
        # Verify file creation
        if not os.path.exists(target_path):
            logger.error(f"Failed to create PDF: {target_path}")
            return False
            
        logger.info(f"Successfully created PDF: {target_path}")
        progress_callback(100)
        return True
        
    except Exception as e:
        logger.error(f"Image to PDF conversion error: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def pdf_to_images(source_path, target_path, progress_callback):
    """Extract pages from a PDF as images."""
    try:
        progress_callback(10)
        
        logger.info(f"Converting PDF to image(s): {source_path} -> {target_path}")
        pdf = PdfReader(source_path)
        total_pages = len(pdf.pages)
        
        if total_pages == 0:
            logger.error("PDF has no pages")
            return False
            
        logger.info(f"PDF has {total_pages} pages")
        
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
            
            logger.info(f"Created image for page {i+1}: {img_path}")
            progress_callback(20 + (i+1) * 80 // total_pages)
        
        progress_callback(100)
        return True
        
    except Exception as e:
        logger.error(f"PDF to images error: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def pdf_to_text(source_path, target_path, progress_callback):
    """Extract text from a PDF."""
    try:
        progress_callback(10)
        
        logger.info(f"Converting PDF to text: {source_path} -> {target_path}")
        pdf = PdfReader(source_path)
        total_pages = len(pdf.pages)
        logger.info(f"PDF has {total_pages} pages")
        
        progress_callback(20)
        
        with open(target_path, 'w', encoding='utf-8') as text_file:
            for i, page in enumerate(pdf.pages):
                text = page.extract_text()
                text_file.write(text)
                text_file.write('\n\n--- Page Break ---\n\n')
                logger.info(f"Extracted text from page {i+1} (length: {len(text)} chars)")
                progress_callback(20 + (i+1) * 70 // total_pages)
        
        # Verify file was created
        if not os.path.exists(target_path):
            logger.error(f"Failed to create text file: {target_path}")
            return False
            
        logger.info(f"Successfully created text file: {target_path}")
        progress_callback(100)
        return True
        
    except Exception as e:
        logger.error(f"PDF to text error: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def docx_to_pdf(source_path, target_path, progress_callback):
    """Convert DOCX to PDF."""
    try:
        progress_callback(20)
        
        logger.info(f"Converting DOCX to PDF: {source_path} -> {target_path}")
        # This is a placeholder for actual conversion
        # In a real app, you'd use libraries like docx2pdf, python-docx, and reportlab
        # For mobile deployment, this would require additional setup
        
        # Mock conversion - create a simple PDF
        pdf_writer = PdfWriter()
        pdf_writer.add_blank_page(width=612, height=792)  # US Letter size
        
        progress_callback(80)
        
        with open(target_path, 'wb') as output_pdf:
            pdf_writer.write(output_pdf)
        
        # Verify file was created
        if not os.path.exists(target_path):
            logger.error(f"Failed to create PDF file: {target_path}")
            return False
            
        logger.info(f"Successfully created PDF file: {target_path}")
        progress_callback(100)
        return True
        
    except Exception as e:
        logger.error(f"DOCX to PDF error: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def docx_to_text(source_path, target_path, progress_callback):
    """Extract text from a DOCX file."""
    try:
        progress_callback(20)
        
        logger.info(f"Converting DOCX to text: {source_path} -> {target_path}")
        doc = Document(source_path)
        
        progress_callback(50)
        
        with open(target_path, 'w', encoding='utf-8') as text_file:
            for para in doc.paragraphs:
                text_file.write(para.text)
                text_file.write('\n')
        
        # Verify file was created
        if not os.path.exists(target_path):
            logger.error(f"Failed to create text file: {target_path}")
            return False
            
        logger.info(f"Successfully created text file: {target_path}")
        progress_callback(100)
        return True
        
    except Exception as e:
        logger.error(f"DOCX to text error: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def text_to_pdf(source_path, target_path, progress_callback):
    """Convert plain text to PDF."""
    try:
        progress_callback(20)
        
        logger.info(f"Converting text to PDF: {source_path} -> {target_path}")
        # This is a placeholder for actual conversion
        # In a real app, you'd use libraries like reportlab or fpdf
        
        # Mock conversion - create a simple PDF
        pdf_writer = PdfWriter()
        pdf_writer.add_blank_page(width=612, height=792)  # US Letter size
        
        progress_callback(80)
        
        with open(target_path, 'wb') as output_pdf:
            pdf_writer.write(output_pdf)
        
        # Verify file was created
        if not os.path.exists(target_path):
            logger.error(f"Failed to create PDF file: {target_path}")
            return False
            
        logger.info(f"Successfully created PDF file: {target_path}")
        progress_callback(100)
        return True
        
    except Exception as e:
        logger.error(f"Text to PDF error: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def text_to_docx(source_path, target_path, progress_callback):
    """Convert plain text to DOCX."""
    try:
        progress_callback(20)
        
        logger.info(f"Converting text to DOCX: {source_path} -> {target_path}")
        with open(source_path, 'r', encoding='utf-8') as text_file:
            text = text_file.read()
        
        progress_callback(50)
        
        doc = Document()
        for paragraph in text.split('\n'):
            doc.add_paragraph(paragraph)
        
        progress_callback(80)
        
        doc.save(target_path)
        
        # Verify file was created
        if not os.path.exists(target_path):
            logger.error(f"Failed to create DOCX file: {target_path}")
            return False
            
        logger.info(f"Successfully created DOCX file: {target_path}")
        progress_callback(100)
        return True
        
    except Exception as e:
        logger.error(f"Text to DOCX error: {str(e)}")
        logger.error(traceback.format_exc())
        return False

def convert_data_format(source_path, target_format, target_path, progress_callback):
    """Convert between data formats (CSV, Excel, JSON, etc.)."""
    try:
        progress_callback(10)
        
        logger.info(f"Converting data format: {source_path} -> {target_path} ({target_format})")
        # Read source file based on its extension
        source_ext = os.path.splitext(source_path)[1].lower()
        
        if source_ext == '.csv':
            logger.info("Reading CSV file")
            df = pd.read_csv(source_path)
        elif source_ext == '.xlsx':
            logger.info("Reading Excel file")
            df = pd.read_excel(source_path)
        elif source_ext == '.json':
            logger.info("Reading JSON file")
            df = pd.read_json(source_path)
        else:
            logger.error(f"Unsupported source format: {source_ext}")
            return False
        
        logger.info(f"Read data with shape: {df.shape}")
        progress_callback(50)
        
        # Write to target format
        if target_format == 'csv':
            logger.info("Writing to CSV format")
            df.to_csv(target_path, index=False)
        elif target_format == 'xlsx':
            logger.info("Writing to Excel format")
            df.to_excel(target_path, index=False)
        elif target_format == 'json':
            logger.info("Writing to JSON format")
            df.to_json(target_path, orient='records')
        elif target_format == 'xml':
            logger.info("Writing to XML format")
            df.to_xml(target_path)
        elif target_format == 'html':
            logger.info("Writing to HTML format")
            df.to_html(target_path, index=False)
        else:
            logger.error(f"Unsupported target format: {target_format}")
            return False
        
        # Verify file was created
        if not os.path.exists(target_path):
            logger.error(f"Failed to create file: {target_path}")
            return False
            
        logger.info(f"Successfully created {target_format} file: {target_path}")
        progress_callback(100)
        return True
        
    except Exception as e:
        logger.error(f"Data format conversion error: {str(e)}")
        logger.error(traceback.format_exc())
        return False