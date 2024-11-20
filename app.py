from flask import Flask, render_template, request, jsonify, session, redirect, flash
import mysql.connector
import secrets
import requests
import discord
from discord.ext import commands
import asyncio
import threading

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# MapmyIndia API credentials
MAPMYINDIA_CLIENT_ID = '96dHZVzsAusZJekSJDqmuYlU_DYicddzUz1L1g1C2NzCqSoUIBsF0XtJNhOOKXc8JzyB83C5o2T8Nmi200M-4g=='  # Replace with your actual client ID
MAPMYINDIA_CLIENT_SECRET = 'lrFxI-iSEg9bmoxgPHLCD_GA7sVASTASqX8XadNRIPmQisopPOBZsFIQm-pnoblu2QGCe376PpDoO9rlXEHTOT7RHB7IjetB'  # Replace with your actual client secret

# Discord Bot credentials
TOKEN = 'MTI4NTU0NzgyMjEwNzg1Njg5Ng.GlDLrh.eLjUj9JdBFXNPrH_zK9AaHH8EdzC_FYuojpQio'  # Replace with your actual bot token

# Initialize the bot
intents = discord.Intents.default()
intents.members = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Function to generate a Bearer Token
def generate_bearer_token():
    url = "https://outpost.mapmyindia.com/api/security/oauth/token"
    payload = f'grant_type=client_credentials&client_id={MAPMYINDIA_CLIENT_ID}&client_secret={MAPMYINDIA_CLIENT_SECRET}'
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    
    response = requests.post(url, headers=headers, data=payload)
    
    if response.status_code == 200:
        access_token = response.json().get("access_token")
        session['mapmyindia_token'] = access_token
        return access_token
    else:
        return None
db=mysql.connector.connect(
            host="localhost",
            user="root",
            password="manasa@1125",
            database="ambulance_db"
)
async def send_notification(discord_username, message):
    print("in send notif")
    for guild in bot.guilds:
        for member in guild.members:
            if member.name == discord_username:
                try:
                    await member.send(message)
                    print(f'Message sent to ')
                except discord.Forbidden:
                    print(f"Cannot send a message to , user has DMs disabled.")
                return
    print(f'User {discord_username} not found.')

@app.route('/')
def home():
    return render_template('Home.html')

