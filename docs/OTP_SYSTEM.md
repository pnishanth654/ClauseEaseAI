# 🔐 OTP Verification System for ClauseEase AI

## **📱 What We're Implementing:**
- **Email OTP**: Email verification with customizable expiry (Phone verification removed)

## **🚀 Features:**

### **Email OTP:**
- ✅ 6-digit verification codes
- ✅ Configurable expiry time (default: 10 minutes)
- ✅ Professional email templates
- ✅ Rate limiting protection
- ✅ Secure code generation

### **System Features:**
- ✅ Email-only verification (simplified)
- ✅ No phone verification complexity
- ✅ Faster registration process

## **⚙️ Configuration:**

### **Environment Variables:**
```env
# OTP Configuration
OTP_EXPIRY_MINUTES=10
SMS_SERVICE_PROVIDER=console  # or twilio, aws_sns

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

### **SMS Service Providers:**
- **`console`**: Development mode - logs OTP to console
- **`twilio`**: Twilio SMS service (TODO: implement)
- **`aws_sns`**: AWS SNS SMS service (TODO: implement)

## **🔍 How It Works:**

### **Registration Flow:**
1. User registers with email and/or phone
2. System generates 6-digit OTP
3. OTP sent via email (if email provided)
4. OTP sent via SMS (if phone provided)
5. User enters OTP on verification page
6. Account marked as verified

### **Verification Process:**
1. **Email Verification**: OTP sent via Flask-Mail
2. **Phone Verification**: OTP sent via configured SMS service
3. **Code Validation**: Server-side verification with expiry check
4. **Account Activation**: Mark email/phone as verified

## **🛡️ Security Features:**

- **Rate Limiting**: Built-in Flask-Limiter protection
- **Secure OTP Generation**: Cryptographically secure random codes
- **Expiry Protection**: Configurable timeout for OTP codes
- **Input Validation**: Server-side validation of all inputs
- **Session Management**: Secure user sessions with Flask-Login

## **📧 Email Templates:**

Professional email templates with:
- Clear verification code display
- Expiry time information
- Security warnings
- Branded messaging

## **📱 SMS Integration:**

### **Development Mode:**
- OTP codes logged to console
- No SMS costs during development
- Easy debugging and testing

### **Production Mode:**
- Integrate with Twilio, AWS SNS, or your preferred service
- Real SMS delivery to user phones
- Professional SMS templates

## **🔧 Customization:**

### **OTP Expiry:**
```python
# Set custom expiry time
OTP_EXPIRY_MINUTES=15  # 15 minutes instead of 10
```

### **SMS Provider:**
```python
# Switch to different SMS service
SMS_SERVICE_PROVIDER=twilio
```

### **Email Templates:**
Modify `src/otp_utils.py` to customize email content and styling.

## **🧪 Testing:**

### **Email OTP:**
1. Register with email address
2. Check email for verification code
3. Enter code on verification page
4. Verify account activation

### **Phone OTP (Development):**
1. Register with phone number
2. Check console logs for OTP code
3. Enter code on verification page
4. Verify account activation

## **📊 Monitoring:**

- **Console Logs**: All OTP activities logged
- **Error Tracking**: Failed OTP attempts logged
- **Rate Limiting**: Built-in abuse prevention
- **User Feedback**: Clear success/error messages

## **🚀 Production Deployment:**

### **Email Service:**
- Use production SMTP server (Gmail, SendGrid, etc.)
- Set up proper SPF/DKIM records
- Monitor delivery rates

### **SMS Service:**
- Choose reliable SMS provider (Twilio, AWS SNS, etc.)
- Set up webhook endpoints
- Monitor delivery success rates

### **Security:**
- Enable HTTPS in production
- Set strong Flask secret key
- Monitor for abuse attempts
- Regular security audits

## **✅ Success Indicators:**

- ✅ OTP codes generated successfully
- ✅ Emails sent without errors
- ✅ SMS codes logged (development) or sent (production)
- ✅ Verification completes successfully
- ✅ Users can login after verification
- ✅ Rate limiting prevents abuse

## **🔒 Best Practices:**

1. **Never log OTP codes in production**
2. **Use HTTPS for all communications**
3. **Implement proper rate limiting**
4. **Monitor for suspicious activity**
5. **Regular security updates**
6. **Backup verification data**

## **📞 Support:**

For issues with the OTP system:
1. Check console logs for errors
2. Verify environment variables
3. Test email/SMS delivery
4. Check rate limiting settings
5. Verify database connectivity 