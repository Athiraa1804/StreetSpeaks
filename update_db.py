import sqlite3

# Connect to database
conn = sqlite3.connect("streetspeaks.db")
cursor = conn.cursor()

# Add latitude and longitude columns if not exist
try:
    cursor.execute("ALTER TABLE complaints ADD COLUMN latitude REAL;")
    print("✅ Added column: latitude")
except:
    print("ℹ️ Column latitude already exists")

try:
    cursor.execute("ALTER TABLE complaints ADD COLUMN longitude REAL;")
    print("✅ Added column: longitude")
except:
    print("ℹ️ Column longitude already exists")

conn.commit()
print("✅ Database update complete!")
