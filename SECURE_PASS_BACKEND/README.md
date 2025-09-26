# Secure Pass Backend

FastAPI-based backend for the Secure Pass license plate recognition system.

## Features

- FastAPI web framework with automatic API documentation
- SQLAlchemy ORM with SQLite database
- JWT-based authentication and authorization
- License plate detection using YOLO
- OCR text recognition with PaddleOCR and EasyOCR
- Image processing with OpenCV
- Role-based access control (Admin, Manager, Security)
- RESTful API endpoints
- CORS support for frontend integration

## Installation

1. Create virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment:
   ```bash
   cp .env.example .env
   # Edit .env file with your settings
   ```

4. Initialize database:
   ```bash
   python init_db.py
   ```

## Running

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
app/
├── api/endpoints/      # API route handlers
├── core/              # Core configurations and models
├── scripts/           # Utility scripts
└── utils/             # Helper utilities
data/                  # Data storage directory
yolo_v8_custom_updated/ # ML model files
```

## Environment Variables

See `.env.example` for all available configuration options.