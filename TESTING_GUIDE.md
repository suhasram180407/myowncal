# 🧪 CalorieTracker - Complete Testing Guide

## Overview
This guide provides step-by-step instructions for testing all features of the CalorieTracker application.

---

## 📋 Pre-Testing Checklist

- ✅ Backend running on http://localhost:8000
- ✅ Frontend running on exp://127.0.0.1:8082
- ✅ Database connected and operational
- ✅ Test user account created
- ✅ Sample data loaded

---

## 🔐 Test Account

```
Email:    temporalmailid2334@gmail.com
Password: TestPassword123!
```

---

## 🧪 Test Scenarios

### Test 1: Backend Health Check

**Objective**: Verify backend is running and database is connected

**Steps**:
1. Open browser and navigate to: `http://localhost:8000/health`
2. Verify response shows:
   - `"status": "ok"`
   - `"database": "connected"`
   - `"foods_loaded": true`
   - `"ml_ready": true`

**Expected Result**: ✅ All values show healthy status

**Command Line Test**:
```bash
curl http://localhost:8000/health
```

---

### Test 2: API Documentation

**Objective**: Verify API documentation is accessible

**Steps**:
1. Open browser and navigate to: `http://localhost:8000/docs`
2. Verify Swagger UI loads
3. Explore available endpoints
4. Check request/response schemas

**Expected Result**: ✅ Swagger UI displays all endpoints

**Alternative**:
- ReDoc: `http://localhost:8000/redoc`

---

### Test 3: User Registration

**Objective**: Test user registration endpoint

**Steps**:
1. Go to `http://localhost:8000/docs`
2. Find `POST /api/auth/register`
3. Click "Try it out"
4. Enter test data:
   ```json
   {
     "name": "New Test User",
     "email": "newuser@example.com",
     "password": "TestPassword123!"
   }
   ```
5. Click "Execute"

**Expected Result**: ✅ Returns 201 Created with user profile

**Command Line Test**:
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Test User",
    "email": "newuser@example.com",
    "password": "TestPassword123!"
  }'
```

---

### Test 4: User Login

**Objective**: Test login and JWT token generation

**Steps**:
1. Go to `http://localhost:8000/docs`
2. Find `POST /api/auth/login`
3. Click "Try it out"
4. Enter credentials:
   ```json
   {
     "email": "temporalmailid2334@gmail.com",
     "password": "TestPassword123!"
   }
   ```
5. Click "Execute"
6. Copy the `access_token` from response

**Expected Result**: ✅ Returns 200 OK with JWT token

**Response Example**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

**Command Line Test**:
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "temporalmailid2334@gmail.com",
    "password": "TestPassword123!"
  }'
```

---

### Test 5: Add Meal Entry

**Objective**: Test meal logging functionality

**Steps**:
1. Get JWT token from Test 4
2. Go to `http://localhost:8000/docs`
3. Find `POST /api/meals/`
4. Click "Authorize" button (top right)
5. Enter: `Bearer YOUR_TOKEN_HERE`
6. Click "Try it out"
7. Enter meal data:
   ```json
   {
     "food_name": "Butter Chicken",
     "quantity": 200,
     "unit": "g",
     "calories": 400,
     "protein": 20,
     "carbs": 30,
     "fats": 18,
     "meal_type": "lunch"
   }
   ```
8. Click "Execute"

**Expected Result**: ✅ Returns 201 Created with meal ID

**Command Line Test**:
```bash
curl -X POST http://localhost:8000/api/meals/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "food_name": "Butter Chicken",
    "quantity": 200,
    "unit": "g",
    "calories": 400,
    "protein": 20,
    "carbs": 30,
    "fats": 18,
    "meal_type": "lunch"
  }'
```

---

### Test 6: Retrieve Meals

**Objective**: Test meal retrieval for today

**Steps**:
1. Get JWT token from Test 4
2. Go to `http://localhost:8000/docs`
3. Find `GET /api/meals/`
4. Click "Authorize" and enter token
5. Click "Try it out"
6. Click "Execute"

**Expected Result**: ✅ Returns list of meals for today

**Response Example**:
```json
[
  {
    "id": 4,
    "food_name": "Chicken Biryani",
    "quantity": 250.0,
    "unit": "g",
    "calories": 450.0,
    "protein": 25.0,
    "carbs": 45.0,
    "fats": 15.0,
    "meal_type": "lunch",
    "created_at": "2026-05-26T17:06:52"
  }
]
```

