# Lung Cancer AI Detection - Flask Backend

A Flask-based REST API backend for lung cancer stage detection using deep learning on DICOM medical images.

## 🏗️ Project Structure

```
flask_server/
│
├── app/
│   ├── __init__.py          # App factory
│   ├── config.py            # Configuration settings
│   ├── models.py            # SQLAlchemy database models
│   ├── extensions.py        # Flask extensions
│   │
│   ├── routes/              # API endpoints
│   │   ├── auth.py          # Authentication routes
│   │   ├── images.py        # Image upload/management
│   │   ├── predictions.py   # AI predictions
│   │   ├── admin.py         # Admin operations
│   │   └── logs.py          # System logs
│   │
│   ├── services/            # Business logic layer
│   │   ├── auth_service.py
│   │   ├── image_service.py
│   │   ├── prediction_service.py
│   │   └── logging_service.py
│   │
│   ├── utils/               # Utility functions
│   │   ├── validators.py
│   │   ├── preprocessing.py
│   │   ├── decorators.py
│   │   └── security.py
│   │
│   └── ai/                  # AI model components
│       └── model_loader.py
│
├── models/                  # Trained model files
│   └── lung_model.pth
│
├── instance/                # Instance-specific files
│   └── lung_ai.db          # SQLite database
│
├── uploads/                 # Uploaded DICOM images
│
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
└── .env                     # Environment variables
```

## 📋 Database Schema

### Tables
- **users** - User accounts (patients and admins)
- **tumor_images** - Uploaded DICOM images
- **predictions** - AI model predictions
- **system_logs** - System activity logs
- **user_sessions** - JWT session management

## 🚀 Setup Instructions

### 1. Create Virtual Environment

```bash
cd flask_server
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows:**
```bash
.\venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` and update the values:
```env
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key
FLASK_ENV=development
```

### 5. Initialize Database

The database will be created automatically when you run the application for the first time.

### 6. Run the Application

```bash
python run.py
```

The server will start on `http://localhost:5000`

## 📡 API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - Login user
- `POST /api/auth/logout` - Logout user
- `POST /api/auth/refresh` - Refresh JWT token

### Images
- `POST /api/images/upload` - Upload DICOM image
- `GET /api/images/` - Get user's images
- `GET /api/images/<id>` - Get specific image
- `DELETE /api/images/<id>` - Delete image

### Predictions
- `POST /api/predictions/predict` - Make prediction
- `GET /api/predictions/` - Get user's predictions
- `GET /api/predictions/<id>` - Get specific prediction
- `GET /api/predictions/history` - Get prediction history

### Admin
- `GET /api/admin/users` - Get all users
- `GET /api/admin/users/<id>` - Get specific user
- `PUT /api/admin/users/<id>/activate` - Activate/deactivate user
- `GET /api/admin/stats` - Get system statistics

### Logs
- `GET /api/logs/` - Get system logs
- `GET /api/logs/user/<id>` - Get user logs
- `GET /api/logs/actions` - Get log actions

## 🔒 Authentication

This API uses JWT (JSON Web Tokens) for authentication. Include the token in the Authorization header:

```
Authorization: Bearer <your-jwt-token>
```

## 🧪 Testing

Run tests with pytest:

```bash
pytest
```

## 📦 Dependencies

- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **PyJWT** - JWT authentication
- **PyTorch** - Deep learning framework
- **pydicom** - DICOM file handling
- **Pillow** - Image processing
- **Flask-CORS** - CORS support

## 🔧 Configuration

Edit `app/config.py` to modify:
- Database URI
- Upload folder location
- Max file size
- Allowed file extensions
- JWT expiration times
- Model path

## 📝 Next Steps

1. ✅ Database models created
2. ✅ API structure implemented
3. ✅ Authentication service ready
4. ⏳ Implement authentication endpoints
5. ⏳ Implement image upload functionality
6. ⏳ Integrate AI model for predictions
7. ⏳ Add comprehensive error handling
8. ⏳ Add input validation
9. ⏳ Write unit tests
10. ⏳ Deploy to production

## 🤝 Contributing

This is a medical application. Please ensure all changes maintain HIPAA compliance and data security standards.

## 📄 License

[Your License Here]
