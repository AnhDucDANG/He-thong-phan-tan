class Config:
    """Configuration settings for the application."""
    
    DEBUG = True  # Set to False in production
    DATABASE_URL = "sqlite:///app.db"  # Example database URL
    SECRET_KEY = "your_secret_key"  # Change this to a random secret key
    ALLOWED_HOSTS = ["localhost", "127.0.0.1"]  # Allowed hosts for the application

    @staticmethod
    def init_app(app):
        """Initialize the application with the configuration."""
        pass  # Additional initialization logic can be added here if needed