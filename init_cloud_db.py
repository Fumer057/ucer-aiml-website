import os
import sys

# Add the project root to sys.path so we can import app
sys.path.append(os.getcwd())

try:
    from app.database import create_tables
    print("Connecting to database and creating tables...")
    create_tables()
    print("Tables created successfully in Supabase!")
except Exception as e:
    print(f"Error creating tables: {e}")
    sys.exit(1)
