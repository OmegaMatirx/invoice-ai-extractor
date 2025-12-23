# Architecture Overview

## System Architecture

The Invoice AI Extractor follows a modern microservices architecture with clear separation of concerns:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │    Backend      │    │   ML Models     │
│   (React)       │◄──►│   (FastAPI)     │◄──►│   (OCR/NLP)     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

## Components

### Frontend (React)
- **Purpose**: User interface for invoice upload and data visualization
- **Technology**: React 18, Axios for API calls
- **Features**:
  - Drag-and-drop file upload
  - Real-time extraction results
  - Responsive design

### Backend (FastAPI)
- **Purpose**: API server handling file processing and ML orchestration
- **Technology**: FastAPI, Python 3.8+
- **Features**:
  - RESTful API endpoints
  - File upload handling
  - Image preprocessing
  - ML model integration

### ML Pipeline
- **OCR Engine**: Tesseract for text extraction
- **Image Processing**: OpenCV for preprocessing
- **Data Extraction**: Custom regex-based field extraction
- **Validation**: Rule-based data validation

## Data Flow

1. **Upload**: User uploads invoice file through frontend
2. **Preprocessing**: Backend preprocesses image for optimal OCR
3. **OCR**: Extract raw text from processed image
4. **Extraction**: Apply ML models to extract structured data
5. **Validation**: Validate and clean extracted data
6. **Response**: Return structured data to frontend

## Security Considerations

- File type validation
- Size limits on uploads
- Input sanitization
- CORS configuration
- Error handling without data leakage

## Scalability

- Stateless API design
- Containerized deployment
- Horizontal scaling capability
- Async processing support