"""Initialize PostgreSQL database tables"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(project_root))

from backend.models.database import init_db

if __name__ == "__main__":
    print("Initializing database tables...")
    init_db()
    print("Database tables created successfully!")

