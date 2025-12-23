# Invoice AI Extractor

> Extract data from invoices automatically using AI. Built by [Omega Matrix](https://omegamatrix.in).

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![React 18](https://img.shields.io/badge/react-18-blue.svg)](https://reactjs.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104-green.svg)](https://fastapi.tiangolo.com/)

## 🚀 Live Demo

Try it now: **[https://omegamatrix.in/demo/invoice](https://omegamatrix.in/demo/invoice)**

No signup. No credit card. Just upload and see results.

## ✨ Features

- ✅ Extracts vendor name, address, tax details
- ✅ Invoice number, dates, payment terms
- ✅ Line items with quantities and prices
- ✅ Calculates totals and validates math
- ✅ Exports to JSON, CSV, Excel
- ✅ Confidence scoring per field
- ✅ Handles PDF and image formats

## 🎯 Use Cases

- Accounts payable automation
- Expense management systems
- Invoice approval workflows
- Financial data extraction
- Vendor management

## 🏃 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 16+
- Tesseract OCR
- Poppler (for PDF processing)

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run server
python main.py
# Server runs on http://localhost:8000
```

### Frontend Setup

```bash
cd frontend
npm install
npm start
# Frontend runs on http://localhost:3000
```

### Install System Dependencies

**macOS:**
```bash
brew install tesseract poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr poppler-utils
```

**Windows:**
- Download Tesseract from [GitHub releases](https://github.com/UB-Mannheim/tesseract/wiki)
- Download Poppler from [releases](https://github.com/oschwartz10612/poppler-windows/releases/)

## 📊 Accuracy

- **Structured invoices:** 90-95%
- **Complex layouts:** 85-90%
- **Handwritten fields:** 75-85%

## 🛠️ Tech Stack

- **Backend:** FastAPI, Python 3.8+
- **OCR:** Tesseract with OpenCV preprocessing
- **AI:** Advanced regex patterns + ML validation
- **Frontend:** React 18, Axios, Lucide Icons
- **Export:** pandas, openpyxl
- **PDF Processing:** PyPDF2, pdf2image

## 📖 How It Works

1. **Upload:** User uploads PDF/image invoice (up to 10MB)
2. **Preprocessing:** Auto-rotation, skew correction, noise reduction
3. **OCR:** Tesseract extracts text with multiple fallback methods
4. **AI Extraction:** 30+ field patterns identify invoice data
5. **Validation:** Mathematical validation, confidence scoring
6. **Export:** Structured JSON/CSV/Excel output

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for details.

## 🔧 Customization

This is a generic demo. For production use:

- **Train on your formats:** 95%+ accuracy for your invoices
- **Add business rules:** Your validation logic
- **Integration:** Connect to your ERP/accounting system
- **Scale:** Batch processing, API rate limits
- **Security:** Authentication, data encryption

**Want this customized?** Contact: info@omegamatrix.in

## 📝 API Documentation

### Extract Invoice

```bash
curl -X POST "http://localhost:8000/api/extract" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@invoice.pdf"
```

Response:
```json
{
  "success": true,
  "processing_time": 2.34,
  "extracted_data": {
    "vendor_name": "Acme Corp",
    "vendor_address": "123 Business St",
    "invoice_number": "INV-2024-001",
    "total": 1242.50
  },
  "field_confidence": {
    "vendor_name": 0.95,
    "total": 0.90
  },
  "overall_confidence": 0.87
}
```

### Export Data

```bash
# Export as JSON
curl -X POST "http://localhost:8000/api/export/json" \
  -F "file=@invoice.pdf" -o data.json

# Export as CSV
curl -X POST "http://localhost:8000/api/export/csv" \
  -F "file=@invoice.pdf" -o data.csv

# Export as Excel
curl -X POST "http://localhost:8000/api/export/excel" \
  -F "file=@invoice.pdf" -o data.xlsx
```

See [API.md](docs/API.md) for complete reference.

## 🚀 Deployment

### Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or build individually
docker build -t invoice-ai-backend ./backend
docker build -t invoice-ai-frontend ./frontend
```

### Cloud Deployment

- **Heroku:** Ready for deployment
- **AWS:** ECS/Fargate compatible
- **Google Cloud:** Cloud Run ready
- **Vercel/Netlify:** Frontend deployment

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed instructions.

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

MIT License - see [LICENSE](LICENSE)

## 🌟 About Omega Matrix

We build custom AI document processing solutions and provide fractional CTO services for startups.

- 🌐 Website: [omegamatrix.in](https://omegamatrix.in)
- 💼 LinkedIn: [linkedin.com/company/omegamatrix](https://linkedin.com/company/omegamatrix)
- 📧 Email: info@omegamatrix.in
- 📍 Based in Karur, Tamil Nadu, India

**Other Open Source Projects:**
- [Contract Analyzer](https://github.com/omegamatrix/contract-analyzer) *(coming soon)*
- [Receipt Scanner](https://github.com/omegamatrix/receipt-scanner) *(coming soon)*

---

⭐ **Star this repo if you find it useful!**

Built with ❤️ in India by [Omega Matrix](https://omegamatrix.in)