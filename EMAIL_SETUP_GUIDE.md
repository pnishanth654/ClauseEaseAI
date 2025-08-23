# Email Setup Guide for ClauseEase AI

## Why Emails Are Not Working

The application is currently not sending emails because:

1. **Missing .env file** - No environment configuration file exists
2. **Default placeholder values** - Using "your-email@gmail.com" and "your-app-password"
3. **Gmail App Password required** - Regular Gmail password won't work

## How to Fix Email Issues

### Step 1: Create .env File

Create a `.env` file in the root directory (`ClauseEaseAI/`) with the following content:

```env
# Database Configuration
DATABASE_URL=postgresql://your-username:your-password@your-host:5432/your-database

# Flask Configuration
FLASK_SECRET_KEY=your-secret-key-here-change-in-production
FLASK_ENV=development

# Email Configuration (Gmail)
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-actual-email@gmail.com
MAIL_PASSWORD=your-gmail-app-password
MAIL_DEFAULT_SENDER=your-actual-email@gmail.com

# OTP Configuration
OTP_EXPIRY_MINUTES=10
```

### Step 2: Get Gmail App Password

1. **Enable 2-Factor Authentication** on your Gmail account
2. **Generate App Password**:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Select "Mail" and "Other (Custom name)"
   - Copy the generated 16-character password
3. **Use the App Password** in your .env file (not your regular Gmail password)

### Step 3: Test Email Configuration

1. **Restart the application** after creating the .env file
2. **Check terminal output** for email configuration warnings
3. **Try registering a new user** to test OTP email delivery

## Current Status

✅ **OTP Generation**: Working (shows in terminal)
✅ **OTP Verification**: Working  
✅ **OTP Expiry**: 10 minutes (consistent everywhere)
❌ **Email Delivery**: Not working (missing configuration)

## Troubleshooting

### If emails still don't work:

1. **Check .env file location** - Must be in root directory
2. **Verify Gmail credentials** - Use App Password, not regular password
3. **Check Gmail security** - Less secure apps access is disabled by Google
4. **Review terminal output** - Look for specific error messages

### Alternative: Use Terminal OTP

Until email is configured, OTP codes are displayed in the terminal:
- Look for `🚨 OTP GENERATED 🚨` messages
- Use the displayed code for verification
- This is a fallback for development/testing

## Security Notes

- Never commit .env file to version control
- Use strong, unique App Passwords
- Regularly rotate App Passwords
- Consider using environment variables in production

## Next Steps

1. Create the .env file with your Gmail credentials
2. Restart the application
3. Test registration and OTP delivery
4. Verify emails are being sent successfully 