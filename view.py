import sqlite3

# Connect to database
conn = sqlite3.connect("streetspeaks.db")
cursor = conn.cursor()

# Query to get table info
cursor.execute("PRAGMA table_info(complaints)")
columns = cursor.fetchall()

print("Columns in complaints table:")
for col in columns:
    print(f"- {col[1]} ({col[2]})")  # col[1] = column name, col[2] = data type
