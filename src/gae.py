from db_setup import DATABASE_URL
import sqlite3

db_path = DATABASE_URL.replace("sqlite:///", "")
conn = sqlite3.connect(db_path)
cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='index'")
print(cursor.fetchall())