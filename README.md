# 🚀 InfraAgent

AI-powered infrastructure deployment management system with a modern, user-friendly interface.

## ✨ Features

- **Smart Form Validation**: Ensures all required fields (GitHub repo URL, environment, deployment description) are provided
- **Modern UI**: Beautiful, responsive design with smooth animations and intuitive user experience
- **Environment Selection**: Visual environment picker with color-coded options (dev, qa, beta, prod)
- **Quick Templates**: Pre-built deployment description templates for common scenarios
- **Real-time Feedback**: Loading states, error handling, and success responses
- **Backend Validation**: Comprehensive server-side validation with helpful error messages

## 🏗️ Architecture

```
InfraAgent/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── models/         # Pydantic models
│   │   ├── routers/        # API endpoints
│   │   ├── services/       # Business logic
│   │   └── utils/          # Utility functions
│   └── requirements.txt
└── frontend/               # React frontend
    ├── src/
    │   ├── components/     # React components
    │   ├── api.js         # API configuration
    │   └── App.js         # Main app component
    └── package.json
```

## 🚀 Quick Start

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the FastAPI server:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the React development server:
   ```bash
   npm start
   ```

4. Open your browser and go to `http://localhost:3000`

## 📋 Usage

### Deployment Process

1. **Enter Deployment Description**: Describe what you want to deploy
   - Use the quick templates for common scenarios
   - Be specific about the service or application

2. **Provide GitHub Repository URL**: 
   - Must be a valid GitHub repository URL
   - Format: `https://github.com/username/repository`

3. **Select Environment**: Choose from:
   - 🟢 **Development** (dev) - For development work
   - 🟡 **QA/Testing** (qa) - For quality assurance
   - 🔵 **Beta/Staging** (beta) - For staging deployments
   - 🔴 **Production** (prod) - For production deployments

4. **Deploy**: Click the "🚀 Deploy Now" button to start the deployment

### Validation Features

The application validates:
- ✅ **Required Fields**: All fields must be filled
- ✅ **GitHub URL Format**: Must be a valid GitHub repository URL
- ✅ **Environment Selection**: Must be one of the supported environments
- ✅ **Backend Validation**: Server-side validation with detailed error messages

### Error Handling

- **Missing Fields**: Clear indication of which fields need to be completed
- **Invalid URLs**: Helpful error messages for malformed GitHub URLs
- **Server Errors**: Graceful handling of backend errors
- **Network Issues**: User-friendly network error messages

## 🎨 UI Features

- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Smooth Animations**: Loading spinners, hover effects, and transitions
- **Color-coded Environments**: Visual distinction between different environments
- **Modern Styling**: Clean, professional appearance with gradient backgrounds
- **Accessibility**: Proper labels, focus states, and keyboard navigation

## 🔧 API Endpoints

### POST /deploy
Deploy an application with the provided configuration.

**Request Body:**
```json
{
  "prompt": "Deploy the user authentication service to production",
  "repo_url": "https://github.com/username/repository",
  "environment": "prod"
}
```

**Response:**
```json
{
  "deployment_id": "deploy_123",
  "status": "success",
  "message": "Deployment initiated successfully"
}
```

## 🛠️ Development

### Adding New Environments

1. Update `backend/app/models/deployment.py`:
   ```python
   valid_envs = ['dev', 'qa', 'beta', 'prod', 'staging']
   ```

2. Update `frontend/src/components/pages/DeployForm.jsx`:
   ```javascript
   const environments = [
     { value: 'dev', label: 'Development', color: '#10B981' },
     { value: 'staging', label: 'Staging', color: '#8B5CF6' },
     // ... other environments
   ];
   ```

### Customizing Styles

Edit `frontend/src/components/pages/DeployForm.css` to customize:
- Colors and gradients
- Animations and transitions
- Layout and spacing
- Responsive breakpoints

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

---

**InfraAgent** - Making infrastructure deployment simple and intuitive! 🚀 