import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """
    Configuration management for API keys, endpoints, and service settings.
    Loads credentials from environment variables.
    """
    
    # API Keys
    FAL_API_KEY = os.getenv('FAL_API_KEY', '')
    BRIA_API_KEY = os.getenv('BRIA_API_KEY', '')
    REPLICATE_API_KEY = os.getenv('REPLICATE_API_KEY', '')
    RUNWARE_API_KEY = os.getenv('RUNWARE_API_KEY', '')
    
    # API Endpoints
    FAL_FIBO_ENDPOINT = 'https://fal.run/fal-ai/bria-fibo'
    BRIA_API_ENDPOINT = 'https://engine.prod.bria-api.com/v1/image/generate'
    REPLICATE_API_ENDPOINT = 'https://api.replicate.com/v1/predictions'
    RUNWARE_API_ENDPOINT = 'https://api.runware.ai/v1'
    
    # Server Configuration
    HOST = '0.0.0.0'
    PORT = 5000
    DEBUG = os.getenv('DEBUG', 'True').lower() == 'true'
    
    # Generation Settings
    DEFAULT_WIDTH = 1024
    DEFAULT_HEIGHT = 1024
    MAX_PARALLEL_AGENTS = 4
    HDR_BIT_DEPTH = 16
    
    # Storage Paths
    OUTPUT_DIR = 'generated_designs'
    TEMP_DIR = 'temp'
    NUKE_SCRIPTS_DIR = 'nuke_scripts'
    
    @classmethod
    def validate(cls):
        """Validate required configuration parameters"""
        required = ['FAL_API_KEY', 'BRIA_API_KEY']
        missing = [key for key in required if not getattr(cls, key)]
        if missing:
            raise ValueError(f"Missing required configuration: {', '.join(missing)}")