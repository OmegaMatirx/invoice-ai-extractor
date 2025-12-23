# API Documentation

## Base URL
```
http://localhost:8000
```

## Endpoints

### Health Check
```http
GET /health
```

**Response:**
```json
{
  "status": "healthy"
}
```

### Root
```http
GET /
```

**Response:**
```json
{
  "message": "Invoice AI Extractor API",
  "status": "running"
}
```

### Extract Invoice Data
```http
POST /api/extract
```

**Request:**
- Content-Type: `multipart/form-data`
- Body: Form data with `file` field containing the invoice image/PDF

**Response:**
```json
{
  "raw_text": "Extracted text from OCR...",
  "extracted_data": {
    "invoice_number": "INV-2024-001",
    "date": "12/15/2024",
    "total": 2898.0,
    "vendor": "ABC Company Inc."
  },
  "confidence": 0.75
}
```

**Error Response:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

## Request Examples

### cURL
```bash
curl -X POST "http://localhost:8000/api/extract" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@invoice.pdf"
```

### JavaScript (Axios)
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const response = await axios.post('http://localhost:8000/api/extract', formData, {
  headers: {
    'Content-Type': 'multipart/form-data'
  }
});
```

### Python (Requests)
```python
import requests

with open('invoice.pdf', 'rb') as f:
    files = {'file': f}
    response = requests.post('http://localhost:8000/api/extract', files=files)
    data = response.json()
```

## Status Codes

- `200` - Success
- `400` - Bad Request (invalid file format, etc.)
- `422` - Validation Error
- `500` - Internal Server Error

## Supported File Formats

- Images: PNG, JPG, JPEG
- Documents: PDF (converted to images internally)

## Rate Limits

Currently no rate limits are implemented. Consider implementing rate limiting for production use.