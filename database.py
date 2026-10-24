import sqlite3
import os

DB_PATH = "github_network.db"

def get_db_connection():
    """Create a database connection to the SQLite database."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize database tables for users and relationships."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL
        )
    ''')
    
    # Relationships table (Follows, Starred, Forked)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS relationships (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            follower_name TEXT NOT NULL,
            followed_name TEXT NOT NULL,
            relation_type TEXT NOT NULL,
            UNIQUE(follower_name, followed_name, relation_type)
        )
    ''')
    
    conn.commit()
    conn.close()

def get_user_id(username):
    """Get user ID or insert user if not exists."""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    if row:
        user_id = row['id']
    else:
        cursor.execute("INSERT INTO users (username) VALUES (?)", (username,))
        conn.commit()
        user_id = cursor.lastrowid
    conn.close()
    return user_id

def record_relationship(follower, followed, relation_type):
    """Record a directed edge/relationship between two users."""
    get_user_id(follower)
    get_user_id(followed)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO relationships (follower_name, followed_name, relation_type)
            VALUES (?, ?, ?)
        ''', (follower, followed, relation_type))
        conn.commit()
    except Exception as e:
        print(f"Database error recording relationship: {e}")
    finally:
        conn.close()

def get_all_data():
    """Retrieve all users and relationships for graph construction and DSA."""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM users")
    users = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("SELECT * FROM relationships")
    relationships = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return users, relationships