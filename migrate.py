import sqlite3

conn = sqlite3.connect('db/sessions.db')

try:
    conn.execute('ALTER TABLE sessions ADD COLUMN field TEXT DEFAULT "cloud"')
    print("✅ Column field added")
except Exception as e:
    print(f"ℹ️  {e}")

try:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS uploaded_courses (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            student    TEXT    NOT NULL,
            filename   TEXT    NOT NULL,
            field      TEXT    NOT NULL,
            filepath   TEXT    NOT NULL,
            size_mb    REAL    NOT NULL DEFAULT 0,
            created_at TEXT    NOT NULL
        );
    """)
    print("✅ Table uploaded_courses ready")
except Exception as e:
    print(f"ℹ️  {e}")

conn.commit()
conn.close()
print("✅ Migration complete")