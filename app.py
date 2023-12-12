import os
from datetime import datetime, timedelta, time
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import re
import json
from json import JSONEncoder
import threading
import time
import matplotlib.pyplot as plt

app = Flask(__name__)
app.config['SECRET_KEY'] = 'lalalalala'


class User:
    def __init__(self, id, email, password_hash ):
        self.id = id
        self.email = email
        self.password_hash = password_hash

class UserEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__

# Defining User Roles- User and Admin
ROLES = {
    'user': ['dashboard', 'bookings', 'payment'],
    'admin': ['dashboard', 'bookings', 'payment', 'manage_car', 'finances'],
}
def role_required(required_roles):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            user_role = get_user_role()
            print('user_role:', user_role)
            if user_role in required_roles:
                return func(*args, **kwargs)
            else:
                return "Permission Denied"

        return wrapper

    return decorator

def get_user_role():
    if 'user' in session:
        user_id = session.get('id')
        print("User ID from Session:", user_id)
        conn = sqlite3.connect('car_rental.db')
        cursor = conn.cursor()
        try:
            cursor.execute('SELECT user_role FROM Clients WHERE id = ?', (user_id,))
            user_role = cursor.fetchone()
        except sqlite3.Error as e:
            print("Database error:", e)

        print("User Role from DB:", user_role)
        conn.commit()
        conn.close()

        if user_role:
            return user_role[0]
        else:
            return 'user'
    return 'guest'

# Home Route- index HTML page
@app.route('/')
def home():
    # Connecting to DB
    conn = sqlite3.connect('car_rental.db')
    print("Database connected...")
    cursor = conn.cursor()
    # Getting data from Vehicles table
    cursor.execute('SELECT * FROM Vehicles')
    vehicles = cursor.fetchall()
    print("Records selected...")
    conn.close()
    print("Done!")
    return render_template("index.html", vehicles=vehicles)

# Login Route
@app.route("/login", methods=["GET", "POST"])
def login():
    msg = ''
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        email = request.form['email']
        password = request.form['password']

        conn = sqlite3.connect('car_rental.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Clients WHERE email = ? AND password = ?', (email, password))
        account = cursor.fetchone()
        conn.close()

        if account:
            session['loggedin'] = True
            session['id'] = account[0]
            session['email'] = account[3]
            session['user_role'] = account[7]
            msg = 'Logged in successfully!'
            user = User(id=account[0], email=account[3], password_hash=account[6])
            user_json = json.dumps(user, indent=4, cls=UserEncoder)
            #print(user_json)
            session['user'] = user_json
            return redirect(url_for('dashboard'))
        else:
            msg = 'Incorrect email/password!'


    return render_template('login.html', msg='')

# Logout Route
@app.route('/logout')
def logout():
    session.pop('loggedin', None)
    session.pop('id', None)
    session.pop('email', None)
    return redirect(url_for('login'))

# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():

    msg = 'REGISTER PAGE'
    if request.method == 'POST' and 'email' in request.form and 'password' in request.form:
        password = request.form['password']
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        phone_number = request.form['phone_number']
        subscription = request.form['membership_level']

        conn = sqlite3.connect('car_rental.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Clients WHERE email = ?', (email,))
        account = cursor.fetchone()

        # Condition for valid email
        def is_valid_email(email):
            pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            if re.match(pattern, email):
                return True
            else:
                return False
        if account:
            flash('Email already exists.', category='error')
        # Conditions for valididation of email, First and Last name, phone number and password
        elif not is_valid_email(email):
            flash('Email form is incorrect. Must be "name@example.com". ', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif len(last_name) < 2:
            flash('Last name must be greater than 1 character.', category='error')
        elif len(phone_number) < 9:
            flash('Phone number incorrect. Enter 9 digits.', category='error')
        elif len(password) < 7:
            flash('Password must be at least 7 characters.', category='error')
        elif not password or not email or not first_name or not last_name or not phone_number:
           flash('Please fill out the form!', category='error')
        else:
            cursor.execute('INSERT INTO Clients (email, password, first_name, last_name, phone_number, membership_level) VALUES (?, ?, ?, ?, ?, ?)', (email, password, first_name, last_name, phone_number, subscription))
            conn.commit()
            conn.close()
            #flash('Account created!', category='success')
            return redirect(url_for('login'))

    elif request.method == 'POST':
        flash('Please fill out the form!', category='error')
    return render_template('register.html', msg=msg)

# Dashboard Route - Page after Login
@app.route('/dashboard', methods=['GET','POST'])
@role_required(['user', 'admin'])
def dashboard():
    user_id = session.get('id')
    if user_id:
        conn = sqlite3.connect('car_rental.db')
        cursor = conn.cursor()

        # Get user's first and last name
        cursor.execute('SELECT * FROM Clients WHERE id = ?', (user_id,))
        client = cursor.fetchall()
        print("client:", client)

        # Get user's category_id from Clients table
        cursor.execute('SELECT membership_level FROM Clients WHERE id = ?', (user_id,))
        user_category_id = cursor.fetchone()[0]
        print("user_category_id: ", user_category_id)

        # Get user's category name
        cursor.execute('SELECT name FROM Categories WHERE id= ?', (user_category_id,))
        user_subscription = cursor.fetchone()
        print("user_subscription:", user_subscription)

        # Get vehicles based on user's category_id
        cursor.execute('SELECT * FROM Vehicles WHERE category_id = ?', (user_category_id,))
        cars = cursor.fetchall()
        print("cars", cars)

        # Get user's bookings along with the booked vehicle information
        cursor.execute('''
        SELECT Bookings.*, Vehicles.* FROM Bookings
        JOIN Vehicles ON Bookings.Vehicle_id = Vehicles.id
        WHERE Bookings.Client_id = ?
        ''', (user_id,))
        user_booking = cursor.fetchall()
        print('user_booking', user_booking)

        # Get user_role from the session
        user_role = session.get('user_role')

        conn.commit()
        conn.close()
        return render_template('dashboard.html', user=user_id, cars=cars, client=client, user_subscription=user_subscription, user_booking=user_booking, user_role=user_role)
    else:
        return redirect(url_for('login'))

# Booking Route
@app.route('/booking <int:vehicle_id>', methods=['GET', 'POST'])
@role_required(['user', 'admin'])
def booking(vehicle_id):
    user_id = session.get('id')
    if not user_id:
        return redirect(url_for('login'))

    conn = sqlite3.connect('car_rental.db')
    cursor = conn.cursor()

    # Get vehicle's info based on the selected vehicle_id
    cursor.execute('SELECT * FROM Vehicles WHERE id = ?', (vehicle_id,))
    selected_vehicle = cursor.fetchone()
    print("selected_vehicle", selected_vehicle)

    if not selected_vehicle:
        conn.close()
        return redirect(url_for('dashboard'))

    # Store selected vehicle in the session
    session['booked_vehicle'] = selected_vehicle

    conn.close()
    return render_template('bookings.html', vehicle=selected_vehicle)


@app.route('/submit_booking', methods=['POST'])
@role_required(['user', 'admin'])
def submit_booking():
    print("Submit Booking route accessed.")
    if 'user' in session:
        user = session['user']
        user_id = session.get('id')

        selected_vehicle = session.get('booked_vehicle')
        vehicle_id = selected_vehicle[0]
        start_date = request.form['start_date']
        end_date = request.form['end_date']

        print("User_ID:", user_id)
        print("Vehicle:", selected_vehicle)
        print("Start_Date:", start_date)
        print("End_Date:", end_date)

        # Format date strings in 'YYYY-MM-DD' format
        formatted_start_date = start_date
        formatted_end_date = end_date

        # Check vehicle's availability
        is_available = check_availability(vehicle_id, formatted_start_date, formatted_end_date)
        print("is_available", is_available)

        if not is_available:
            # Vehicle is unavailable
            availability = False
            return render_template('unavailable.html', availability=availability)
        else:
            availability = True

        # Update the availability on DB
        update_vehicle_availability(vehicle_id, availability)

        # Calculate total price based on the selected dates and vehicle price_per_day
        total_price = calculate_total_price(selected_vehicle[6], start_date, end_date)


        # Store booking info and total price in session
        session['booking'] = {
            'user_id': user_id,
            'vehicle_id': vehicle_id,
            'start_date': formatted_start_date,
            'end_date': formatted_end_date,
            'total_price': total_price
        }
        return redirect(url_for('payment'))
    else:
        return redirect(url_for('login'))
def check_availability(vehicle_id, formatted_start_date, formatted_end_date):
    try:
        conn = sqlite3.connect('car_rental.db')
        cursor = conn.cursor()
        # Query to check if there are overlapping bookings
        query = '''
            SELECT COUNT(*) FROM Bookings
            WHERE vehicle_id = ? 
            AND (start_date <= ? AND end_date >= ?)
            OR (start_date <= ? AND end_date >= ?)
            OR (? <= start_date AND ? >= end_date)
        '''
        cursor.execute(query, (vehicle_id, formatted_start_date,  formatted_end_date, formatted_start_date,  formatted_end_date, formatted_start_date,  formatted_end_date))
        count = cursor.fetchone()[0]

        # If count > 0, there are overlapping bookings, indicating unavailability
        return count == 0  # Vehicle is available if count is 0

    except sqlite3.Error as e:
        print("Database error:", e)
        return False  # Assume availability status as False in case of an error

    finally:
        conn.close()

def update_vehicle_availability(vehicle_id, availability):
    try:
        conn = sqlite3.connect('car_rental.db')
        cursor = conn.cursor()
        # Update the availability status in the Vehicles table
        update_query = "UPDATE Vehicles SET availability = ? WHERE id = ?"
        cursor.execute(update_query, (availability, vehicle_id))
        conn.commit()
    except sqlite3.Error as e:
        print("Database error:", e)
    finally:
        conn.close()

# Function to calculate the number of days between start_date and end_date and multiply by the price_per_day
def calculate_total_price(price_per_day, start_date, end_date):

    delta = datetime.strptime(end_date, '%Y-%m-%d') - datetime.strptime(start_date, '%Y-%m-%d')
    num_days = delta.days + 1
    total_price = price_per_day * num_days

    return total_price


@app.route('/payment', methods=['GET','POST'])
@role_required(['user', 'admin'])
def payment():
    if 'booking' in session:
        booking = session['booking']
        vehicle = get_vehicle_by_id(booking['vehicle_id'])
        return render_template('payment.html', booking=booking, vehicle=vehicle)
    else:
        return redirect(url_for('dashboard'))

def get_vehicle_by_id(vehicle_id):
    conn = sqlite3.connect('car_rental.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM Vehicles WHERE id = ?', (vehicle_id,))
    vehicle = cursor.fetchone()
    conn.close()
    return vehicle
#

@app.route('/complete_payment', methods=['POST'])
@role_required(['user', 'admin'])
def complete_payment():
    if 'booking' in session:
        booking = session['booking']

        user_id = booking['user_id']
        vehicle_id = booking['vehicle_id']
        start_date = booking['start_date']
        end_date = booking['end_date']
        total_price = booking['total_price']

        # Payement info
        card_number = request.form['card_number']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        cvc = request.form['cvc']

        # Check if card_number is valid
        if len(card_number) != 16 :
            return "Card number not valid, must be 16 digits long"
        # Check if first_name or last_name not null
        if not first_name or not last_name:
            return "First name and Last name are required"
        # Check if cvc is valid
        if len(cvc) !=3:
            return "CVC not valid, must be 3 digits long"

        # Insert booking into the database
        conn = sqlite3.connect('car_rental.db')
        cursor = conn.cursor()
        try:
            cursor.execute('INSERT INTO Bookings (Client_id, Vehicle_id, start_date, end_date, price) VALUES (?, ?, ?, ?, ?)', (user_id, vehicle_id, start_date, end_date, total_price))
            conn.commit()
            print("Booking insert into DB")
        except sqlite3.Error as e:
            print("Error inserting booking:", e)
            conn.rollback()
        finally:
            conn.close()
    session.pop('booking', None)

    # Store total_price in Finance table
    conn = sqlite3.connect('car_rental.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO Finances (income, date) VALUES (?, ?)', (total_price,start_date, ))
    conn.commit()
    conn.close()

    return redirect(url_for('dashboard'))

# Threads for checking the need of vehicle maintenance, legal maintenance and vehicles stock

# Maintenance_alert thread
maintenance_alerts = []

# Define function for checking maintenance alerts
def check_maintenance_alerts():
    while True:
        # Calculate today's date
        current_date = datetime.now()

        # Query the database for vehicles requiring maintenance
        conn = sqlite3.connect('car_rental.db')
        cursor = conn.cursor()
        query = '''
        SELECT id, last_maintenance, model
        FROM Vehicles
        '''
        cursor.execute(query)
        vehicles_needing_maintenance = cursor.fetchall()


        # Iterate through the vehicles and update the 'needs_maintenance' field
        for vehicle in vehicles_needing_maintenance:
            vehicle_id= vehicle[0]
            last_maintenance_date = datetime.strptime(vehicle[1], '%d-%m-%Y')
            six_months_from_now = timedelta(weeks=26)
            next_maintenance_date = last_maintenance_date + six_months_from_now

            if current_date >= next_maintenance_date:
                needs_maintenance = True
            else:
                needs_maintenance = False


            # Update the 'needs_maintenance' field in the database
            update_query = "UPDATE Vehicles SET needs_maintenance = ? WHERE id = ?"
            cursor.execute(update_query, (needs_maintenance, vehicle_id))

            # Add the alerts to the list
            if needs_maintenance:
                alert_message = f"Vehicle {vehicle[2]} requires maintenance soon."
                maintenance_alerts.append(alert_message)

        conn.commit()
        conn.close()
        time.sleep(24 * 60 * 60)

# Create and start the maintenance_thread
maintenance_thread = threading.Thread(target=check_maintenance_alerts)
maintenance_thread.daemon = True
maintenance_thread.start()


# Legal alert thread
legal_alerts = []

def check_legal_alerts():
    conn = sqlite3.connect('car_rental.db')
    cursor = conn.cursor()

    while True:
        current_date = datetime.now()

        # Query the database for vehicles requiring legal
        cursor.execute('''SELECT id, last_legal, model, legal_maintenance_added FROM Vehicles''')
        vehicles_needing_legal = cursor.fetchall()

        for legal_vehicles in vehicles_needing_legal:
            legal_vehicles_id, last_legal_date, model, maintenance_added = legal_vehicles
            last_legal_date = datetime.strptime(last_legal_date, '%d-%m-%Y')
            one_year_from_now = timedelta(weeks=52)

            # Calculate next_legal_date outside the loop
            next_legal_date = last_legal_date + one_year_from_now

            if current_date >= next_legal_date and not maintenance_added:
                needs_legal = True
            else:
                needs_legal = False

            # Update the 'needs_legal' and 'legal_maintenance_added' fields in the database
            update_query = "UPDATE Vehicles SET needs_legal = ?, legal_maintenance_added = ? WHERE id = ?"
            cursor.execute(update_query, (needs_legal, True, legal_vehicles_id))

            if needs_legal:
                alert_message = f"Vehicle {model} needs to update legal soon."
                legal_alerts.append(alert_message)

                # Insert cost into Finances
                cursor.execute('INSERT INTO Finances (costs, date) VALUES (?, ?)', (250, next_legal_date))

        conn.commit()
        time.sleep(24 * 60 * 60)  # sleep for 1 day before checking again

    conn.close()

# Create and start the legal_thread
legal_thread = threading.Thread(target=check_legal_alerts)
legal_thread.daemon = True
legal_thread.start()

# Stock thread
stock_alerts = []
def check_stock():
    while True:
        conn = sqlite3.connect('car_rental.db')
        cursor = conn.cursor()

        # Calculate number of clients
        cursor.execute('SELECT COUNT(DISTINCT Client_id) FROM Bookings')
        num_clients = cursor.fetchone()[0]
        # Calculate number of vehicles
        availability_status = '1'
        cursor.execute('SELECT COUNT(*) FROM Vehicles WHERE availability = ?', (availability_status,))
        num_available_vehicles = cursor.fetchone()[0]

        minimum_stock = num_clients + 5

        if num_available_vehicles < minimum_stock:
            stock_alert_message = f"Stock Alert: Only {num_available_vehicles} vehicles available, purchase more!"
            stock_alerts.append(stock_alert_message)


        conn.commit()
        conn.close()
        time.sleep(24 * 60 * 60) # Sleep for 1 day before checking again

    # Create and start the stock_thread
stock_thread = threading.Thread(target=check_stock)
stock_thread.daemon = True
stock_thread.start()

# Manage Route (only admin)
@app.route('/manage_cars')
@role_required(['admin'])
def manage_cars():
    user_id = session.get('id')
    # Access the maintenance_alerts list
    alerts = maintenance_alerts
    legal = legal_alerts

    stock = stock_alerts
    conn = sqlite3.connect('car_rental.db')
    cursor = conn.cursor()
    # Get user's first and last name
    cursor.execute('SELECT * FROM Clients WHERE id = ?', (user_id,))
    client = cursor.fetchall()
    conn.close()
    return render_template('/manage_cars.html',  client=client, maintenance_alerts=alerts, legal=legal_alerts, stock=stock_alerts)

# Vehicles Route for admin users
@app.route('/vehicle')
@role_required(['admin'])
def vehicle():
    user_id = session.get('id')
    conn = sqlite3.connect('car_rental.db')
    cursor = conn.cursor()

    # Access to all vehicles and info
    cursor.execute('SELECT V.id, V.type, V.model, V.registration, V.year,V.fuel_type,V.price_per_day,(SELECT name FROM Categories WHERE id = V.category_id) AS category_name, V.seats, V.gear, V.availability FROM Vehicles V ')
    car_data = cursor.fetchall()
    print('car_data:', car_data)

    # Get user's first and last name
    cursor.execute('SELECT * FROM Clients WHERE id = ?', (user_id,))
    client = cursor.fetchall()

    # Get booking info
    cursor.execute('SELECT * FROM Bookings')
    bookings_data = cursor.fetchall()
    conn.close()
    return render_template('vehicle.html', car_data=car_data, client=client, bookings_data=bookings_data)

# Finances Route for Admin users
@app.route('/finances')
@role_required(['admin'])
def finances():
    user_id = session.get('id')
    conn = sqlite3.connect('car_rental.db')
    cursor = conn.cursor()
    # Get user's first and last name
    cursor.execute('SELECT * FROM Clients WHERE id = ?', (user_id,))
    client = cursor.fetchall()

    # Calculate and update total income
    cursor.execute('SELECT SUM(income) FROM Finances')
    total_income = cursor.fetchone()[0]
    print("total_income: ",total_income)
    cursor.execute('UPDATE Total SET income = ?', (total_income,))

    # Calculate and update total costs
    cursor.execute('SELECT SUM(costs) FROM Finances')
    total_costs = cursor.fetchone()[0]
    print("total_costs: ",total_costs)
    cursor.execute('UPDATE Total SET costs = ?', (total_costs,))

    # Calculate balance and insert into DB
    balance = total_income - total_costs
    print("balance", balance)
    cursor.execute('UPDATE Total SET balance = ?', (balance,))

    # Select data for the plots
    cursor.execute('SELECT date, income, costs FROM Finances')
    data = cursor.fetchall()
    conn.commit()
    conn.close()

    # Separate data into lists
    date, income, costs = zip(*data)

    # Handle null values by replacing them with 0
    income = [0 if x is None else x for x in income]
    costs = [0 if x is None else x for x in costs]

    # Calculate balance again after fetching the updated data
    balance = [inc - cst for inc, cst in zip(income, costs)]

    # Plot income
    plt.plot(date, income, label='Income', color='blue')
    plt.ylabel('Income')
    plt.legend()
    # Save the income graph as an image file
    image_path_income = os.path.join('static', 'graph_income.png')
    plt.savefig(image_path_income)
    # Clear the figure
    plt.figure()

    # Plot costs
    if any(costs):
        plt.plot(date, costs, label='Costs', color='orange')
        plt.ylabel('Costs')
        plt.legend()
        # Save the costs graph as an image file
        image_path_costs = os.path.join('static', 'graph_costs.png')
        plt.savefig(image_path_costs)
        # Clear the figure
        plt.figure()

    # Plot Balance
    if any(balance):
        plt.plot(date, balance, label='Balance', color='green')
        plt.xlabel('Time')
        plt.ylabel('Balance')
        plt.legend()
        # Save the balance graph as an image file
        image_path_balance = os.path.join('static', 'graph_balance.png')
        plt.savefig(image_path_balance)

    plt.suptitle('Transaction History')
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    plt.clf()
    return render_template('finances.html', client=client, image_path_income=image_path_income, image_path_costs=image_path_costs, image_path_balance=image_path_balance)

# Clients Route for Admin users
@app.route('/clients')
@role_required(['admin'])
def clients():
    user_id = session.get('id')
    conn = sqlite3.connect('car_rental.db')
    cursor = conn.cursor()
    # Get user's first and last name
    cursor.execute('SELECT * FROM Clients WHERE id = ?', (user_id,))
    client = cursor.fetchall()

    # Get clients info
    cursor.execute('SELECT C.id, C.first_name, C.last_name, C.email, C.phone_number, (SELECT name FROM Categories WHERE id = C.membership_level) AS membership FROM Clients C')
    client_data= cursor.fetchall()

    conn.close()
    return render_template('clients.html', client=client, client_data=client_data)


if __name__ == '__main__':
    app.run(debug=True)
