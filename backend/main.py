from fastapi import FastAPI, File, UploadFile, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, StreamingResponse
import uvicorn
import io
from utils.extractor import extract_invoice_data
from utils.export_utils import export_to_json, export_to_csv, export_to_excel
from utils.rate_limiter import rate_limiter
from utils.duplicate_detector import duplicate_detector
import time

app = FastAPI(
    title="Invoice AI Extractor API",
    description="Advanced API for extracting data from invoices using AI/ML",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.get("/")
async def root():
    return {
        "message": "Invoice AI Extractor API v2.0",
        "status": "running",
        "features": [
            "Multi-format support (PDF, JPG, PNG, TIFF)",
            "Multi-page PDF processing",
            "Auto-rotation and skew correction",
            "Comprehensive data extraction",
            "Mathematical validation",
            "Export to JSON/CSV/Excel",
            "Rate limiting (10/day per IP)",
            "Duplicate detection"
        ],
        "endpoints": {
            "extract": "/api/extract",
            "export": "/api/export/{format}",
            "health": "/health",
            "stats": "/api/stats"
        }
    }

@app.post("/api/extract")
async def extract_invoice(request: Request, file: UploadFile = File(...)):
    """
    Extract comprehensive data from uploaded invoice
    Supports: PDF, JPG, PNG, TIFF up to 10MB
    """
    client_ip = request.client.host
    
    # Rate limiting
    is_allowed, error_msg = rate_limiter.is_allowed(client_ip)
    if not is_allowed:
        raise HTTPException(status_code=429, detail=error_msg)
    
    try:
        # Read file
        contents = await file.read()
        
        # Extract data
        extracted_data = extract_invoice_data(contents, file.filename, client_ip)
        
        # Check for duplicates
        is_duplicate, previous_data = duplicate_detector.check_duplicate(
            client_ip, contents, extracted_data
        )
        
        if is_duplicate:
            return JSONResponse(content={
                **previous_data['data'],
                "duplicate_detected": True,
                "message": "This invoice has been processed before",
                "previous_processing_time": previous_data.get('timestamp')
            })
        
        # Add rate limit info to response
        remaining = rate_limiter.get_remaining_requests(client_ip)
        extracted_data["rate_limit_info"] = {
            "remaining_requests": remaining,
            "limit": 10,
            "window": "24 hours"
        }
        
        return JSONResponse(content=extracted_data)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export/{format}")
async def export_data(format: str, request: Request, file: UploadFile = File(...)):
    """
    Extract and export data in specified format
    Formats: json, csv, excel
    """
    client_ip = request.client.host
    
    # Rate limiting (same limit as extract)
    is_allowed, error_msg = rate_limiter.is_allowed(client_ip)
    if not is_allowed:
        raise HTTPException(status_code=429, detail=error_msg)
    
    if format.lower() not in ['json', 'csv', 'excel']:
        raise HTTPException(status_code=400, detail="Format must be json, csv, or excel")
    
    try:
        contents = await file.read()
        extracted_data = extract_invoice_data(contents, file.filename, client_ip)
        
        if format.lower() == 'json':
            content = export_to_json(extracted_data)
            media_type = "application/json"
            filename = f"invoice_data_{int(time.time())}.json"
        
        elif format.lower() == 'csv':
            content = export_to_csv(extracted_data)
            media_type = "text/csv"
            filename = f"invoice_data_{int(time.time())}.csv"
        
        elif format.lower() == 'excel':
            content = export_to_excel(extracted_data)
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = f"invoice_data_{int(time.time())}.xlsx"
            
            return StreamingResponse(
                io.BytesIO(content),
                media_type=media_type,
                headers={"Content-Disposition": f"attachment; filename={filename}"}
            )
        
        return Response(
            content=content,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/stats")
async def get_stats(request: Request):
    """Get usage statistics for current IP"""
    client_ip = request.client.host
    
    remaining = rate_limiter.get_remaining_requests(client_ip)
    reset_time = rate_limiter.get_reset_time(client_ip)
    
    return {
        "rate_limit": {
            "remaining_requests": remaining,
            "total_limit": 10,
            "window": "24 hours",
            "reset_time": reset_time
        },
        "supported_formats": ["PDF", "JPG", "JPEG", "PNG", "TIFF"],
        "max_file_size": "10MB",
        "features": {
            "multi_page_pdf": True,
            "auto_rotation": True,
            "skew_correction": True,
            "mathematical_validation": True,
            "duplicate_detection": True,
            "line_item_extraction": True,
            "confidence_scoring": True
        }
    }

@app.get("/api/sample")
async def get_sample_data():
    """Get sample invoice data structure"""
    return {
        "sample_response": {
            "success": True,
            "processing_time": 2.34,
            "file_info": {
                "filename": "invoice.pdf",
                "file_type": "pdf",
                "file_size": 245760,
                "pages": 1
            },
            "extracted_data": {
                "vendor_name": "ABC Company Inc.",
                "vendor_address": "123 Business St, City, State 12345",
                "vendor_tax_id": "12-3456789",
                "invoice_number": "INV-2024-001",
                "invoice_date": "12/15/2024",
                "due_date": "01/14/2025",
                "po_number": "PO-2024-456",
                "payment_terms": "Net 30",
                "subtotal": 2635.00,
                "tax_amount": 263.50,
                "tax_rate": 10.0,
                "total": 2898.50,
                "currency": "USD",
                "line_items": [
                    {
                        "description": "Web Development Services",
                        "quantity": 1,
                        "unit_price": 2500.00,
                        "line_total": 2500.00
                    },
                    {
                        "description": "Domain Registration",
                        "quantity": 1,
                        "unit_price": 15.00,
                        "line_total": 15.00
                    }
                ]
            },
            "field_confidence": {
                "vendor_name": 0.85,
                "invoice_number": 0.95,
                "total": 0.90
            },
            "overall_confidence": 0.87,
            "math_validation": {
                "subtotal_tax_total_match": True,
                "line_items_sum_match": True,
                "calculations_correct": True
            },
            "missing_required_fields": []
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "version": "2.0.0"
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