@app.route('/check_hospital', methods=['POST'])
def check_hospital():
    data = request.get_json()
    selected_eloc = data.get('selected_eloc')
    print(f"Received eLoc: {selected_eloc}")
    if not selected_eloc:
        return jsonify({'error': 'eLoc is required'}), 400

    cursor = db.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM hospitals WHERE hsptl_eloc = %s", (selected_eloc,))
        hospital = cursor.fetchone()
    except mysql.connector.Error as e:
        print(f"Database query error: {e}")
        return jsonify({'error': 'Database query failed'}), 500
    finally:
        cursor.close()

    if hospital:
        print(f"Hospital found: {hospital}")
        discord_username = hospital['discord_username']
        message ="An ambulance is on its way prepare accordingly."
        print(message)
        # Call the bot's method to send notification
        #bot.loop.create_task(send_notification(discord_username, message, tts=True))
        # Directly send the notification
        print("call send notif")
        #asyncio.run(send_notification(discord_username, message))
        bot.loop.create_task(send_notification(discord_username, message))
        print("after call send notif")
        
        return jsonify({"message": "Hospital found and notification sent.", "data": hospital}), 200
    else:
        print("Hospital not found")
        return jsonify({"message": "Hospital not found in the database."}), 404
    
    
    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        role = request.form.get('role')

        if not username or not email or not password or not role:
            flash("All fields are required.", "error")
            return redirect('/register')

        cursor = db.cursor()
        try:
            if role == 'ambulance_driver':
                cursor.execute(
                    "INSERT INTO users (username, email, password, role) VALUES (%s, %s, %s, %s)",
                    (username, email, password, role)
                )
            elif role == 'hospital':
                name = request.form.get('name')
                location = request.form.get('hsptl_location')
                latitude_str = request.form.get('hsptl_latitude')
                longitude_str = request.form.get('hsptl_longitude')
                hsptl_eloc = request.form.get('hsptl_eloc')
                beds_available = request.form.get('beds_available')
                doctors_available = bool(request.form.get('doctors_available', False))
                hsptl_duname = request.form.get('hsptl_duname')

                if not latitude_str or not longitude_str:
                    flash("Latitude and Longitude are required fields for hospitals.", "error")
                    return redirect('/register')
                
                try:
                    hslatitude = float(latitude_str)
                    hslongitude = float(longitude_str)
                except ValueError:
                    flash("Latitude and Longitude must be valid numbers.", "error")
                    return redirect('/register')

                cursor.execute(
                    "INSERT INTO hospitals (name, location, latitude, longitude, beds_available, doctors_available, discord_username, hsptl_eloc) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (name, location, hslatitude, hslongitude, beds_available, doctors_available, hsptl_duname, hsptl_eloc)
                )
                cursor.execute(
                    "INSERT INTO users (username, email, password, role, discord_username, location, latitude, longitude) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (username, email, password, role, hsptl_duname, location, hslatitude, hslongitude)
                )

            elif role == 'traffic_police':
                print("in tp")
                tname = request.form.get('signal_name')
                tlatitude_str = request.form.get('trlatitude')
                tlongitude_str = request.form.get('trlongitude')
                truname = request.form.get('truname')
                print(tname + " "+ tlatitude_str+" "+tlongitude_str+" "+truname)
                if not tlatitude_str or not tlongitude_str:
                    flash("Latitude and Longitude are required fields for traffic police.", "error")
                    return redirect('/register')

                try:
                    tplatitude = float(tlatitude_str)
                    tplongitude = float(tlongitude_str)
                except ValueError:
                    flash("Latitude and Longitude must be valid numbers.", "error")
                    return redirect('/register')
                print("inputs taken")
                cursor.execute("""
                INSERT INTO traffic_pnt_signals (signal_name, location, trdname) 
                VALUES (%s, ST_GeomFromText(CONCAT('POINT(', %s, ' ', %s, ')')), %s)
                """, (tname, tplongitude, tplatitude, truname))
                print("inserted into tp")
                cursor.execute(
                    "INSERT INTO users (username, email, password, role, discord_username, location, latitude, longitude) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)",
                    (username, email, password, role, truname, tname, tplatitude, tplongitude)
                )

            db.commit()
            flash("Registration successful!", "success")
            # Instead of rendering login.html, render discord.html
            return render_template('discord.html')  # Render discord.html after successful registration

        except mysql.connector.Error as err:
            db.rollback()
            flash(f"Database error: {err}", "error")
        finally:
            cursor.close()

        return redirect('/register')

    return render_template('register.html')

@app.route('/hospitals', methods=['GET'])
def hospitals_page():
    # Ensure user is logged in and has the role 'hospital'
    if 'user_id' not in session or session.get('role') != 'hospital':
        flash("Unauthorized access.", "error")
        return redirect('/login')

    cursor = db.cursor(dictionary=True)
    hospital = None  # Initialize hospital variable
    try:
        discord_username = session.get('discord_username')
        print(f"Fetching hospital details for discord_username: {discord_username}")  # Debugging line

        # Execute the query
        cursor.execute("SELECT * FROM hospitals WHERE discord_username = %s", (discord_username,))
        hospital = cursor.fetchone()  # Fetch the result

        # Fetch all remaining rows to avoid unread result error, even if we don’t need them
        cursor.fetchall()  # This line clears any remaining unread results

        if hospital:
            print(f"Hospital details found: {hospital}")  # Debugging line
        else:
            print("No hospital details found in the database.")  # Debugging line

    except mysql.connector.Error as err:
        flash(f"Database error: {err}", "error")
        return redirect('/')
    
    finally:
        cursor.close()  # Close the cursor after fetching results

    # Render the hospitals.html template with the hospital data
    return render_template('hospitals.html', hospital=hospital)


