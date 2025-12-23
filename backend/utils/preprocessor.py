"""
Enhanced image preprocessing utilities with auto-rotation and multi-format support
"""
import cv2
import numpy as np
from PIL import Image, ImageOps
import io
from typing import Tuple, List

def preprocess_image(image_data: bytes) -> bytes:
    """Enhanced preprocessing for better OCR results"""
    # Convert bytes to PIL Image
    image = Image.open(io.BytesIO(image_data))
    
    # Auto-rotate based on EXIF data
    image = ImageOps.exif_transpose(image)
    
    # Convert to RGB if necessary
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Convert PIL to OpenCV format
    cv_image = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    
    # Apply preprocessing pipeline
    processed = apply_preprocessing_pipeline(cv_image)
    
    # Convert back to bytes
    _, buffer = cv2.imencode('.png', processed)
    return buffer.tobytes()

def apply_preprocessing_pipeline(img: np.ndarray) -> np.ndarray:
    """Apply comprehensive preprocessing pipeline"""
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Auto-rotate if needed (detect and correct skew)
    gray = correct_skew(gray)
    
    # Enhance contrast
    gray = enhance_contrast(gray)
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    
    # Apply adaptive thresholding
    thresh = cv2.adaptiveThreshold(
        denoised, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    
    # Morphological operations to clean up
    kernel = np.ones((1, 1), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
    
    return cleaned

def correct_skew(image: np.ndarray) -> np.ndarray:
    """Detect and correct skew in the image"""
    try:
        # Find edges
        edges = cv2.Canny(image, 50, 150, apertureSize=3)
        
        # Find lines using Hough transform
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=100)
        
        if lines is not None:
            # Calculate angles
            angles = []
            for rho, theta in lines[:10]:  # Use first 10 lines
                angle = theta * 180 / np.pi
                if angle < 45:
                    angles.append(angle)
                elif angle > 135:
                    angles.append(angle - 180)
            
            if angles:
                # Get median angle
                median_angle = np.median(angles)
                
                # Rotate image if skew is significant
                if abs(median_angle) > 0.5:
                    return rotate_image(image, -median_angle)
    
    except Exception:
        pass  # If skew detection fails, return original
    
    return image

def rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
    """Rotate image by given angle"""
    height, width = image.shape[:2]
    center = (width // 2, height // 2)
    
    # Get rotation matrix
    rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    
    # Calculate new dimensions
    cos_angle = abs(rotation_matrix[0, 0])
    sin_angle = abs(rotation_matrix[0, 1])
    new_width = int((height * sin_angle) + (width * cos_angle))
    new_height = int((height * cos_angle) + (width * sin_angle))
    
    # Adjust rotation matrix for new center
    rotation_matrix[0, 2] += (new_width / 2) - center[0]
    rotation_matrix[1, 2] += (new_height / 2) - center[1]
    
    # Rotate image
    rotated = cv2.warpAffine(image, rotation_matrix, (new_width, new_height), 
                           flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    
    return rotated

def enhance_contrast(image: np.ndarray) -> np.ndarray:
    """Enhance image contrast using CLAHE"""
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    return clahe.apply(image)

def detect_orientation(image: np.ndarray) -> int:
    """Detect image orientation (0, 90, 180, 270 degrees)"""
    try:
        # This is a simplified orientation detection
        # In practice, you might want to use more sophisticated methods
        
        # Convert to PIL for easier handling
        pil_image = Image.fromarray(image)
        
        # Try OCR on different orientations and pick the best one
        orientations = [0, 90, 180, 270]
        best_orientation = 0
        best_confidence = 0
        
        import pytesseract
        
        for angle in orientations:
            rotated = pil_image.rotate(angle, expand=True)
            
            # Get OCR confidence
            try:
                data = pytesseract.image_to_data(rotated, output_type=pytesseract.Output.DICT)
                confidences = [int(conf) for conf in data['conf'] if int(conf) > 0]
                avg_confidence = sum(confidences) / len(confidences) if confidences else 0
                
                if avg_confidence > best_confidence:
                    best_confidence = avg_confidence
                    best_orientation = angle
            except:
                continue
        
        return best_orientation
    
    except Exception:
        return 0  # Default to no rotation

def preprocess_for_table_detection(image: np.ndarray) -> np.ndarray:
    """Specialized preprocessing for table/line item detection"""
    # Convert to grayscale if needed
    if len(image.shape) == 3:
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        gray = image.copy()
    
    # Enhance horizontal and vertical lines
    horizontal_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (25, 1))
    vertical_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 25))
    
    # Detect horizontal lines
    horizontal_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, horizontal_kernel)
    
    # Detect vertical lines  
    vertical_lines = cv2.morphologyEx(gray, cv2.MORPH_OPEN, vertical_kernel)
    
    # Combine lines
    table_structure = cv2.addWeighted(horizontal_lines, 0.5, vertical_lines, 0.5, 0.0)
    
    return table_structure
