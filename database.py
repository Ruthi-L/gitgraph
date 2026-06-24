import sqlite3

DB_NAME = "github_network.db"

def init_db():
    """Initializes the database and clears old tracking schemas for testing."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Drop old tables during configuration to clear hardcoded 'FETCHED' states
    cursor.execute('DROP TABLE IF EXISTS relationships')
    cursor.execute('DROP TABLE IF EXISTS users')
    
    # Create Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL
        )
    ''')
    
    # Create Multidimensional Relationships table
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
    """Retrieves or inserts a user node and returns their system ID."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("INSERT OR IGNORE INTO users (username) VALUES (?)", (username,))
    conn.commit()
    
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    user_id = cursor.fetchone()[0]
    
    conn.close()
    return user_id

def record_relationship(follower, followed, relation_type):
    """Records distinct multi-metric developer interactions (FOLLOWS, STARRED, FORKED)."""
    get_user_id(follower)
    get_user_id(followed)
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT OR IGNORE INTO relationships (follower_name, followed_name, relation_type)
            VALUES (?, ?, ?)
        ''', (follower, followed, relation_type))
        conn.commit()
    except sqlite3.Error as e:
        print(f"Database error writing relationship: {e}")
    finally:
        conn.close()

def get_all_data():
    """Fetches full topology metrics for the NetworkX analytics pipeline."""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username FROM users")
    users = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("SELECT follower_name, followed_name, relation_type FROM relationships")
    relationships = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return users, relationships