@app.route('/update_hospital', methods=['GET', 'POST'])
def update_hospital():
    if 'user_id' not in session or session.get('role') != 'hospital':
        flash("Unauthorized access.", "error")
        return redirect('/login')

    cursor = db.cursor(dictionary=True)
    if request.method == 'POST':
        name = request.form.get('name')
        location = request.form.get('location')
        beds_available = request.form.get('beds_available')
        doctors_available = request.form.get('doctors_available') == '1'  # Convert to boolean
        discord_username = session.get('discord_username')

        try:
            cursor.execute("""
                UPDATE hospitals
                SET name = %s, location = %s, beds_available = %s, doctors_available = %s
                WHERE discord_username = %s
            """, (name, location, beds_available, doctors_available, discord_username))
            db.commit()
            flash("Hospital details updated successfully!", "success")
            return redirect('/hospitals')
        except mysql.connector.Error as err:
            db.rollback()
            flash(f"Database error: {err}", "error")
            return redirect('/hospitals')
        finally:
            cursor.close()

    # GET request to fetch current hospital details
    discord_username = session.get('discord_username')
    cursor.execute("SELECT * FROM hospitals WHERE discord_username = %s", (discord_username,))
    hospital = cursor.fetchone()
    cursor.close()
    

    return render_template('update_hospital.html', hospital=hospital)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        if not email or not password:
            flash("Email and password are required.", "error")
            return redirect('/login')

        cursor = db.cursor(dictionary=True, buffered=True)  # Add buffered=True here
        try:
            cursor.execute(
                "SELECT * FROM users WHERE email = %s AND password = %s",
                (email, password)
            )
            user = cursor.fetchone()

            if user:
                session['user_id'] = user['id']  # Store user id in session
                session['role'] = user['role']    # Store user role in session
                session['discord_username'] = user.get('discord_username')  # Ensure this is included

                # Redirect based on user role
                if user['role'] == 'ambulance_driver':
                    return redirect('/driver')
                elif user['role'] == 'hospital':
                    return redirect('/hospitals')
                else:
                    flash("Role not recognized.", "error")
            else:
                flash("Invalid email or password.", "error")
        except mysql.connector.Error as err:
            flash(f"Database error: {err}", "error")
        finally:
            cursor.close()  # Ensure cursor is closed after each use

    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()  # Clear the session
    flash("You have been logged out.", "success")
    return redirect('/login')  # Redirect to login page


@app.route('/driver')
def driver_page():
    token = generate_bearer_token()
    if token is None:
        return "Failed to generate MapmyIndia token", 500
    return render_template('driver.html', token=token)

notif_sent = []

@app.route('/check_signals', methods=['POST'])
def check_signals():
    data = request.get_json()
    print(data)
    latitude = data['latitude']
    longitude = data['longitude']
    already_notified = data['notif_sent']
    print("already notified")
    print(already_notified)
    #buffer_distance = data.get('buffers',3000)
    buffer_distance = 3000
    cursor = db.cursor()
    query = """
    SELECT trdname
    FROM traffic_pnt_signals
    WHERE ST_Distance_Sphere(location, ST_GeomFromText('POINT(%s %s)')) <= %s
    """
    cursor.execute(query, (longitude, latitude, buffer_distance))
    results = cursor.fetchall()
    print(results)
    discord_usernames = []
    print("usernames taken")
    # Collect Discord usernames
    for result in results:
        username = result[0]
        print("in for loop")
        print(username)
        if username not in already_notified:
            # Append new usernames to the list
            discord_usernames.append(username)
            print("in not if")
            print("appended username")
            print(username)
            message = "An ambulance is on its way to a hospital goes through a route along your traffic signal. Please clear the route."
            print(message)
            print("call traffic send notif")
            bot.loop.create_task(send_notification(username, message))
            print("after call send notif")

    print(discord_usernames)
    print("names print done")
    db.commit()  # Commit changes to the database
    cursor.close()

    return jsonify({
        'signals': discord_usernames,
        'message': 'Traffic signals fetched and notifications sent successfully.'
    })

@app.route('/get_counts', methods=['GET'])
def get_counts():
    # Connect to the database (update with your database configuration)
    conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Vani@2607",
        database="Sept_Pro_DB"
    )
    cursor = conn.cursor()

    # Query to get counts for each role
    cursor.execute("SELECT COUNT(*) FROM users WHERE role='hospital'")
    hospitals = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE role='traffic_police'")
    traffic_police = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM users WHERE role='ambulance_driver'")
    ambulance_drivers = cursor.fetchone()[0]

    # Close the database connection
    cursor.close()
    conn.close()

    # Return JSON response
    return jsonify({
        "hospitals": hospitals,
        "traffic_police": traffic_police,
        "ambulance_drivers": ambulance_drivers
    })

# Run both the Flask app and Discord bot concurrently

def run_flask():
    app.run(debug=False, use_reloader=False)

def run_discord_bot():
    bot.run(TOKEN)

if __name__ == '__main__':
    # Start both the Flask app and Discord bot concurrently in separate threads
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.start()

    # Run the Discord bot
    run_discord_bot()