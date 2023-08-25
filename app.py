
from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__) #app is the web server
@app.route('/')
def home():
    #conecting to DB

    conn = sqlite3.connect('car_rental.db')
    print("Database connected...")
    cursor = conn.cursor()
#Getting data from Vehicles table
    cursor.execute('SELECT * FROM Vehicles')
    vehicles = cursor.fetchall()
    print("records selected...")
    return render_template("index.html", vehicles=vehicles)

    conn.close()
    print("Done!")

if __name__ == '__main__':
    app.run(debug=True)
