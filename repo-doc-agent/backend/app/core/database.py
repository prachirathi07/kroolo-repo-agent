from supabase import create_client, Client
from app.core.config import settings
from app.core.logger import logger

# Initialize Supabase client
url: str = settings.SUPABASE_URL
key: str = settings.SUPABASE_KEY

try:
    if not url or not key:
        logger.warning("Supabase credentials not found. Database features will fail.")
        supabase: Client = None
    else:
        supabase: Client = create_client(url, key)
except Exception as e:
    logger.error(f"Failed to initialize Supabase client: {str(e)}")
    supabase = None

def get_db():
    """
    Dependency to get Supabase client.
    Returns the global supabase client instance.
    """
    return supabase

def init_db():
    """
    Placeholder for database initialization.
    With Supabase, tables are managed via the dashboard of SQL editor.
    """
    pass

