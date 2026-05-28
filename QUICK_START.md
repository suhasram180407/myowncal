# CalorieTracker - Quick Start Guide

## 🚀 Running the Project

### Backend (FastAPI)
```bash
cd backend
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
- **URL**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **Status**: Running ✅

### Frontend (React Native + Expo)
```bash
cd frontend/artifacts/mobile
pnpm install
pnpm exec expo start --localhost --port 8082
```
- **URL**: exp://127.0.0.1:8082
- **Web**: http://localhost:8082
- **Status**: Running ✅

---

## 🔐 Test Account

**Email**: temporalmailid2334@gmail.com  
**Password**: TestPassword123!

---

## 📊 Database Status

✅ **Connected to PostgreSQL**
- 5 test meals stored
- User account created
- All data persisted correctly

### Sample Data
| Food | Calories | Type | Date |
|------|----------|------|------|
| Chicken Biryani | 450 | Lunch | 2026-05-26 |
| Paneer Butter Masala | 380 | Dinner | 2026-05-26 |
| Idli with Sambar | 200 | Breakfast | 2026-05-26 |
| Dosa with Chutney | 320 | Breakfast | 2026-05-26 |
| Samosa | 280 | Snacks | 2026-05-26 |

**Total**: 1,630 kcal

---

## 🔧 Fixes Applied

### Expo Notifications Error - FIXED ✅

**Issue**: `expo-notifications was removed from Expo Go with SDK 53`

**Solution**:
1. Removed `expo-notifications` plugin from `app.json`
2. Added graceful fallback in `lib/notifications.ts`
3. App now works without errors in Expo Go

**Files Modified**:
- `frontend/artifacts/mobile/app.json`
- `frontend/artifacts/mobile/lib/notifications.ts`

---

## 📱 How to Test on Mobile

1. **Install Expo Go**
   - Android: Google Play Store
   - iOS: App Store

2. **Scan QR Code**
   - Open Expo Go app
   - Tap "Scan QR code"
   - Point at the QR code in terminal

3. **Login**
   - Email: temporalmailid2334@gmail.com
   - Password: TestPassword123!

4. **Add Meals**
   - Log your food intake
   - View calorie tracking
   - Check daily summary

---

## 🧪 API Testing

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "temporalmailid2334@gmail.com",
    "password": "TestPassword123!"
  }'
```

### Add Meal
```bash
curl -X POST http://localhost:8000/api/meals/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "food_name": "Chicken Biryani",
    "quantity": 250,
    "unit": "g",
    "calories": 450,
    "protein": 25,
    "carbs": 45,
    "fats": 15,
    "meal_type": "lunch"
  }'
```

### Get Meals
```bash
curl -X GET http://localhost:8000/api/meals/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## 📋 Checklist

- ✅ Backend running on port 8000
- ✅ Frontend running on port 8082
- ✅ Database connected
- ✅ User account created
- ✅ Test data added (5 meals)
- ✅ Login working
- ✅ Notifications error fixed
- ✅ API endpoints tested
- ✅ Data persisted correctly

---

## 🆘 Troubleshooting

### Backend won't start
```bash
# Check if port 8000 is in use
netstat -ano | findstr :8000

# Kill process if needed
taskkill /PID <PID> /F
```

### Frontend won't start
```bash
# Clear cache
rm -r node_modules
pnpm install

# Try different port
pnpm exec expo start --localhost --port 8083
```

### Database connection error
- Check `.env` file for correct DATABASE_URL
- Verify PostgreSQL is running
- Check connection string format

### Notifications still showing error
- This is expected in Expo Go (SDK 53+)
- Use development build for full notifications
- App works fine without notifications

---

## 📞 Support

**Backend Logs**: `backend/logs/app.log`  
**Frontend Logs**: Check Expo terminal output  
**API Docs**: http://localhost:8000/docs

---

**Last Updated**: May 26, 2026  
**Status**: All Systems Operational ✅
