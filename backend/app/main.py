from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env first

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import deploy, webhook

app = FastAPI(title="InfraAgent", version="1.0.0")

# Add CORS middleware here
origins = [
    "http://localhost:3000",  # Local development
    "https://infraagent-frontend.onrender.com",  # Render frontend
    "https://*.onrender.com",  # Any Render subdomain
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,      # Allow frontend origin(s)
    allow_credentials=True,
    allow_methods=["*"],        # Allow all HTTP methods
    allow_headers=["*"],        # Allow all headers
)

# Include route modules
app.include_router(deploy.router, prefix="/deploy")
app.include_router(webhook.router, prefix="/webhook")

@app.get("/")
def root():
    return {"message": "Welcome to InfraAgent API", "version": "1.0.0"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "InfraAgent API"}

