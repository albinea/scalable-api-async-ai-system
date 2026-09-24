import sqlite3


connection = sqlite3.connect("business.db")

cursor = connection.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS customers (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    city TEXT,
    plan TEXT
)
""")


customers = [
    (1, "Anil", "anil@example.com", "Kochi", "Premium"),
    (2, "John", "john@example.com", "Bangalore", "Basic"),
    (3, "Mary", "mary@example.com", "Chennai", "Premium"),
    (4, "David", "david@example.com", "Kochi", "Enterprise"),
]


cursor.executemany(
    """
    INSERT OR REPLACE INTO customers
    VALUES (?, ?, ?, ?, ?)
    """,
    customers
)


connection.commit()
connection.close()

print("Database created.")