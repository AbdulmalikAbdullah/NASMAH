# 📮 Postman Testing Guide - Lung Cancer AI Backend

## Server URL
```
http://localhost:5000
```

---

## 🏥 1. Health Check (No Auth Required)
Test if the server is running

**Request:**
```
GET http://localhost:5000/health
```

**Expected Response (200):**
```json
{
  "status": "healthy",
  "service": "Lung Cancer AI Backend"
}
```

---

## 🔐 2. Authentication Endpoints

### 2.1 Register New User
**Request:**
```
POST http://localhost:5000/api/auth/register
Content-Type: application/json
```

**Body:**
```json
{
  "fname": "John",
  "lname": "Doe",
  "email": "john.doe@example.com",
  "password": "SecurePass123",
  "role": "PATIENT"
}
```

**Expected Response (501 - Not Yet Implemented):**
```json
{
  "message": "Registration endpoint - to be implemented"
}
```

---

### 2.2 Login User
**Request:**
```
POST http://localhost:5000/api/auth/login
Content-Type: application/json
```

**Body:**
```json
{
  "email": "test@example.com",
  "password": "TestPass123"
}
```

**Expected Response (501 - Not Yet Implemented):**
```json
{
  "message": "Login endpoint - to be implemented"
}
```

**Once Implemented - Expected Response (200):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "user": {
    "user_id": 1,
    "email": "test@example.com",
    "Fname": "Test",
    "Lname": "User",
    "role": "PATIENT"
  }
}
```

---

### 2.3 Logout User
**Request:**
```
POST http://localhost:5000/api/auth/logout
Content-Type: application/json
Authorization: Bearer {ACCESS_TOKEN}
```

**Headers:**
- `Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`

**Expected Response (501 - Not Yet Implemented):**
```json
{
  "message": "Logout endpoint - to be implemented"
}
```

---

### 2.4 Refresh Token
**Request:**
```
POST http://localhost:5000/api/auth/refresh
Content-Type: application/json
Authorization: Bearer {REFRESH_TOKEN}
```

**Headers:**
- `Authorization: Bearer {REFRESH_TOKEN}`

**Expected Response (501 - Not Yet Implemented):**
```json
{
  "message": "Refresh endpoint - to be implemented"
}
```

---

## 📁 3. Image Upload Endpoints

### 3.1 Upload DICOM Image
**Request:**
```
POST http://localhost:5000/api/images/upload
Content-Type: multipart/form-data
Authorization: Bearer {ACCESS_TOKEN}
```

**Form Data:**
- Key: `file` | Value: Select your `.dcm` or `.dicom` file

**Headers:**
- `Authorization: Bearer {ACCESS_TOKEN}`

**Expected Response (501 - Not Yet Implemented):**
```json
{
  "message": "Image upload endpoint - to be implemented"
}
```

**Once Implemented - Expected Response (201):**
```json
{
  "image_id": 1,
  "user_id": 1,
  "image_path": "/uploads/1/scan_001.dcm",
  "file_extension": "dcm",
  "file_size_mb": 5.2,
  "file_hash": "a1b2c3d4e5f6...",
  "width_mm": 256.0,
  "height_mm": 256.0,
  "depth_mm": 128.0,
  "is_valid": true,
  "uploaded_at": "2026-02-11T15:30:00"
}
```

---

### 3.2 Get All User Images
**Request:**
```
GET http://localhost:5000/api/images/
Authorization: Bearer {ACCESS_TOKEN}
```

**Headers:**
- `Authorization: Bearer {ACCESS_TOKEN}`

**Expected Response (501 - Not Yet Implemented):**
```json
{
  "message": "Get images endpoint - to be implemented"
}
```

**Once Implemented - Expected Response (200):**
```json
[
  {
    "image_id": 1,
    "user_id": 1,
    "image_path": "/uploads/1/scan_001.dcm",
    "file_extension": "dcm",
    "file_size_mb": 5.2,
    "uploaded_at": "2026-02-11T15:30:00"
  },
  {
    "image_id": 2,
    "user_id": 1,
    "image_path": "/uploads/1/scan_002.dcm",
    "file_extension": "dcm",
    "file_size_mb": 4.8,
    "uploaded_at": "2026-02-11T16:00:00"
  }
]
```

---

### 3.3 Get Specific Image
**Request:**
```
GET http://localhost:5000/api/images/1
Authorization: Bearer {ACCESS_TOKEN}
```

**Replace `1` with the image ID**

**Headers:**
- `Authorization: Bearer {ACCESS_TOKEN}`

**Expected Response (501 - Not Yet Implemented):**
```json
{
  "message": "Get image 1 endpoint - to be implemented"
}
```

---

### 3.4 Delete Image
**Request:**
```
DELETE http://localhost:5000/api/images/1
Authorization: Bearer {ACCESS_TOKEN}
```

**Headers:**
- `Authorization: Bearer {ACCESS_TOKEN}`

**Expected Response (501 - Not Yet Implemented):**
```json
{
  "message": "Delete image 1 endpoint - to be implemented"
}
```

---

## 🤖 4. Prediction Endpoints

### 4.1 Make Prediction
**Request:**
```
POST http://localhost:5000/api/predictions/predict
Content-Type: application/json
Authorization: Bearer {ACCESS_TOKEN}
```

**Body:**
```json
{
  "image_id": 1
}
```

**Headers:**
- `Authorization: Bearer {ACCESS_TOKEN}`

**Expected Response (501 - Not Yet Implemented):**
```json
{
  "message": "Prediction endpoint - to be implemented"
}
```

**Once Implemented - Expected Response (200):**
```json
{
  "prediction_id": 1,
  "image_id": 1,
  "cancer_stage": "2",
  "confidence": 0.92,
  "model_name": "LungCancerClassifier_v1",
  "created_at": "2026-02-11T15:35:00"
}
```

---

### 4.2 Get All Predictions
**Request:**
```
GET http://localhost:5000/api/predictions/
Authorization: Bearer {ACCESS_TOKEN}
```

**Headers:**
- `Authorization: Bearer {ACCESS_TOKEN}`

**Once Implemented - Expected Response (200):**
```json
[
  {
    "prediction_id": 1,
    "image_id": 1,
    "cancer_stage": "2",
    "confidence": 0.92,
    "model_name": "LungCancerClassifier_v1",
    "created_at": "2026-02-11T15:35:00"
  },
  {
    "prediction_id": 2,
    "image_id": 2,
    "cancer_stage": "1",
    "confidence": 0.78,
    "model_name": "LungCancerClassifier_v1",
    "created_at": "2026-02-11T16:05:00"
  }
]
```

---

### 4.3 Get Prediction History (with Pagination)
**Request:**
```
GET http://localhost:5000/api/predictions/history?limit=10
Authorization: Bearer {ACCESS_TOKEN}
```

**Headers:**
- `Authorization: Bearer {ACCESS_TOKEN}`

**Query Parameters:**
- `limit`: Number of predictions (optional, default 50)

---

## ⚙️ 5. Admin Endpoints

### 5.1 Get All Users (Admin Only)
**Request:**
```
GET http://localhost:5000/api/admin/users
Authorization: Bearer {ADMIN_TOKEN}
```

**Headers:**
- `Authorization: Bearer {ADMIN_TOKEN}` (requires ADMIN role)

**Expected Response (403 if not admin):**
```json
{
  "error": "Admin access required"
}
```

---

### 5.2 Get Specific User (Admin Only)
**Request:**
```
GET http://localhost:5000/api/admin/users/1
Authorization: Bearer {ADMIN_TOKEN}
```

**Headers:**
- `Authorization: Bearer {ADMIN_TOKEN}`

**Expected Response (200):**
```json
{
  "user_id": 1,
  "Fname": "Test",
  "Lname": "User",
  "email": "test@example.com",
  "role": "PATIENT",
  "is_active": true,
  "created_at": "2026-02-11T10:00:00"
}
```

---

### 5.3 Activate/Deactivate User (Admin Only)
**Request:**
```
PUT http://localhost:5000/api/admin/users/1/activate
Content-Type: application/json
Authorization: Bearer {ADMIN_TOKEN}
```

**Body:**
```json
{
  "is_active": false
}
```

**Headers:**
- `Authorization: Bearer {ADMIN_TOKEN}`

---

### 5.4 Get System Statistics (Admin Only)
**Request:**
```
GET http://localhost:5000/api/admin/stats
Authorization: Bearer {ADMIN_TOKEN}
```

**Headers:**
- `Authorization: Bearer {ADMIN_TOKEN}`

**Expected Response (200):**
```json
{
  "total_users": 5,
  "total_images": 12,
  "total_predictions": 8,
  "average_confidence": 0.87
}
```

---

## 📋 6. Logging Endpoints

### 6.1 Get System Logs (Admin Only)
**Request:**
```
GET http://localhost:5000/api/logs/?limit=25&action=login
Authorization: Bearer {ADMIN_TOKEN}
```

**Headers:**
- `Authorization: Bearer {ADMIN_TOKEN}`

**Query Parameters:**
- `limit`: Number of logs (optional)
- `action`: Filter by action (optional)

---

### 6.2 Get User Logs (Admin Only)
**Request:**
```
GET http://localhost:5000/api/logs/user/1
Authorization: Bearer {ADMIN_TOKEN}
```

**Headers:**
- `Authorization: Bearer {ADMIN_TOKEN}`

---

### 6.3 Get Log Actions (Admin Only)
**Request:**
```
GET http://localhost:5000/api/logs/actions
Authorization: Bearer {ADMIN_TOKEN}
```

**Headers:**
- `Authorization: Bearer {ADMIN_TOKEN}`

**Expected Response (200):**
```json
{
  "actions": [
    "USER_LOGIN",
    "IMAGE_UPLOAD",
    "PREDICTION_MADE",
    "USER_LOGOUT"
  ]
}
```

---

## 🔑 Authentication Flow Example

### Step 1: Login
```
POST http://localhost:5000/api/auth/login
Content-Type: application/json

