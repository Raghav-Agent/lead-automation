import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    # API Keys
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    BRAVE_API_KEY = os.getenv("BRAVE_API_KEY")

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///leads.db")

    # Email
    SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", 587))
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")

    # Server
    SERVER_HOST = os.getenv("SERVER_HOST", "0.0.0.0")
    SERVER_PORT = int(os.getenv("SERVER_PORT", 8000))

    # Website Builder
    WEBSITE_OUTPUT_PATH = os.getenv("WEBSITE_OUTPUT_PATH", "./generated_sites")
    VITE_DIST_PATH = os.getenv("VITE_DIST_PATH", "../templates/vite/dist")  # path to built React app

    # AI Server (OpenClaw with OpenRouter)
    AI_SERVER_URL = os.getenv("AI_SERVER_URL", "http://localhost:9000")

settings = Settings()
