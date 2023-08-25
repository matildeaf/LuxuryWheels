import sqlite3
conn = sqlite3.connect('car_rental.db')
cursor = conn.cursor()

cursor.execute('INSERT INTO Categories (name, price) VALUES ("Economic", 50)')

cursor.execute('INSERT INTO Categories (name, price) VALUES ("Silver", 250)')
cursor.execute('INSERT INTO Categories (name, price) VALUES ("Gold", 600)')
cursor.execute('INSERT INTO Clients (first_name, last_name, email, phone_number, membership_level) VALUES ("Laura", "Sousa", "lsousa@gmail.com", 123456789, 2)')
cursor.execute('INSERT INTO Clients (first_name, last_name, email, phone_number, membership_level) VALUES ("Francisco", "Xavier", "franciscoxavier@sapo.pt", 987654321,3)')
cursor.execute('INSERT INTO Clients (first_name, last_name, email, phone_number, membership_level) VALUES ("Bruno", "Mars", "bmars@hotmail.com", 321456987, 3)')
cursor.execute('INSERT INTO Clients (first_name, last_name, email, phone_number, membership_level) VALUES ("Metilf", "Figs", "mfigs@hotmail.com", 452136897, 2)')
cursor.execute('INSERT INTO Clients (first_name, last_name, email, phone_number, membership_level) VALUES ("Vitor", "Silva", "vsilva@gmail.com", 852147639, 1)')
cursor.execute('INSERT INTO Clients (first_name, last_name, email, phone_number, membership_level) VALUES ("Maria", "Teixeira"," mariateixeira@gmail.com", 951423876, 1)')

cursor.execute('INSERT INTO Vehicles (type, model, registration, year, fuel_type, price_per_day, category_id) VALUES ("compact", "Fiat 500", "51FX20", 2019, "Gasoline", 41, 1)')
cursor.execute('INSERT INTO Vehicles (type, model, registration, year, fuel_type, price_per_day, category_id) VALUES ("compact", "Renault Twingo", "30RN16", 2021, "Gasoline", 35, 1)')
cursor.execute('INSERT INTO Vehicles (type, model, registration, year, fuel_type, price_per_day, category_id) VALUES ("city", "Peujeot 308", "57PJ80", 2022, "Diesel", 63, 1)')
cursor.execute('INSERT INTO Vehicles (type, model, registration, year, fuel_type, price_per_day, category_id) VALUES ("city", "Opel Corsa", "OP4723", 2023, "Diesel", 75, 1)')
cursor.execute('INSERT INTO Vehicles (type, model, registration, year, fuel_type, price_per_day, category_id) VALUES ("mid", "Citroen C4 Cactus", "CX2019", 2019, "Gasoline", 81, 1)')
cursor.execute('INSERT INTO Vehicles (type, model, registration, year, fuel_type, price_per_day, category_id) VALUES ("mid"," Mitsubishi ASX Invite", "17MX40", 2019, "Gasoline", 95, 2)')
cursor.execute('INSERT INTO Vehicles (type, model, registration, year, fuel_type, price_per_day, category_id) VALUES ("mid","Opel Crossland","25OC32", 2019, "Diesel", 102, 2)')
cursor.execute('INSERT INTO Vehicles (type, model, registration, year, fuel_type, price_per_day, category_id) VALUES ("executive","BMW S1","45BM62", 2020, "Diesel", 112, 2)')
cursor.execute('INSERT INTO Vehicles (type, model, registration, year, fuel_type, price_per_day, category_id) VALUES ("executive","BMW S2 Grand Coupe","MB1486", 2021, "Gasoline", 120, 2)')
cursor.execute('INSERT INTO Vehicles (type, model, registration, year, fuel_type, price_per_day, category_id) VALUES ("executive","Mercedes Classe C", "98MC43", 2019, "Gasoline", 125, 2)')
cursor.execute('INSERT INTO Vehicles (type, model, registration, year, fuel_type, price_per_day, category_id) VALUES ("lux","BMW S8 Cabrio", "67BM26", 2021, "Electric", 145, 3)')
cursor.execute('INSERT INTO Vehicles (type, model, registration, year, fuel_type, price_per_day, category_id) VALUES ("lux","Lexus LC500 Cabrio", "23LX41", 2020, "Electric", 150, 3)')
cursor.execute('INSERT INTO Vehicles (type, model, registration, year, fuel_type, price_per_day, category_id) VALUES ("lux" ,"Porsche Taycon", "71PS40", 2022, "Diesel", 200, 3)')
cursor.execute('INSERT INTO Vehicles (type, model, registration, year, fuel_type, price_per_day, category_id) VALUES ("lux","Tesla M3", "TS4025", 2022, "Electric", 190, 3)')
cursor.execute('INSERT INTO Vehicles (type, model, registration, year, fuel_type, price_per_day, category_id) VALUES ("lux","Audi A6", "34AD92", 2020, "Diessel", 185, 3)')


conn.commit()
conn.close()