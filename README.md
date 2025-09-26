# Secure Pass - License Plate Recognition System

A modern, full-stack application for automated license plate recognition and access control management.

## 🚀 Features

- **Real-time License Plate Recognition**: Advanced OCR and ML-based plate detection
- **Role-based Access Control**: Admin, Manager, and Security user roles
- **Responsive Web Interface**: Modern, mobile-friendly design
- **Real-time Monitoring**: Live dashboard for security personnel
- **Vehicle Management**: Add, remove, and manage authorized vehicles
- **Access Logging**: Comprehensive logging of all access attempts
- **Photo Capture**: Automatic photo capture of detected vehicles

## 🏗️ Architecture

### Backend (FastAPI)
- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM
- **OpenCV**: Computer vision library for image processing
- **PaddleOCR/EasyOCR**: OCR engines for text recognition
- **YOLO**: Object detection for license plate detection
- **JWT Authentication**: Secure token-based authentication

### Frontend (React + Vite)
- **React 19**: Modern React with latest features
- **Vite**: Fast build tool and development server
- **Tailwind CSS**: Utility-first CSS framework
- **React Router**: Client-side routing
- **Axios**: HTTP client for API communication
- **React Icons**: Beautiful icon library

## 📁 Project Structure

```
secure-pass/
├── SECURE_PASS_BACKEND/
│   ├── app/
│   │   ├── api/endpoints/          # API route handlers
│   │   ├── core/                   # Core configurations
│   │   ├── scripts/                # Utility scripts
│   │   └── utils/                  # Helper utilities
│   ├── data/                       # Data storage
│   ├── debug/                      # Debug files
│   ├── scripts/                    # Database scripts
│   └── yolo_v8_custom_updated/     # ML model files
└── SECURE_PASS_FRONTEND/
    ├── public/                     # Static assets
    └── src/
        ├── assets/                 # Images and static files
        ├── components/             # React components
        ├── pages/                  # Page components
        └── styles/                 # Global styles
```

## 🛠️ Installation & Setup

### Prerequisites
- Python 3.8+
- Node.js 16+
- npm or yarn

### Backend Setup

1. **Navigate to backend directory**:
   ```bash
   cd SECURE_PASS_BACKEND
   ```

2. **Create virtual environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize database**:
   ```bash
   python init_db.py
   ```

6. **Run the server**:
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### Frontend Setup

1. **Navigate to frontend directory**:
   ```bash
   cd SECURE_PASS_FRONTEND
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Set up environment variables**:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

4. **Run the development server**:
   ```bash
   npm run dev
   ```

### Quick Start (Both Services)

Use the provided startup script:
```bash
# Windows
start_secure_pass.bat

# Or manually start both services in separate terminals
```

## 🔐 Default Users

The system comes with pre-configured users for testing:

| Username | Password | Role |
|----------|----------|------|
| admin | admin123 | Admin |
| manager | manager123 | Manager |
| security | security123 | Security |

## 🌐 API Endpoints

### Authentication
- `POST /token` - Login and get access token

### Users (Admin only)
- `GET /users/` - List all users
- `POST /users/` - Create new user
- `DELETE /users/{user_id}` - Delete user

### Vehicles
- `GET /vehicles` - List authorized vehicles
- `POST /vehicles` - Add new vehicle
- `DELETE /vehicles/{plate_number}` - Remove vehicle

### Access Logs
- `GET /logs/` - Get access logs
- `POST /logs/` - Create log entry

### Photos
- `GET /photos/` - Get captured photos
- `POST /photos/` - Upload photo

## 🎨 UI/UX Features

- **Responsive Design**: Works on desktop, tablet, and mobile
- **Dark Theme**: Modern dark interface with glass morphism
- **Real-time Updates**: Live data updates every 5 seconds
- **Animated Components**: Smooth transitions and hover effects
- **Accessibility**: WCAG compliant with proper ARIA labels
- **Mobile Navigation**: Collapsible sidebar for mobile devices

## 🔧 Configuration

### Backend Environment Variables
```env
DATABASE_URL=sqlite:///./secure_pass.db
HOST=0.0.0.0
PORT=8000
SECRET_KEY=your-secret-key
DEBUG=True
```

### Frontend Environment Variables
```env
REACT_APP_API_URL=http://localhost:8000
REACT_APP_APP_NAME=Secure Pass
```

## 🚀 Deployment

### Docker Deployment (Recommended)
```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Manual Deployment
- Configure environment variables for production
- Use a process manager like PM2 for Node.js
- Use Gunicorn or similar for Python
- Set up reverse proxy with Nginx

## 🧪 Testing

### Backend Tests
```bash
cd SECURE_PASS_BACKEND
pytest
```

### Frontend Tests
```bash
cd SECURE_PASS_FRONTEND
npm test
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- OpenCV community for computer vision tools
- PaddlePaddle team for OCR capabilities
- Ultralytics for YOLO implementation
- React and FastAPI communities

## 📞 Support

For support, email support@securepass.com or create an issue on GitHub.

---

**Built with ❤️ using modern technologies**