{
  "email": "test@example.com",
  "password": "TestPass123"
}
```

**Save the `access_token` from response**

### Step 2: Use Token for Protected Endpoints
```
GET http://localhost:5000/api/images/
Authorization: Bearer {ACCESS_TOKEN_FROM_STEP_1}
```

### Step 3: Refresh Token (when expired)
```
POST http://localhost:5000/api/auth/refresh
Authorization: Bearer {REFRESH_TOKEN}
```

### Step 4: Logout
```
POST http://localhost:5000/api/auth/logout
Authorization: Bearer {ACCESS_TOKEN}
```

---

## ⚠️ Error Responses

### 400 Bad Request
```json
{
  "error": "Missing required fields: email, password"
}
```

### 401 Unauthorized
```json
{
  "error": "Token is missing"
}
```

### 403 Forbidden
```json
{
  "error": "Admin access required"
}
```

### 404 Not Found
```json
{
  "error": "Image not found"
}
```

### 501 Not Implemented
```json
{
  "message": "Endpoint - to be implemented"
}
```

---

## 📌 Postman Setup Tips

1. **Create an Environment Variable** for your token:
   - Click "Environments" → Create new
   - Add variable: `token` = your JWT token
   - Use `{{token}}` in Authorization header

2. **Reuse Token**:
   - After login, go to "Tests" tab
   - Add: `pm.environment.set("token", pm.response.json().access_token);`
   - Now all subsequent requests auto-use this token

3. **Import Collection**:
   - You can export these as a Postman Collection
   - File → Import → Paste raw or upload

---

## 🧪 Quick Test Checklist

- [ ] Test `/health` endpoint
- [ ] Test `/api/auth/register` with various inputs
- [ ] Test `/api/auth/login` with correct/incorrect credentials
- [ ] Test protected endpoints without token (should get 401)
- [ ] Test admin endpoints with non-admin token (should get 403)
- [ ] Test image upload with invalid file type
- [ ] Test prediction with non-existent image ID

