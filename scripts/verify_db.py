import sqlite3
import os
from pathlib import Path

# Determine DB path
db_path = os.getenv("BUSINESS_DB_PATH", "business_database.db")
print(f"Checking database at: {db_path}")

if not os.path.exists(db_path):
    print("Database file does not exist!")
    # Create it to check schema creation
    print("Creating new database...")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # List tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    print(f"Tables found: {tables}")
    
    required_tables = [
        "corporate_objectives",
        "department_tasks",
        "knowledge_articles",
        "executive_directives",
        "products",
        "vectors" # This might be in a separate vector_memory.db
    ]
    
    for table in required_tables:
        if table in tables:
            print(f"✅ Table '{table}' exists.")
        else:
            print(f"❌ Table '{table}' MISSING.")
            
    conn.close()
    
    # Check vector DB if separate
    vector_db_path = "vector_memory.db"
    if os.path.exists(vector_db_path):
        print(f"\nChecking vector database at: {vector_db_path}")
        v_conn = sqlite3.connect(vector_db_path)
        v_cursor = v_conn.cursor()
        v_cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        v_tables = [row[0] for row in v_cursor.fetchall()]
        print(f"Vector DB Tables: {v_tables}")
        if "vectors" in v_tables:
             print("✅ Table 'vectors' exists in vector_memory.db")
        else:
             print("❌ Table 'vectors' MISSING in vector_memory.db")
        v_conn.close()
    else:
        print(f"\n⚠️ Vector database file '{vector_db_path}' not found.")

except Exception as e:
    print(f"Error: {e}")
