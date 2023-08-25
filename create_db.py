import sqlite3

conn = sqlite3.connect('car_rental.db')
cursor = conn.cursor()
cursor.execute('DROP TABLE IF EXISTS Vehicles')
#creating vehicles table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Vehicles (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        model TEXT,
        registration TEXT,
        year INTEGER,
        fuel_type TEXT,
        price_per_day REAL,
        category_id INTEGER,
        FOREIGN KEY (category_id) REFERENCES Categories (id)
    )
''')
#creating clients table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        email TEXT,
        phone_number TEXT,
        membership_level INTEGER,
        FOREIGN KEY (membership_level) REFERENCES Categories (id)
    )
''')

#creating Categories table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS Categories (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        price REAL
    )
''')
conn.commit()
conn.close()

