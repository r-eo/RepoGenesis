# Render + Vercel Deployment Guide

## Quick Fix for CORS Errors

### ✅ Backend Changes Made
The CORS configuration in `server/app.py` has been updated to:
- Allow all origins (`origins: "*"`)
- Support all necessary HTTP methods
- Include proper headers
- Enable credentials

### 🔧 Steps to Fix CORS on Your Deployment

#### 1. Update Backend on Render

**Option A: Automatic (Recommended)**
```bash
# Commit and push changes
git add server/app.py
git commit -m "Fix CORS for production"
git push origin main
```
Render will automatically redeploy.

**Option B: Manual Redeploy**
1. Go to your Render dashboard
2. Find your service "repogenesis-1"
3. Click "Manual Deploy" → "Deploy latest commit"

#### 2. Verify Backend is Running
```bash
curl https://repogenesis-1.onrender.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-22T...",
  "service": "sleep-quest-api"
}
```

#### 3. Update Frontend API URL

Your `client/src/sleepApi.js` already points to:
```javascript
const API_URL = 'https://repogenesis-1.onrender.com/api';
```

**If using environment variables (recommended):**
1. Create `client/.env.production`:
   ```
   REACT_APP_API_URL=https://repogenesis-1.onrender.com/api
   ```

2. Update `client/src/sleepApi.js`:
   ```javascript
   const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';
   ```

#### 4. Deploy Frontend to Vercel

**Option A: Vercel CLI**
```bash
cd client
npm install -g vercel
vercel --prod
```

**Option B: Vercel Dashboard**
1. Go to vercel.com
2. Import your GitHub repository
3. Set Root Directory: `client`
4. Framework Preset: Create React App
5. Build Command: `npm run build`
6. Output Directory: `build`
7. Deploy

#### 5. Configure Environment Variables on Vercel

1. Go to your Vercel project settings
2. Navigate to "Environment Variables"
3. Add:
   - **Name:** `REACT_APP_API_URL`
   - **Value:** `https://repogenesis-1.onrender.com/api`
   - **Environment:** Production
4. Redeploy

---

## Troubleshooting CORS Errors

### Error: "Access-Control-Allow-Origin"

**Cause:** Backend not allowing frontend origin

**Solution:**
1. Check backend logs on Render
2. Verify CORS configuration in `server/app.py`
3. Ensure backend is running: `https://repogenesis-1.onrender.com/health`

### Error: "Network Error"

**Cause:** Backend not reachable or wrong URL

**Solution:**
1. Verify API URL in `sleepApi.js`
2. Check Render service status
3. Test backend directly: `curl https://repogenesis-1.onrender.com/api/auth/login`

### Error: "Preflight request failed"

**Cause:** OPTIONS method not allowed

**Solution:**
Already fixed! The updated CORS config includes:
```python
methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"]
```

---

## Environment Variables Summary

### Backend (Render)
Set these in Render Dashboard → Environment:

| Variable | Value | Required |
|----------|-------|----------|
| `SECRET_KEY` | Random string (generate one) | Yes |
| `DEBUG` | `False` | Yes |
| `FLASK_ENV` | `production` | Yes |

### Frontend (Vercel)
Set these in Vercel Dashboard → Environment Variables:

| Variable | Value | Required |
|----------|-------|----------|
| `REACT_APP_API_URL` | `https://repogenesis-1.onrender.com/api` | Yes |

---

## Deployment Checklist

### Backend (Render)
- [x] CORS configuration updated
- [x] Health check endpoint added
- [ ] Environment variables set
- [ ] Latest code deployed
- [ ] Service is running
- [ ] Database initialized

### Frontend (Vercel)
- [x] API URL updated to production
- [ ] Environment variables set
- [ ] Build successful
- [ ] Deployed to production
- [ ] Can access the site

### Testing
- [ ] Can create account
- [ ] Can login
- [ ] Can use /sleep command
- [ ] Reliability badge shows
- [ ] No CORS errors in console

---

## Quick Test Commands

### Test Backend Health
```bash
curl https://repogenesis-1.onrender.com/health
```

### Test Registration
```bash
curl -X POST https://repogenesis-1.onrender.com/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"test123"}'
```

### Test CORS Headers
```bash
curl -I -X OPTIONS https://repogenesis-1.onrender.com/api/auth/register \
  -H "Origin: https://your-app.vercel.app" \
  -H "Access-Control-Request-Method: POST"
```

Look for:
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS
```

---

## Production URLs

- **Backend API:** https://repogenesis-1.onrender.com
- **Frontend:** https://your-app.vercel.app (update after deployment)
- **Health Check:** https://repogenesis-1.onrender.com/health

---

## Need Help?

1. Check Render logs for backend errors
2. Check Vercel logs for frontend build errors
3. Check browser console for CORS/network errors
4. Verify environment variables are set correctly

---

**Last Updated:** 2025-11-22  
**Status:** ✅ CORS Configuration Fixed
