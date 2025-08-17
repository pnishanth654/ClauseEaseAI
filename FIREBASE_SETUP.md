# 🔥 Firebase Setup Guide for ClauseEase AI

## **📱 What We're Implementing:**
- **Email OTP**: Traditional email verification
- **Phone OTP**: Firebase Phone Authentication (SMS via Firebase)

## **🚀 Step 1: Create Firebase Project**

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project"
3. Enter project name: `clauseease-ai`
4. Enable Google Analytics (optional)
5. Click "Create project"

## **📱 Step 2: Enable Phone Authentication**

1. In Firebase Console → Authentication
2. Click "Get started"
3. Go to "Sign-in method" tab
4. Click "Phone" provider
5. Click "Enable"
6. Add test phone numbers (for development):
   - `+15555555555` → OTP: `123456`
   - `+15555555556` → OTP: `123456`
   - `+15555555557` → OTP: `123456`

## **🔑 Step 3: Get Firebase Config**

1. In Firebase Console → Project Settings (gear icon)
2. Scroll down to "Your apps"
3. Click "Add app" → Web app (</>)
4. Register app with name: `ClauseEase AI Web`
5. Copy the config object:

```javascript
const firebaseConfig = {
  apiKey: "your-api-key-here",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project-id",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "your-app-id"
};
```

## **🔐 Step 4: Get Service Account Key**

1. In Firebase Console → Project Settings → Service Accounts
2. Click "Generate new private key"
3. Download the JSON file
4. Save it as `firebase-service-account.json` in your project root

## **⚙️ Step 5: Update .env File**

Add these to your `.env` file:

```env
# Firebase Configuration
FIREBASE_API_KEY=your-api-key-from-step-3
FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=your-sender-id
FIREBASE_APP_ID=your-app-id
FIREBASE_SERVICE_ACCOUNT_KEY=firebase-service-account.json
```

## **🧪 Step 6: Test the System**

1. **Start your app**: `python app.py`
2. **Register a new user** with phone number
3. **Go to verification page**
4. **Click "Send SMS via Firebase"**
5. **Complete reCAPTCHA**
6. **Enter the OTP** from SMS
7. **Phone will be verified!**

## **🔍 How It Works:**

### **Email Verification:**
- User gets 6-digit OTP via email
- User enters code in form
- Backend verifies and marks email as verified

### **Phone Verification:**
- User clicks "Send SMS via Firebase"
- Firebase sends SMS with 6-digit OTP
- User enters code from SMS
- Backend verifies Firebase token
- Phone marked as verified

## **🚨 Troubleshooting:**

### **"Firebase: Error (auth/invalid-api-key)"**
- Check your `FIREBASE_API_KEY` in `.env`
- Make sure it matches the one from Firebase Console

### **"Service account key not found"**
- Ensure `firebase-service-account.json` exists
- Check `FIREBASE_SERVICE_ACCOUNT_KEY` path in `.env`

### **"Phone number not supported"**
- Add test phone numbers in Firebase Console
- Use test numbers: `+15555555555`, `+15555555556`, etc.

### **reCAPTCHA not working**
- Check Firebase config in browser console
- Ensure all Firebase config values are correct

## **✅ Success Indicators:**

- ✅ Firebase config loads without errors
- ✅ reCAPTCHA appears when clicking "Send SMS"
- ✅ SMS received with 6-digit code
- ✅ Phone verification completes successfully
- ✅ User can login after verification

## **🔒 Security Features:**

- **reCAPTCHA Protection**: Prevents bot abuse
- **Token Verification**: Server-side Firebase token validation
- **Rate Limiting**: Built-in Firebase rate limiting
- **Secure Storage**: Firebase handles SMS delivery securely

## **📞 Support:**

If you encounter issues:
1. Check Firebase Console for errors
2. Verify all config values in `.env`
3. Check browser console for JavaScript errors
4. Ensure test phone numbers are added to Firebase 