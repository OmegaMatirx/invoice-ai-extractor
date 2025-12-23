"""
Enhanced invoice data extraction utilities with multi-format support
"""
import pytesseract
from PIL import Image
import io
from typing import Dict, Any, List, Tuple
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from models.invoice_model import InvoiceModel
from utils.pdf_processor import is_pdf, process_pdf
from utils.file_validator import validate_file, get_file_type
from utils.preprocessor import preprocess_image
import time

def extract_text_from_image(image_data: bytes) -> str:
    """Extract text from image using OCR with enhanced configuration"""
    try:
        image = Image.open(io.BytesIO(image_data))
        
        # Use enhanced OCR configuration
        custom_config = r'--oem 3 --psm 6 -c tessedit_char_whitelist=0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,/$%-#:() '
        text = pytesseract.image_to_string(image, config=custom_config)
        return text
    except Exception as e:
        raise Exception(f"OCR extraction failed: {str(e)}")

def extract_invoice_data(file_data: bytes, filename: str = "", client_ip: str = "") -> Dict[str, Any]:
    """
    Enhanced extraction supporting multiple formats and comprehensive data extraction
    """
    start_time = time.time()
    
    # Validate file
    is_valid, error_msg = validate_file(file_data, filename)
    if not is_valid:
        raise Exception(error_msg)
    
    # Determine file type and process accordingly
    file_type = get_file_type(file_data)
    
    if file_type == 'pdf' or is_pdf(file_data):
        raw_text, images = process_pdf(file_data)
        processed_images = []
        
        # Preprocess images for better OCR if needed
        if not raw_text.strip():  # If no text from native PDF
            for img in images:
                img_bytes = io.BytesIO()
                img.save(img_bytes, format='PNG')
                img_bytes.seek(0)
                processed_img = preprocess_image(img_bytes.getvalue())
                processed_images.append(processed_img)
    else:
        # Handle image files
        processed_image = preprocess_image(file_data)
        raw_text = extract_text_from_image(processed_image)
        processed_images = [processed_image]
    
    # Initialize enhanced model
    model = InvoiceModel()
    
    # Extract fields using enhanced patterns
    extracted_fields = model.extract_fields(raw_text)
    
    # Validate and clean data with confidence scoring
    validation_result = model.validate_extraction(extracted_fields)
    
    processing_time = time.time() - start_time
    
    # Build comprehensive response
    result = {
        "success": True,
        "processing_time": round(processing_time, 2),
        "file_info": {
            "filename": filename,
            "file_type": file_type,
            "file_size": len(file_data),
            "pages": len(processed_images) if file_type == 'pdf' else 1
        },
        "raw_text": raw_text,
        "extracted_data": validation_result['extracted_data'],
        "field_confidence": validation_result['field_confidence'],
        "overall_confidence": validation_result['overall_confidence'],
        "math_validation": validation_result['math_validation'],
        "missing_required_fields": validation_result['missing_required_fields'],
        "data_quality": {
            "has_line_items": bool(validation_result['extracted_data'].get('line_items')),
            "has_vendor_info": bool(validation_result['extracted_data'].get('vendor_name')),
            "has_financial_summary": bool(validation_result['extracted_data'].get('total')),
            "calculations_valid": validation_result['math_validation'].get('calculations_correct', False)
        }
    }
    
    return result

def calculate_confidence(data: Dict[str, Any]) -> float:
    """Enhanced confidence calculation"""
    if not data:
        return 0.0
    
    # Weight different field types
    field_weights = {
        'invoice_number': 0.2,
        'invoice_date': 0.15,
        'total': 0.2,
        'vendor_name': 0.15,
        'subtotal': 0.1,
        'tax_amount': 0.1,
        'line_items': 0.1
    }
    
    weighted_score = 0.0
    total_weight = 0.0
    
    for field, weight in field_weights.items():
        if field in data and data[field]:
            weighted_score += weight
        total_weight += weight
    
    return weighted_score / total_weight if total_weight > 0 else 0.0

def extract_with_fallback_methods(image_data: bytes) -> str:
    """Try multiple OCR methods for better text extraction"""
    methods = [
        {'config': r'--oem 3 --psm 6'},  # Default
        {'config': r'--oem 3 --psm 4'},  # Single column
        {'config': r'--oem 3 --psm 3'},  # Fully automatic
        {'config': r'--oem 1 --psm 6'},  # Legacy engine
    ]
    
    best_text = ""
    best_confidence = 0
    
    image = Image.open(io.BytesIO(image_data))
    
    for method in methods:
        try:
            # Get text and confidence data
            data = pytesseract.image_to_data(image, config=method['config'], 
                                           output_type=pytesseract.Output.DICT)
            
            # Calculate average confidence
            confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0
            
            if avg_confidence > best_confidence:
                best_confidence = avg_confidence
                best_text = pytesseract.image_to_string(image, config=method['config'])
        
        except Exception:
            continue
    
    return best_text if best_text else pytesseract.image_to_string(image)

def detect_invoice_regions(image_data: bytes) -> Dict[str, Any]:
    """Detect different regions of the invoice (header, line items, totals)"""
    # This is a placeholder for more advanced region detection
    # In a production system, you might use ML models for layout analysis
    
    return {
        "header_region": {"x": 0, "y": 0, "width": 100, "height": 30},
        "line_items_region": {"x": 0, "y": 30, "width": 100, "height": 50},
        "totals_region": {"x": 0, "y": 80, "width": 100, "height": 20}
    }