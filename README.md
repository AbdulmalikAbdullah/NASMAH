#  NASMAH - AI-Powered Web Platform for Lung Cancer Severity Classification

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![Node.js 18+](https://img.shields.io/badge/node.js-18+-brightgreen.svg)](https://nodejs.org/)
[![Flask](https://img.shields.io/badge/flask-3.0-darkgreen.svg)](https://flask.palletsprojects.com/)
[![React](https://img.shields.io/badge/react-latest-61dafb.svg)](https://react.dev/)

An advanced AI-powered medical imaging platform for early detection and segmentation of lung tumors using deep learning. Built with Flask backend, Vue.js frontend, and PyTorch-based neural networks for precise DICOM image analysis.

## ✨ Features

- 🤖 **Advanced AI Models**: UNet and ResNet34 for accurate lung segmentation
- 🏥 **DICOM Support**: Native support for medical imaging standards
- 🔐 **Secure Authentication**: JWT-based authentication with role-based access control
- 📊 **Real-time Predictions**: Fast inference on GPU-enabled systems
- 🖼️ **Interactive Visualization**: Real-time image viewing and annotation
- 📈 **Prediction History**: Track and review historical predictions
- 👥 **Multi-User Support**: Patient and admin roles with separate dashboards
- ☁️ **Cloud Storage**: AWS S3 integration for scalable storage
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile devices
- 📋 **Comprehensive Logging**: Detailed system and audit logs
- 🧪 **API Testing**: Built-in Postman collection for testing

## 🏗️ Architecture

```
Breath/
├── backend/                 # Flask REST API
│   ├── app/
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # Business logic
│   │   ├── ai/             # ML model loading
│   │   └── utils/          # Utilities & helpers
│   ├── models/             # Pre-trained models (UNet, ResNet34)
│   ├── uploads/            # DICOM image storage
│   └── requirements.txt    # Python dependencies
│
└── frontend/                # Vue.js + React Web App
    ├── src/
    │   ├── components/     # Reusable UI components
    │   ├── pages/          # Page components
    │   ├── api/            # API client
    │   └── context/        # State management
    ├── public/             # Static assets
    └── package.json        # Node dependencies
```

## 🛠️ Tech Stack

### Backend
- **Framework**: Flask 3.0
- **Database**: SQLAlchemy + SQLite
- **AI/ML**: PyTorch, TorchVision, Segmentation Models
- **Image Processing**: OpenCV, Pillow, pydicom
- **Authentication**: JWT (PyJWT), bcrypt
- **Cloud**: AWS S3 (boto3)
- **API**: RESTful with Flask-CORS

### Frontend
- **Framework**: Vue.js / React
- **Build Tool**: Vite
- **Styling**: Tailwind CSS
- **HTTP Client**: Axios
- **Linting**: ESLint

### Deployment
- **Backend**: Python 3.9+
- **Database**: SQLite (Development), PostgreSQL (Production)
- **Cloud Storage**: AWS S3

## 📋 Prerequisites

- **Python** 3.9 or higher
- **Node.js** 18 or higher
- **npm** or **yarn**
- **Git**
- AWS S3 bucket (optional, for cloud storage)
- CUDA 11.8+ (recommended for GPU acceleration)

## 🚀 Quick Start

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
.\venv\Scripts\activate
# On Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your configuration

# Initialize database
python verify_db.py

# Run the Flask server
python run.py
```

The backend will be available at `http://localhost:5000`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build
```

The frontend will be available at `http://localhost:5173`

## 🔌 API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout
- `POST /api/auth/refresh` - Refresh JWT token

### Images
- `GET /api/images` - Get user's images
- `POST /api/images/upload` - Upload DICOM image
- `GET /api/images/<id>` - Get image details
- `DELETE /api/images/<id>` - Delete image

### Predictions
- `POST /api/predictions` - Generate prediction
- `GET /api/predictions/<id>` - Get prediction details
- `GET /api/predictions/history` - Get prediction history

### Admin
- `GET /api/admin/users` - List all users
- `GET /api/admin/logs` - System logs
- `DELETE /api/admin/users/<id>` - Delete user


## 🔒 Security Features

- ✅ JWT-based authentication
- ✅ Password hashing with bcrypt
- ✅ CORS protection
- ✅ SQL injection prevention via ORM
- ✅ Input validation and sanitization
- ✅ Rate limiting (implementable)
- ✅ HTTPS support
- ✅ Secure session management

## 📈 Performance

- **Model Inference**: ~2-5 seconds per DICOM image
- **API Response Time**: < 500ms (excluding inference)
- **Database Queries**: Optimized with indexing
- **Frontend Bundle Size**: ~150KB gzipped


## 📝 Environment Variables

Create a `.env` file in the backend directory:

```env
# Flask Configuration
FLASK_ENV=development
FLASK_APP=run.py
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///instance/lung_ai.db

# JWT
JWT_SECRET_KEY=your-jwt-secret-key

# AWS S3 (Optional)
AWS_ACCESS_KEY_ID=your-access-key
AWS_SECRET_ACCESS_KEY=your-secret-key
AWS_STORAGE_BUCKET_NAME=your-bucket-name

# Email (Optional)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-password
```

## 👥 Team

**Developed by**: GP2 Team - NASMAH

- Abdulmalik Abdulwahab  
- Osama Almalki  
- Omar Mansor  
- Omer Elfaki  

---
