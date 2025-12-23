# Deployment Guide

## Local Development

### Prerequisites
- Python 3.8+
- Node.js 16+
- Tesseract OCR

### Setup Steps

1. **Clone the repository:**
```bash
git clone https://github.com/yourusername/invoice-ai-extractor.git
cd invoice-ai-extractor
```

2. **Backend setup:**
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

3. **Frontend setup:**
```bash
cd frontend
npm install
npm start
```

## Docker Deployment

### Backend Dockerfile
```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile
```dockerfile
FROM node:16-alpine

WORKDIR /app

COPY package*.json ./
RUN npm install

COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=0 /app/build /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose
```yaml
version: '3.8'

services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app

  frontend:
    build: ./frontend
    ports:
      - "3000:80"
    depends_on:
      - backend
```

## Cloud Deployment

### AWS Deployment
1. **ECS/Fargate**: Use Docker containers with ECS
2. **Lambda**: For serverless processing (with size limits)
3. **S3**: Store uploaded files temporarily
4. **CloudFront**: CDN for frontend assets

### Google Cloud Platform
1. **Cloud Run**: Serverless container deployment
2. **App Engine**: Managed platform deployment
3. **Cloud Storage**: File storage

### Heroku
1. Create Heroku apps for frontend and backend
2. Configure buildpacks for Python and Node.js
3. Set environment variables
4. Deploy using Git

## Environment Variables

### Backend
```bash
# Optional configurations
TESSERACT_CMD=/usr/bin/tesseract
MAX_FILE_SIZE=10485760  # 10MB
ALLOWED_EXTENSIONS=png,jpg,jpeg,pdf
```

### Frontend
```bash
REACT_APP_API_URL=http://localhost:8000
```

## Production Considerations

1. **Security**:
   - Enable HTTPS
   - Configure CORS properly
   - Implement rate limiting
   - Add authentication if needed

2. **Performance**:
   - Use Redis for caching
   - Implement file size limits
   - Add request queuing for heavy processing

3. **Monitoring**:
   - Add logging
   - Health checks
   - Error tracking (Sentry)
   - Performance monitoring

4. **Scaling**:
   - Load balancer configuration
   - Auto-scaling policies
   - Database for storing results