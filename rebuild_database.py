# rebuild_database.py
import os
import shutil
from config import get_api_key
from enhanced_data_loader import get_or_create_vector_database_enhanced

def rebuild_database():
    """Rebuild the vector database with enhanced data processing."""
    print("🔄 Rebuilding vector database with enhanced processing...")
    
    DATA_FOLDER = "data"
    DB_FOLDER = "chroma_db"
    
    # Remove existing database
    if os.path.exists(DB_FOLDER):
        print("🗑️  Removing existing database...")
        shutil.rmtree(DB_FOLDER)
    
    # Get API key
    try:
        api_key = get_api_key()
        print("✅ API key loaded successfully.")
    except ValueError as e:
        print(f"❌ Error: {e}")
        return False
    
    # Rebuild with enhanced processing
    print("🔄 Creating new enhanced database...")
    vectordb = get_or_create_vector_database_enhanced(
        DATA_FOLDER, 
        DB_FOLDER, 
        api_key, 
        force_rebuild=True
    )
    
    if vectordb:
        print("✅ Enhanced database rebuilt successfully!")
        return True
    else:
        print("❌ Failed to rebuild database.")
        return False

if __name__ == "__main__":
    rebuild_database() 