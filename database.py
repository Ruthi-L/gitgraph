import sqlite3

DB_NAME = "github_network.db"

def init_db():
<<<<<<< HEAD
    """Initializes the database and creates the necessary tables safely."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
=======
    """Initializes the database and clears old tracking schemas for testing."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Drop old tables during configuration to clear hardcoded 'FETCHED' states
    cursor.execute('DROP TABLE IF EXISTS relationships')
    cursor.execute('DROP TABLE IF EXISTS users')
    
    # Create Users table
>>>>>>> 9378a66941f24135a0949128d2c9a2e95ef9e770
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL
        )
    ''')
    
<<<<<<< HEAD
=======
    # Create Multidimensional Relationships table
>>>>>>> 9378a66941f24135a0949128d2c9a2e95ef9e770
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
<<<<<<< HEAD
    """Retrieves or inserts a user and returns their database ID."""
=======
    """Retrieves or inserts a user node and returns their system ID."""
>>>>>>> 9378a66941f24135a0949128d2c9a2e95ef9e770
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("INSERT OR IGNORE INTO users (username) VALUES (?)", (username,))
    conn.commit()
    
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
<<<<<<< HEAD
    row = cursor.fetchone()
    user_id = row[0] if row else None
=======
    user_id = cursor.fetchone()[0]
>>>>>>> 9378a66941f24135a0949128d2c9a2e95ef9e770
    
    conn.close()
    return user_id

<<<<<<< HEAD
def record_relationship(follower, followed, relation_type="FETCHED"):
    """Records a directed relationship connection between two developers."""
=======
def record_relationship(follower, followed, relation_type):
    """Records distinct multi-metric developer interactions (FOLLOWS, STARRED, FORKED)."""
>>>>>>> 9378a66941f24135a0949128d2c9a2e95ef9e770
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
<<<<<<< HEAD
        print(f"Database error recording relationship: {e}")
=======
        print(f"Database error writing relationship: {e}")
>>>>>>> 9378a66941f24135a0949128d2c9a2e95ef9e770
    finally:
        conn.close()

def get_all_data():
<<<<<<< HEAD
    """Fetches all stored nodes and edges for network analysis processing."""
=======
    """Fetches full topology metrics for the NetworkX analytics pipeline."""
>>>>>>> 9378a66941f24135a0949128d2c9a2e95ef9e770
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT id, username FROM users")
    users = [dict(row) for row in cursor.fetchall()]
    
    cursor.execute("SELECT follower_name, followed_name, relation_type FROM relationships")
    relationships = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return users, relationships