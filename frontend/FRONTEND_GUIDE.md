# Lung AI Frontend

A modern React-based frontend for the Lung AI medical imaging system. Built with Vite, React Router, and Tailwind CSS.

## 🏗️ Architecture

```
frontend/
├── src/
│   ├── api/
│   │   └── axiosConfig.js           # Centralized Axios with JWT Interceptors
│   ├── components/
│   │   ├── common/                  # Reusable UI components
│   │   │   ├── Button.jsx
│   │   │   ├── Input.jsx
│   │   │   ├── Navbar.jsx
│   │   │   └── LoadingSpinner.jsx
│   │   ├── auth/                    # Authentication components
│   │   │   └── ProtectedRoute.jsx
│   │   └── dashboard/               # Dashboard-specific components
│   │       ├── FileUpload.jsx
│   │       └── PredictionResult.jsx
│   ├── context/
│   │   └── AuthContext.jsx          # Global Auth State (JWT & User data)
│   ├── pages/
│   │   ├── Login.jsx
│   │   ├── Register.jsx
│   │   └── Dashboard.jsx
│   ├── hooks/
│   │   └── useApi.js                # Custom hook for loading/error states
│   ├── App.jsx                      # Main app with routing
│   ├── main.jsx                     # Entry point
│   └── index.css                    # Global styles with Tailwind
├── .env                             # Environment variables
├── tailwind.config.js               # Tailwind CSS configuration
├── postcss.config.js                # PostCSS configuration
└── package.json                     # Dependencies
```

## 🚀 Quick Start

### Prerequisites
- Node.js 16+ and npm
- Backend API running on `http://localhost:5000`

### Installation

1. **Install dependencies:**
   ```bash
   npm install
   ```

2. **Configure environment:**
   The `.env` file is already configured:
   ```
   VITE_API_URL=http://localhost:5000
   ```

3. **Start development server:**
   ```bash
   npm run dev
   ```
   The app will be available at `http://localhost:5173`

4. **Build for production:**
   ```bash
   npm run build
   ```
   Production files will be in the `dist/` folder, which Flask can serve.

## 🔑 Features

### Authentication
- **JWT-based authentication** with automatic token refresh
- **Protected routes** that redirect unauthenticated users to login
- **Role-based access control** (ready for admin features)
- Secure token storage in localStorage

### Dashboard
- **DICOM file upload** with drag-and-drop support
- **Real-time AI predictions** with confidence scores
- **Recent predictions history** in the session
- **Visual indicators** for cancer stages and confidence levels
- **Medical disclaimer** for compliance

### UI/UX
- **Tailwind CSS** for modern, responsive design
- **Loading states** during API calls and predictions
- **Error handling** with user-friendly messages
- **Form validation** with inline error display

## 📡 API Integration

### Authentication Endpoints
```javascript
POST /api/auth/login      - User login
POST /api/auth/register   - User registration
POST /api/auth/logout     - User logout
POST /api/auth/refresh    - Refresh access token
```

### Image & Prediction Workflow
```javascript
// 1. Upload DICOM image
POST /api/images/upload
   Body: FormData with 'file'
   Response: { image_id }

// 2. Request prediction
POST /api/predictions/predict
   Body: { image_id }
   Response: { predicted_stage, confidence }
```

### Admin Endpoints (Ready for Implementation)
```javascript
GET  /api/admin/users             - Get all users
GET  /api/admin/users/:id         - Get specific user
PUT  /api/admin/users/:id/activate - Activate/deactivate user
GET  /api/admin/statistics        - System statistics
GET  /api/logs                    - System logs
```

## 🧩 Key Components

### AuthContext
Manages global authentication state:
- `login(email, password)` - Authenticate user
- `register(username, email, password)` - Create account
- `logout()` - Clear session
- `isAuthenticated()` - Check auth status
- `isAdmin()` - Check admin role

### useApi Hook
Simplifies API calls with automatic state management:
```javascript
const { loading, error, data, execute } = useApi();

await execute(async () => {
  return await axiosInstance.get('/api/endpoint');
});
```

### ProtectedRoute
Wraps components that require authentication:
```javascript
<ProtectedRoute>
  <Dashboard />
</ProtectedRoute>

// Admin-only route
<ProtectedRoute adminOnly>
  <AdminPanel />
</ProtectedRoute>
```

## 🔧 Customization

### Adding Admin Panel
Uncomment the admin routes in `App.jsx`:
```javascript
<Route
  path="/admin"
  element={
    <ProtectedRoute adminOnly>
      <AdminPanel />
    </ProtectedRoute>
  }
/>
```

Create `src/pages/AdminPanel.jsx`:
```javascript
import axiosInstance from '../api/axiosConfig';

const AdminPanel = () => {
  // Use axiosInstance to call /api/admin/* endpoints
  const fetchUsers = async () => {
    const response = await axiosInstance.get('/api/admin/users');
    return response.data;
  };
  
  // ... component logic
};
```

### Adding System Logs Page
Similar to admin panel, create `src/pages/SystemLogs.jsx` and use `/api/logs` endpoints.

## 📋 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_URL` | Backend API base URL | `http://localhost:5000` |

## 🛡️ Security Features

- **JWT tokens** stored in localStorage
- **Automatic token refresh** on 401 errors
- **Request interceptors** add Authorization headers
- **Protected routes** prevent unauthorized access
- **CORS** configured for localhost development

## 📦 Dependencies

### Production
- `react` & `react-dom` - UI framework
- `react-router-dom` - Client-side routing
- `axios` - HTTP client

### Development
- `vite` - Build tool and dev server
- `tailwindcss` - Utility-first CSS framework
- `autoprefixer` & `postcss` - CSS processing
- `eslint` - Code linting

## 🐛 Troubleshooting

**Issue: Axios 401 errors even after login**
- Check that `VITE_API_URL` matches your backend URL
- Verify JWT tokens are stored in localStorage
- Ensure backend CORS allows your frontend origin

**Issue: Tailwind styles not working**
- Run `npm install` to install all dependencies
- Restart the dev server after changing Tailwind config

**Issue: File upload fails**
- Verify file is `.dcm` or `.dicom` format
- Check file size is under 50MB
- Ensure backend `/api/images/upload` endpoint is working

## 📖 Next Steps

1. **Test the application:**
   - Register a new user
   - Upload a DICOM file
   - View prediction results

2. **Customize styling:**
   - Modify `tailwind.config.js` for colors/themes
   - Update component styles as needed

3. **Add admin features:**
   - Create AdminPanel and SystemLogs pages
   - Integrate with backend admin endpoints

4. **Deploy to production:**
   - Run `npm run build`
   - Flask backend will serve the `dist/` folder

## 📝 License

This project is part of the Lung AI medical imaging system.
