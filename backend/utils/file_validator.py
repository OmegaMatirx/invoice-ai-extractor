"""
File validation utilities
"""
from typing import Tuple, Optional

# File size limit: 10MB
MAX_FILE_SIZE = 10 * 1024 * 1024

ALLOWED_MIME_TYPES = {
    'application/pdf',
    'image/jpeg',
    'image/jpg', 
    'image/png',
    'image/tiff',
    'image/tif'
}

ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.tiff', '.tif'}

def validate_file(file_bytes: bytes, filename: str) -> Tuple[bool, Optional[str]]:
    """
    Validate uploaded file
    Returns: (is_valid, error_message)
    """
    # Check file size
    if len(file_bytes) > MAX_FILE_SIZE:
        return False, f"File size ({len(file_bytes)} bytes) exceeds 10MB limit"
    
    if len(file_bytes) == 0:
        return False, "File is empty"
    
    # Check file extension
    file_ext = get_file_extension(filename).lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        return False, f"File type {file_ext} not supported. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
    
    return True, None

def get_file_extension(filename: str) -> str:
    """Get file extension from filename"""
    return '.' + filename.split('.')[-1] if '.' in filename else ''

def get_file_type(file_bytes: bytes) -> str:
    """Determine file type from bytes"""
    if file_bytes[:4] == b'%PDF':
        return 'pdf'
    elif file_bytes[:2] == b'\xff\xd8':
        return 'jpeg'
    elif file_bytes[:8] == b'\x89PNG\r\n\x1a\n':
        return 'png'
    elif file_bytes[:2] in [b'II', b'MM']:
        return 'tiff'
    else:
        return 'unknown'