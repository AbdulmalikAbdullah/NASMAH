# 🧪 Postman Backend Testing - Complete Guide

## 🚀 Quick Start

### Step 1: Import Collection
1. Open **Postman**
2. Click **Import** (top left)
3. Select **Upload Files**
4. Choose `postman_collection.json` from the flask_server folder
5. The entire API collection is now ready to test!

### Step 2: Set Up Environment Variables
1. Go to **Environments** (left sidebar)
2. Create new environment called `Lung Cancer AI`
3. Add these variables:
   - `access_token` = (empty, will be filled after login)
   - `refresh_token` = (empty, will be filled after login)
   - `admin_token` = (empty, for admin endpoints)
4. Select this environment in the top-right dropdown

---

## ✅ Testing Flow (Step by Step)

### 1️⃣ Test Health Endpoint
```
GET http://localhost:5000/health
```
**Expected:** `200 OK` with message `healthy`

---

### 2️⃣ Register a New User
```
POST http://localhost:5000/api/auth/register
Content-Type: application/json
```

**Body:**
```json
{
  "fname": "Sarah",
  "lname": "Smith",
  "email": "sarah.smith@test.com",
  "password": "SecurePass123",
  "role": "PATIENT"
}
```

**Expected:** `201 Created` with user details

---

### 3️⃣ Login (Get Tokens)
```
POST http://localhost:5000/api/auth/login
Content-Type: application/json
```

**Body:**
```json
{
  "email": "sarah.smith@test.com",
  "password": "SecurePass123"
}
```

**Expected:** `200 OK` with:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**IMPORTANT:** 
- Copy the `access_token` value
- Go to Postman Environments
- Paste it in `access_token` variable
- Save the environment

---

### 4️⃣ Test Protected Endpoint (Get Images)
```
GET http://localhost:5000/api/images/
Authorization: Bearer {{access_token}}
```

**Expected:** `200 OK` (empty array if no images yet)

---

### 5️⃣ Upload DICOM Image
```
POST http://localhost:5000/api/images/upload
Authorization: Bearer {{access_token}}
Content-Type: multipart/form-data
```

**Form Data:**
- Key: `file`
- Value: Select a `.dcm` or `.dicom` file from your computer

**Expected:** `201 Created` with image details

---

### 6️⃣ Make Prediction
```
POST http://localhost:5000/api/predictions/predict
Authorization: Bearer {{access_token}}
Content-Type: application/json
```

**Body:**
```json
{
  "image_id": 1
}
```

**Expected:** `200 OK` with prediction results

---

## 🔐 Testing Authentication

### Login Flow
1. **Register** → new user
2. **Login** → get tokens
3. **Copy access_token** → save to environment
4. **Use token** → in all protected endpoints
5. **Refresh** → when token expires
6. **Logout** → cleanup session

### Test Invalid Token
```
GET http://localhost:5000/api/images/
Authorization: Bearer invalid_token_here
```
**Expected:** `401 Unauthorized`

### Test Missing Token
```
GET http://localhost:5000/api/images/
(No Authorization header)
```
**Expected:** `401 Unauthorized`

---

## ⚙️ Testing Admin Endpoints

### Get Admin Token
1. Login with admin user
2. Copy the `access_token` 
3. Paste into `admin_token` environment variable
4. Use in admin endpoints

### Try Admin-Only Endpoint
```
GET http://localhost:5000/api/admin/users
Authorization: Bearer {{admin_token}}
```
**Expected:** `200 OK` with user list

### Try as Non-Admin
```
GET http://localhost:5000/api/admin/users
Authorization: Bearer {{access_token}}
```
**Expected:** `403 Forbidden`

---

## 📊 Error Testing

### Test Invalid Email Format
```
POST http://localhost:5000/api/auth/register

{
  "fname": "John",
  "lname": "Doe",
  "email": "invalid-email",
  "password": "SecurePass123"
}
```
**Expected:** `400 Bad Request` - "Invalid email format"

