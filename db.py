import sqlite3

def get_db_connection():
    return sqlite3.connect("mental_health.db")

def init_db():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        username TEXT UNIQUE,
        password TEXT,
        role TEXT
    )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS entries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        date TEXT,
        sleep INTEGER,
        workload INTEGER,
        energy INTEGER,
        mood INTEGER,
        journal TEXT,
        sentiment REAL,
        stress_score REAL,
        FOREIGN KEY(user_id) REFERENCES users(id)
    )
    ''')
    cur.execute('''
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        counselor_id INTEGER,
        date TEXT,
        time TEXT,
        status TEXT,
        notes TEXT DEFAULT '',
        FOREIGN KEY(user_id) REFERENCES users(id),
        FOREIGN KEY(counselor_id) REFERENCES users(id)
    )
    ''')

    try:
        cur.execute("ALTER TABLE appointments ADD COLUMN notes TEXT DEFAULT ''")
    except sqlite3.OperationalError as e:
        if "duplicate column" not in str(e):
            raise e

    conn.commit()
    conn.close()
    print("✅ Database initialized and schema updated.")

if __name__ == "__main__":
    init_db()