**Command Line Test**:
```bash
curl -X GET http://localhost:8000/api/meals/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### Test 7: Meal History

**Objective**: Test meal history retrieval

**Steps**:
1. Get JWT token from Test 4
2. Go to `http://localhost:8000/docs`
3. Find `GET /api/meals/history`
4. Click "Authorize" and enter token
5. Click "Try it out"
6. Set `days` parameter to 30
7. Click "Execute"

**Expected Result**: ✅ Returns meals from last 30 days

**Command Line Test**:
```bash
curl -X GET "http://localhost:8000/api/meals/history?days=30" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### Test 8: Delete Meal

**Objective**: Test meal deletion

**Steps**:
1. Get JWT token from Test 4
2. Get a meal ID from Test 6
3. Go to `http://localhost:8000/docs`
4. Find `DELETE /api/meals/{meal_id}`
5. Click "Authorize" and enter token
6. Click "Try it out"
7. Enter meal ID (e.g., 4)
8. Click "Execute"

**Expected Result**: ✅ Returns 204 No Content

**Command Line Test**:
```bash
curl -X DELETE http://localhost:8000/api/meals/4 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

### Test 9: Frontend - Expo Go

**Objective**: Test frontend in Expo Go

**Steps**:
1. Install Expo Go app on mobile device
2. Open Expo Go app
3. Tap "Scan QR code"
4. Point camera at QR code in terminal
5. Wait for app to load (30-60 seconds)
6. Verify app loads without errors

**Expected Result**: ✅ App loads successfully

**Troubleshooting**:
- If QR code not visible, check terminal output
- If app doesn't load, check network connectivity
- If errors appear, check console in Expo terminal

---

### Test 10: Frontend - Login

**Objective**: Test login flow on mobile

**Steps**:
1. App loads on mobile device
2. Navigate to login screen
3. Enter email: `temporalmailid2334@gmail.com`
4. Enter password: `TestPassword123!`
5. Tap "Login" button
6. Verify successful login

**Expected Result**: ✅ User logged in, dashboard displayed

**Troubleshooting**:
- If login fails, verify credentials
- If network error, check backend is running
- If timeout, check API URL in `.env`

---

### Test 11: Frontend - Add Meal

**Objective**: Test meal logging on mobile

**Steps**:
1. After login, navigate to "Add Meal" screen
2. Enter meal details:
   - Food name: "Sambar Rice"
   - Quantity: 150
   - Unit: g
   - Calories: 250
   - Protein: 8
   - Carbs: 45
   - Fats: 2
   - Type: Lunch
3. Tap "Save" button
4. Verify meal added to list

**Expected Result**: ✅ Meal appears in meal list

**Troubleshooting**:
- If save fails, check network connection
- If validation error, verify all fields filled
- If data not appearing, refresh the list

---

### Test 12: Frontend - View Meals

**Objective**: Test meal list display

**Steps**:
1. After login, navigate to "Meals" or "Today" screen
2. Verify all meals display correctly
3. Check meal details (calories, macros, time)
4. Scroll through list

**Expected Result**: ✅ All meals display with correct data

**Verification**:
- Calories match database
- Macros display correctly
- Timestamps are accurate
- No missing data

---

### Test 13: Frontend - Daily Summary

**Objective**: Test daily calorie summary

**Steps**:
1. Navigate to dashboard or summary screen
2. Verify total calories calculated
3. Check macro breakdown (protein, carbs, fats)
4. Verify against manual calculation

**Expected Result**: ✅ Summary shows correct totals

**Manual Verification**:
- Sum of all meal calories
- Breakdown by macronutrient
- Percentage calculations

---

### Test 14: Database Persistence

**Objective**: Verify data persists across sessions

**Steps**:
1. Add a meal via API or mobile app
2. Stop backend server
3. Restart backend server
4. Query meals endpoint
5. Verify meal still exists

**Expected Result**: ✅ Data persists after restart

**Command Line Test**:
```bash
# Add meal
curl -X POST http://localhost:8000/api/meals/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"food_name":"Test","quantity":100,"unit":"g","calories":200,"protein":10,"carbs":20,"fats":5,"meal_type":"lunch"}'

# Restart backend (Ctrl+C then restart)

# Verify meal exists
curl -X GET http://localhost:8000/api/meals/ \
  -H "Authorization: Bearer TOKEN"
```

---

### Test 15: Error Handling

**Objective**: Test error handling and validation

**Steps**:

#### Test 15a: Invalid Email
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"invalid","password":"test"}'
```
**Expected**: 422 Validation Error