### Test Weak Password
```
POST http://localhost:5000/api/auth/register

{
  "fname": "John",
  "lname": "Doe",
  "email": "john@test.com",
  "password": "weak"
}
```
**Expected:** `400 Bad Request` - "Password must be at least 8 characters..."

### Test Duplicate Email
```
POST http://localhost:5000/api/auth/register

{
  "fname": "Jane",
  "lname": "Doe",
  "email": "sarah.smith@test.com",
  "password": "SecurePass123"
}
```
**Expected:** `409 Conflict` - "Email already registered"

### Test Invalid Credentials
```
POST http://localhost:5000/api/auth/login

{
  "email": "sarah.smith@test.com",
  "password": "WrongPassword"
}
```
**Expected:** `401 Unauthorized` - "Invalid email or password"

---

## 🧬 Advanced Testing

### Use Pre-request Scripts
Add to `/api/auth/login` request **Tests** tab:
```javascript
// Save tokens to environment after login
if (pm.response.code === 200) {
    const jsonData = pm.response.json();
    pm.environment.set("access_token", jsonData.access_token);
    pm.environment.set("refresh_token", jsonData.refresh_token);
    console.log("✅ Tokens saved!");
}
```

### Create Test Assertions
Add to any request **Tests** tab:
```javascript
// Check response status
pm.test("Status is 200", function() {
    pm.response.to.have.status(200);
});

// Check response has expected fields
pm.test("Response has access_token", function() {
    pm.expect(pm.response.json()).to.have.property("access_token");
});
```

---

## 📋 Complete Test Suite Checklist

- [ ] Health endpoint responds
- [ ] Can register new user
- [ ] Can login with correct credentials
- [ ] Login returns access_token
- [ ] Can access protected endpoints with token
- [ ] Cannot access without token (401)
- [ ] Invalid token returns 401
- [ ] Can refresh token
- [ ] Can logout
- [ ] Admin endpoints require admin role
- [ ] Non-admin cannot access admin endpoints (403)
- [ ] Invalid email format rejected
- [ ] Weak password rejected
- [ ] Duplicate email rejected
- [ ] Image upload works
- [ ] Can list images
- [ ] Prediction endpoint works
- [ ] Get all predictions works

---

## 🐛 Troubleshooting

### "Cannot GET /api/auth/register"
- Make sure server is running: `python run.py`
- Check URL is exactly: `http://localhost:5000/api/auth/register`
- Check method is `POST` not `GET`

### "401 Unauthorized"
- Token may have expired (valid for 1 hour)
- Use refresh endpoint to get new token
- Check Authorization header format: `Bearer {TOKEN}`

### "403 Forbidden"
- Your user role is PATIENT, not ADMIN
- Login with admin account for admin endpoints

### "Cannot import collection"
- Make sure `postman_collection.json` is in correct format
- Try exporting from Postman first, then import again

---

## 📚 API Response Examples

### Successful Login
```json
{
  "message": "Login successful",
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "expires_in": 3600,
  "user": {
    "user_id": 1,
    "email": "test@example.com",
    "Fname": "Test",
    "Lname": "User",
    "role": "PATIENT"
  }
}
```

### Error Response
```json
{
  "error": "Invalid email or password"
}
```

### Protected Endpoint Success
```json
[
  {
    "image_id": 1,
    "user_id": 1,
    "file_size_mb": 5.2,
    "uploaded_at": "2026-02-11T15:30:00"
  }
]
```

---

## 🎯 Next Steps

1. ✅ Import Postman collection
2. ✅ Test health endpoint
3. ✅ Register new user
4. ✅ Login and save token
5. ✅ Test protected endpoints
6. ✅ Upload test DICOM file
7. ✅ Make predictions
8. ⏳ Connect React frontend
9. ⏳ Implement image processing
10. ⏳ Deploy to production

**Happy Testing!** 🚀
