# ClauseEase AI - Legal Document Simplifier

Transform complex legal documents into simple, easy-to-understand language with AI-powered simplification.

## 🚀 Features

- **Document Upload**: Support for PDF, DOCX, TXT, RTF, MD, ODT, PPT, PPTX
- **AI Simplification**: Complex legal jargon converted to plain English
- **Interactive Chat**: Ask questions about any section of your documents
- **User Management**: Secure authentication with OTP verification
- **File Storage**: User-specific directories for organized file management

## 📋 Prerequisites

- Python 3.8+
- PostgreSQL database (Neon recommended)
- SMTP server for email (Gmail recommended)

## 🛠️ Installation

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd ClauseEaseAI
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
Create a `.env` file in the root directory:
```env
# Database Configuration
DATABASE_URL=postgresql+psycopg2://username:password@host/database

# Flask Configuration
FLASK_SECRET_KEY=your-secret-key-here

# Email Configuration
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=true
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=your-email@gmail.com
```

### 5. Database Setup
The app will automatically create tables on first run. Make sure your PostgreSQL database is running and accessible.

## 🚀 Running the Application

### Option 1: Run from Root Directory (Recommended)
```bash
# From the root directory (ClauseEaseAI/)
python src/app.py
```

### Option 2: Run from src Directory
```bash
# From the src directory
cd src
python app.py
```

## 📁 File Storage Configuration

The application automatically detects your project structure and creates an `uploads` directory in the root folder. This ensures that:

- **Files are stored in the correct location** regardless of where you run the app
- **User directories are created automatically** for each registered user
- **File paths are consistent** across different operating systems

### Automatic Directory Detection
The app uses intelligent path detection to find your project root:
1. Looks for the `src` folder in current or parent directories
2. Creates `uploads` folder in the project root
3. Creates user-specific subdirectories as needed

### Example Directory Structure
```
ClauseEaseAI/
├── uploads/                    ← Files stored here
│   ├── user1@email.com/
│   │   ├── document1.pdf
│   │   └── document2.docx
│   └── user2@email.com/
│       └── contract.pdf
├── src/
│   ├── app.py
│   └── ...
├── templates/
├── static/
└── requirements.txt
```

## 🔧 Configuration Verification

### Check Upload Configuration
Visit `/public-upload-config` to verify your setup:
```bash
curl http://localhost:5000/public-upload-config
```

### Expected Output
```json
{
  "success": true,
  "project_root": "/path/to/ClauseEaseAI",
  "upload_folder": "/path/to/ClauseEaseAI/uploads",
  "upload_folder_exists": true,
  "current_working_directory": "/path/to/ClauseEaseAI",
  "src_folder_in_project_root": true
}
```

## 🧪 Testing

### 1. Start the Application
```bash
python src/app.py
```

### 2. Visit the Landing Page
Open `http://localhost:5000` in your browser

### 3. Check Upload Configuration
The landing page shows real-time upload directory status

### 4. Register/Login
- Create a new account or login
- Upload a document to test file storage

## 🔍 Troubleshooting

### Upload Directory Issues
If files aren't being stored correctly:

1. **Check the terminal output** when starting the app
2. **Verify the upload folder path** in the logs
3. **Use the migration tools** if you have existing files in wrong locations

### Migration Tools
If you have existing files in the wrong location:

1. **Login to the app**
2. **Use the migration panel** in the sidebar
3. **Click "Migrate Files"** to move files to correct location
4. **Click "Cleanup Old"** to remove old directories

### Common Issues

#### Issue: "Upload folder not found"
**Solution**: Make sure you're running the app from the correct directory

#### Issue: "Permission denied"
**Solution**: Check folder permissions in your project directory

#### Issue: "Database connection failed"
**Solution**: Verify your DATABASE_URL in the .env file

## 📱 Usage

### 1. **Landing Page** (`/`)
- Shows app information and upload configuration status
- Redirects to login page

### 2. **Login/Register** (`/login`, `/register`)
- User authentication with OTP verification
- Secure account creation

### 3. **Home Page** (`/home`)
- Document upload interface
- Drag & drop file support
- Chat interface for document interaction

### 4. **File Management**
- Automatic user directory creation
- Secure file storage
- File type validation
- Size limits (10MB max)

## 🔒 Security Features

- **OTP Verification**: Email-based verification for new accounts
- **User Isolation**: Each user can only access their own files
- **File Validation**: Type and size restrictions
- **CSRF Protection**: Built-in CSRF token validation
- **Rate Limiting**: Login attempt restrictions

## 🌐 API Endpoints

### Public Endpoints
- `GET /` - Landing page
- `GET /public-upload-config` - Upload configuration (no auth required)
- `GET /login` - Login page
- `GET /register` - Registration page

### Protected Endpoints
- `GET /home` - Home page (requires login)
- `POST /upload-document` - File upload
- `POST /chat-message` - Chat functionality
- `POST /update-chat-title` - Rename chat titles
- `GET /upload-config` - Detailed configuration (requires login)

## 🚀 Deployment

### Production Considerations
1. **Environment Variables**: Use proper production secrets
2. **Database**: Use production PostgreSQL instance
3. **File Storage**: Consider cloud storage for large deployments
4. **HTTPS**: Enable SSL/TLS in production
5. **Logging**: Configure proper logging levels

### Docker Support
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "src/app.py"]
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter any issues:

1. **Check the terminal logs** for detailed error messages
2. **Verify your configuration** using `/public-upload-config`
3. **Check the troubleshooting section** above
4. **Open an issue** with detailed error information

## 🔄 Updates

### Recent Changes
- ✅ **Fixed app launch flow** - Now goes to login page first
- ✅ **Improved upload directory detection** - Works from any directory
- ✅ **Added migration tools** - Move existing files to correct location
- ✅ **Enhanced error handling** - Better debugging information
- ✅ **Added landing page** - Professional introduction to the app

---

**Happy Document Simplifying! 🎉** 