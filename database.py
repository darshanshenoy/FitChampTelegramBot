import sqlite3

def init_db():
    conn = sqlite3.connect("health_data.db")
    c = conn.cursor()
    # Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (telegram_id INTEGER PRIMARY KEY, google_token TEXT)''')
    # Health data table
    c.execute('''CREATE TABLE IF NOT EXISTS health_data
                 (telegram_id INTEGER, date TEXT, steps INTEGER, calories REAL, distance REAL,
                  FOREIGN KEY(telegram_id) REFERENCES users(telegram_id))''')
    # Leaderboard table (optional, can be derived from health_data)
    c.execute('''CREATE TABLE IF NOT EXISTS leaderboard
                 (telegram_id INTEGER, total_steps INTEGER,
                  FOREIGN KEY(telegram_id) REFERENCES users(telegram_id))''')
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()