
import sys
import os
from sqlalchemy import text, create_engine, inspect

# Setup path
sys.path.append(os.getcwd())
from app.core.config import get_settings

def check_schema():
    print("--- Verifying DB Schema ---")
    settings = get_settings()
    engine = create_engine(settings.database_url)
    
    inspector = inspect(engine)
    columns = inspector.get_columns("processing_jobs")
    
    found = False
    for col in columns:
        if col["name"] == "error_message":
            found = True
            print(f"Found column: {col['name']} ({col['type']})")
            
    if not found:
        print("column 'error_message' NOT FOUND in processing_jobs table!")
        print("Existing columns:", [c["name"] for c in columns])
    else:
        print("Schema check passed.")

if __name__ == "__main__":
    check_schema()
