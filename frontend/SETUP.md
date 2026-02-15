# 🚀 Quick Setup Guide

## Step-by-Step Installation

### 1. Install Dependencies
```bash
cd C:\Users\os234\Desktop\lung_project\frontend
npm install
```

This will install:
- React & React DOM
- React Router DOM (routing)
- Axios (API calls)
- Tailwind CSS (styling)
- Vite (build tool)

### 2. Verify Environment Configuration
The `.env` file is already configured:
```
VITE_API_URL=http://localhost:5000
```

**Important:** Make sure your Flask backend is running on port 5000!

### 3. Start Development Server
```bash
npm run dev
```

The frontend will be available at: `http://localhost:5173`

### 4. Test the Application

#### Test Authentication:
1. Open `http://localhost:5173`
2. Click "Register" and create an account
3. You'll be redirected to the Dashboard

#### Test File Upload & Prediction:
1. Prepare a `.dcm` DICOM file
2. Drag and drop it into the upload area (or click to browse)
3. Click "Upload and Analyze"
4. Wait for the AI prediction result

### 5. Build for Production (Optional)
When ready to deploy:
```bash
npm run build
```

This creates a `dist/` folder that your Flask backend can serve automatically.

## 📁 Project Structure Created

```
frontend/src/
├── api/
│   └── axiosConfig.js              ✅ JWT interceptors
├── components/
│   ├── common/
│   │   ├── Button.jsx              ✅ Reusable button
│   │   ├── Input.jsx               ✅ Reusable input
│   │   ├── LoadingSpinner.jsx      ✅ Loading indicator
│   │   └── Navbar.jsx              ✅ Navigation
│   ├── auth/
│   │   └── ProtectedRoute.jsx      ✅ Route protection
│   └── dashboard/
│       ├── FileUpload.jsx          ✅ DICOM uploader
│       └── PredictionResult.jsx    ✅ AI results display
├── context/
│   └── AuthContext.jsx             ✅ Global auth state
├── hooks/
│   └── useApi.js                   ✅ API state management
├── pages/
│   ├── Dashboard.jsx               ✅ Main dashboard
│   ├── Login.jsx                   ✅ Login page
│   └── Register.jsx                ✅ Registration page
├── App.jsx                         ✅ Routing setup
├── main.jsx                        ✅ Entry point
└── index.css                       ✅ Tailwind setup
```

## 🔍 Verification Checklist

- [ ] Backend is running on `http://localhost:5000`
- [ ] Frontend dependencies installed (`node_modules/` exists)
- [ ] Dev server starts without errors
- [ ] Can register a new user
- [ ] Can login with credentials
- [ ] Can upload a DICOM file
- [ ] Can see prediction results

## 🐛 Common Issues

**"npm install" fails:**
- Make sure you have Node.js 16+ installed
- Delete `node_modules/` and `package-lock.json`, then try again

**Backend connection fails:**
- Check Flask server is running: `python backend/run.py`
- Verify CORS is enabled in Flask
- Check `.env` has correct `VITE_API_URL`

**Tailwind styles not loading:**
- Restart the dev server after installing dependencies
- Clear browser cache

## 📖 Next Steps

1. **Customize the UI:**
   - Edit colors in `tailwind.config.js`
   - Modify component styles

2. **Add Admin Features:**
   - Create `src/pages/AdminPanel.jsx`
   - Uncomment admin routes in `App.jsx`
   - See `FRONTEND_GUIDE.md` for examples

3. **Add System Logs:**
   - Create `src/pages/SystemLogs.jsx`
   - Use `/api/logs` endpoints

4. **Deploy:**
   - Run `npm run build`
   - Flask will serve from `dist/` folder automatically

## 📞 Need Help?

Check the detailed documentation in `FRONTEND_GUIDE.md` for:
- Full API integration guide
- Component examples
- Customization instructions
- Security best practices