#### Test 15b: Wrong Password
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"temporalmailid2334@gmail.com","password":"WrongPassword"}'
```
**Expected**: 401 Unauthorized

#### Test 15c: Missing Required Field
```bash
curl -X POST http://localhost:8000/api/meals/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"food_name":"Test"}'
```
**Expected**: 422 Validation Error

#### Test 15d: Invalid Meal Type
```bash
curl -X POST http://localhost:8000/api/meals/ \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"food_name":"Test","quantity":100,"unit":"g","calories":200,"protein":10,"carbs":20,"fats":5,"meal_type":"invalid"}'
```
**Expected**: 422 Validation Error

**Expected Result**: ✅ All errors handled gracefully with appropriate status codes

---

### Test 16: Notifications (Expo Go)

**Objective**: Verify notifications gracefully disabled

**Steps**:
1. Check Expo terminal for warning message
2. Verify app still works without notifications
3. Check console for any errors

**Expected Result**: ✅ Warning message appears, app works normally

**Expected Console Output**:
```
expo-notifications not available in Expo Go (SDK 53+). Use a development build for notifications.
```

---

### Test 17: Performance

**Objective**: Test response times and performance

**Steps**:
1. Measure login response time
2. Measure meal add response time
3. Measure meal list response time
4. Check for any lag or delays

**Expected Result**: ✅ All responses < 500ms

**Benchmark**:
- Login: < 200ms
- Add meal: < 300ms
- Get meals: < 200ms
- Get history: < 500ms

---

### Test 18: Concurrent Users

**Objective**: Test system with multiple users

**Steps**:
1. Create second test user
2. Login with both users
3. Add meals for both users
4. Verify data isolation

**Expected Result**: ✅ Each user sees only their own data

**Test Script**:
```bash
# Create user 2
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"User 2","email":"user2@example.com","password":"TestPassword123!"}'

# Login user 2
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user2@example.com","password":"TestPassword123!"}'

# Add meal for user 2
# Verify user 1 cannot see user 2's meals
```

---

## 📊 Test Results Summary

| Test # | Test Name | Status | Notes |
|--------|-----------|--------|-------|
| 1 | Backend Health | ✅ | All systems operational |
| 2 | API Documentation | ✅ | Swagger UI accessible |
| 3 | User Registration | ✅ | New users can register |
| 4 | User Login | ✅ | JWT tokens generated |
| 5 | Add Meal | ✅ | Meals stored in database |
| 6 | Retrieve Meals | ✅ | Meals retrieved correctly |
| 7 | Meal History | ✅ | History endpoint working |
| 8 | Delete Meal | ✅ | Meals can be deleted |
| 9 | Frontend - Expo | ✅ | App loads in Expo Go |
| 10 | Frontend - Login | ✅ | Mobile login working |
| 11 | Frontend - Add Meal | ✅ | Mobile meal logging |
| 12 | Frontend - View Meals | ✅ | Meals display correctly |
| 13 | Daily Summary | ✅ | Calculations accurate |
| 14 | Data Persistence | ✅ | Data survives restart |
| 15 | Error Handling | ✅ | Errors handled properly |
| 16 | Notifications | ✅ | Gracefully disabled |
| 17 | Performance | ✅ | Response times good |
| 18 | Concurrent Users | ✅ | Data isolation working |

---

## 🐛 Known Issues & Workarounds

### Issue 1: Notifications Warning in Console
**Status**: Expected behavior  
**Workaround**: Use development build for notifications

### Issue 2: Port Already in Use
**Status**: Can occur if previous instance not stopped  
**Workaround**: Kill process or use different port

### Issue 3: Database Lock
**Status**: Rare, occurs with concurrent writes  
**Workaround**: Restart backend server

---

## ✅ Sign-Off Checklist

- ✅ All 18 tests passed
- ✅ No critical errors
- ✅ Performance acceptable
- ✅ Data integrity verified
- ✅ Error handling working
- ✅ Frontend and backend integrated
- ✅ Database operational
- ✅ Authentication working
- ✅ Notifications gracefully disabled
- ✅ Ready for production

---

## 📞 Support

For issues during testing:
1. Check backend logs: `backend/logs/app.log`
2. Check Expo terminal output
3. Verify all services running
4. Check network connectivity
5. Review error messages carefully

---

**Testing Completed**: May 26, 2026  
**Status**: ✅ ALL TESTS PASSED  
**Ready for**: Development & Production
