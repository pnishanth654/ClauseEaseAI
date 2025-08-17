# Firebase Test Configuration Guide

## 🔧 **Setup for Development/Testing**

### **1. Firebase Console Setup**
1. Go to [Firebase Console](https://console.firebase.google.com)
2. Create a new project or select existing project
3. Enable Phone Authentication:
   - Go to Authentication > Sign-in methods
   - Enable "Phone" provider
   - Add test phone numbers (see below)

### **2. Test Phone Numbers**
In Firebase Console → Authentication → Phone → Add test numbers:

| Phone Number | OTP Code | Purpose |
|--------------|----------|---------|
| +15555555555 | 123456 | Test number 1 |
| +15555555556 | 123456 | Test number 2 |
| +15555555557 | 123456 | Test number 3 |

### **3. Environment Variables**
Add to your `.env` file:

```env
# Firebase Configuration
FIREBASE_API_KEY=your-api-key-from-firebase-console
FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
FIREBASE_MESSAGING_SENDER_ID=your-sender-id
FIREBASE_APP_ID=your-app-id
FIREBASE_SERVICE_ACCOUNT_KEY=path/to/serviceAccountKey.json
```

### **4. Get Firebase Config**
1. In Firebase Console → Project Settings → General
2. Scroll down to "Your apps" section
3. Click on the web app (</>) icon
4. Copy the config object

### **5. Service Account Key**
1. In Firebase Console → Project Settings → Service Accounts
2. Click "Generate new private key"
3. Download the JSON file
4. Save it securely and update the path in `.env`

## 🧪 **Testing Without SMS Costs**

### **Test Phone Numbers**
Firebase provides test phone numbers that always return fixed OTPs:

- **Phone**: +15555555555 → **OTP**: 123456
- **Phone**: +15555555556 → **OTP**: 123456
- **Phone**: +15555555557 → **OTP**: 123456

### **Testing Flow**
1. Register with a test phone number
2. Use the Firebase Phone Auth UI
3. Enter the fixed OTP (123456)
4. Phone will be verified without SMS costs

## 🔒 **Security Notes**

### **Production Setup**
- Use real phone numbers in production
- Enable reCAPTCHA protection
- Set up proper Firebase security rules
- Use HTTPS in production

### **Rate Limiting**
- Firebase has built-in rate limiting
- Monitor usage in Firebase Console
- Set up alerts for unusual activity

## 🚀 **Deployment Checklist**

- [ ] Firebase project created
- [ ] Phone Authentication enabled
- [ ] Service account key downloaded
- [ ] Environment variables configured
- [ ] Test phone numbers added
- [ ] reCAPTCHA configured
- [ ] Security rules set up
- [ ] HTTPS enabled (production)

## 📱 **Mobile Testing**

For mobile testing, you can use:
- **Android Emulator**: Use test phone numbers
- **iOS Simulator**: Use test phone numbers
- **Real Device**: Use real phone numbers (will incur SMS costs)

## 🔍 **Troubleshooting**

### **Common Issues**
1. **"reCAPTCHA not set up"**: Check Firebase config
2. **"Invalid phone number"**: Use proper format (+1234567890)
3. **"OTP expired"**: Request new OTP
4. **"Token verification failed"**: Check service account key

### **Debug Mode**
Enable debug logging in Firebase Console:
- Go to Project Settings → General
- Enable "Debug mode" for development 