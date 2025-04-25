import sqlite3

DB_PATH = 'game_site.db'

def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Create users table
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')

    conn.commit()
    cur.close()
    conn.close()
    print("Database initialized successfully!")

if __name__ == '__main__':
    initialize_database()
