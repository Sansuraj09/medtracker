#!/usr/bin/env python3
"""
Database initialization script for MedTracker
This script creates the MySQL database and all tables
"""
import os
import sys
from dotenv import load_dotenv
import mysql.connector

load_dotenv()

# MySQL connection parameters
MYSQL_USER = os.environ.get("MYSQL_USER", "root")
MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "")
MYSQL_HOST = os.environ.get("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.environ.get("MYSQL_PORT", "3306"))
MYSQL_DB = os.environ.get("MYSQL_DB", "medtracker")

def create_database():
    """Create MySQL database"""
    try:
        # Connect to MySQL without selecting a database
        print(f"Connecting to MySQL: {MYSQL_USER}@{MYSQL_HOST}:{MYSQL_PORT}")
        connection = mysql.connector.connect(
            host=MYSQL_HOST,
            port=MYSQL_PORT,
            user=MYSQL_USER,
            password=MYSQL_PASSWORD
        )
        
        cursor = connection.cursor()
        
        # Create database if it doesn't exist
        sql = f"CREATE DATABASE IF NOT EXISTS {MYSQL_DB} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"
        cursor.execute(sql)
        print(f"✓ Database '{MYSQL_DB}' created or already exists")
        
        connection.commit()
        cursor.close()
        connection.close()
        
        return True
    except Exception as e:
        print(f"✗ Error creating database: {e}")
        return False


def create_tables():
    """Create all tables using Flask-SQLAlchemy"""
    try:
        from app import app, db
        
        with app.app_context():
            db.create_all()
            print("✓ All tables created successfully")
            
            # List tables
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"\nTables in database '{MYSQL_DB}':")
            for table in tables:
                print(f"  - {table}")
            
        return True
    except Exception as e:
        print(f"✗ Error creating tables: {e}")
        return False


def main():
    print("=" * 50)
    print("MedTracker Database Initialization")
    print("=" * 50)
    print(f"\nConfiguration:")
    print(f"  Host: {MYSQL_HOST}")
    print(f"  Port: {MYSQL_PORT}")
    print(f"  User: {MYSQL_USER}")
    print(f"  Database: {MYSQL_DB}\n")
    
    # Step 1: Create database
    if not create_database():
        sys.exit(1)
    
    # Step 2: Create tables
    if not create_tables():
        sys.exit(1)
    
    print("\n" + "=" * 50)
    print("✓ Database initialization complete!")
    print("=" * 50)


if __name__ == "__main__":
    main()
