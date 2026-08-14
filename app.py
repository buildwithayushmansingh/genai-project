from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)

app.secret_key = "energyai-secret-key"


# ==============================
# ELECTRICITY RATE
# ==============================

# Approximate electricity cost per kWh
ELECTRICITY_RATE = 8


# ==============================
# DATABASE CONNECTION
# ==============================

def get_db():

    conn = sqlite3.connect("database.db")

    conn.row_factory = sqlite3.Row

    return conn


# ==============================
# CREATE DATABASE
# ==============================

def create_database():

    conn = get_db()

    # ==============================
    # USERS TABLE
    # ==============================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT UNIQUE NOT NULL,

            email TEXT UNIQUE NOT NULL,

            password TEXT NOT NULL

        )
    """)


    # ==============================
    # ENERGY DATA TABLE
    # ==============================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS energy_data (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            user_id INTEGER NOT NULL,

            energy_usage REAL DEFAULT 0,

            energy_saved REAL DEFAULT 0,

            cost REAL DEFAULT 0,

            FOREIGN KEY (user_id) REFERENCES users(id)

        )
    """)


    # ==============================
    # APPLIANCES TABLE
    # ==============================

    conn.execute("""
        CREATE TABLE IF NOT EXISTS appliances (

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            username TEXT NOT NULL,

            name TEXT NOT NULL,

            power REAL NOT NULL,

            hours REAL NOT NULL

        )
    """)


    conn.commit()

    conn.close()


# ==============================
# UPDATE ENERGY FROM APPLIANCES
# ==============================

def update_energy_from_appliances(username, user_id):

    conn = get_db()


    # Get all appliances of current user

    appliances = conn.execute(
        """
        SELECT power, hours
        FROM appliances
        WHERE username = ?
        """,
        (username,)
    ).fetchall()


    # Calculate total daily energy usage

    total_energy = 0

    for appliance in appliances:

        power = float(appliance["power"])

        hours = float(appliance["hours"])

        # Watts × hours / 1000 = kWh

        total_energy += (power * hours) / 1000


    # Calculate electricity cost

    total_cost = total_energy * ELECTRICITY_RATE


    # Check whether energy data exists

    energy = conn.execute(
        """
        SELECT id
        FROM energy_data
        WHERE user_id = ?
        """,
        (user_id,)
    ).fetchone()


    if energy:

        # Update existing energy data

        conn.execute(
            """
            UPDATE energy_data

            SET energy_usage = ?,
                cost = ?

            WHERE user_id = ?
            """,
            (
                round(total_energy, 2),
                round(total_cost, 2),
                user_id
            )
        )

    else:

        # Create energy data if it doesn't exist

        conn.execute(
            """
            INSERT INTO energy_data
            (
                user_id,
                energy_usage,
                energy_saved,
                cost
            )

            VALUES (?, ?, 0, ?)
            """,
            (
                user_id,
                round(total_energy, 2),
                round(total_cost, 2)
            )
        )


    conn.commit()

    conn.close()


# ==============================
# HOME / LOGIN
# ==============================

@app.route("/")
def home():

    if "user_id" in session:

        return redirect(url_for("dashboard"))

    return render_template("login.html")


# ==============================
# LOGIN
# ==============================

@app.route("/login", methods=["POST"])
def login():

    username = request.form["username"]

    password = request.form["password"]


    conn = get_db()


    user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE username = ?
        """,
        (username,)
    ).fetchone()


    conn.close()


    if user and check_password_hash(
        user["password"],
        password
    ):

        session["user_id"] = user["id"]

        session["username"] = user["username"]

        return redirect(url_for("dashboard"))


    return "Invalid username or password"


# ==============================
# REGISTER
# ==============================

@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "GET":

        return render_template("register.html")


    username = request.form["username"]

    email = request.form["email"]

    password = request.form["password"]

    confirm_password = request.form["confirm_password"]


    # Password check

    if password != confirm_password:

        return "Passwords do not match"


    conn = get_db()


    # Check username

    existing_user = conn.execute(
        """
        SELECT *
        FROM users
        WHERE username = ?
        """,
        (username,)
    ).fetchone()


    if existing_user:

        conn.close()

        return "Username already exists"


    # Check email

    existing_email = conn.execute(
        """
        SELECT *
        FROM users
        WHERE email = ?
        """,
        (email,)
    ).fetchone()


    if existing_email:

        conn.close()

        return "Email already exists"


    # Password hashing

    password_hash = generate_password_hash(password)


    # Create user

    cursor = conn.execute(
        """
        INSERT INTO users
        (
            username,
            email,
            password
        )

        VALUES (?, ?, ?)
        """,
        (
            username,
            email,
            password_hash
        )
    )


    user_id = cursor.lastrowid


    # Create empty energy data

    conn.execute(
        """
        INSERT INTO energy_data
        (
            user_id,
            energy_usage,
            energy_saved,
            cost
        )

        VALUES (?, 0, 0, 0)
        """,
        (user_id,)
    )


    conn.commit()

    conn.close()


    return redirect(url_for("home"))


# ==============================
# DASHBOARD
# ==============================

@app.route("/dashboard")
def dashboard():

    if "user_id" not in session:

        return redirect(url_for("home"))


    conn = get_db()


    # ==============================
    # ENERGY DATA
    # ==============================

    energy = conn.execute(
        """
        SELECT *
        FROM energy_data
        WHERE user_id = ?
        """,
        (session["user_id"],)
    ).fetchone()


    # ==============================
    # APPLIANCES
    # ==============================

    appliances = conn.execute(
        """
        SELECT *
        FROM appliances
        WHERE username = ?
        """,
        (session["username"],)
    ).fetchall()


    conn.close()


    # If energy data doesn't exist

    if energy is None:

        energy = {

            "energy_usage": 0,

            "energy_saved": 0,

            "cost": 0

        }


    return render_template(

        "index.html",

        energy=energy,

        appliances=appliances

    )


# ==============================
# SAVE / UPDATE ENERGY
# ==============================

@app.route("/save-energy", methods=["POST"])
def save_energy():

    if "user_id" not in session:

        return redirect(url_for("home"))


    energy_usage = request.form["energy_usage"]

    energy_saved = request.form["energy_saved"]

    cost = request.form["cost"]


    conn = get_db()


    conn.execute(
        """
        UPDATE energy_data

        SET energy_usage = ?,
            energy_saved = ?,
            cost = ?

        WHERE user_id = ?
        """,
        (
            energy_usage,
            energy_saved,
            cost,
            session["user_id"]
        )
    )


    conn.commit()

    conn.close()


    return redirect(url_for("dashboard"))


# ==============================
# ADD APPLIANCE
# ==============================

@app.route("/add-appliance", methods=["POST"])
def add_appliance():

    if "user_id" not in session:

        return redirect(url_for("home"))


    name = request.form["name"]

    power = request.form["power"]

    hours = request.form["hours"]

    username = session["username"]

    user_id = session["user_id"]


    conn = get_db()


    # Add appliance

    conn.execute(
        """
        INSERT INTO appliances
        (
            username,
            name,
            power,
            hours
        )

        VALUES (?, ?, ?, ?)
        """,
        (
            username,
            name,
            power,
            hours
        )
    )


    conn.commit()

    conn.close()


    # ==============================
    # UPDATE ENERGY DATA
    # ==============================

    update_energy_from_appliances(

        username,

        user_id

    )


    return redirect(url_for("dashboard"))


# ==============================
# DELETE APPLIANCE
# ==============================

@app.route(
    "/delete-appliance/<int:appliance_id>",
    methods=["POST"]
)
def delete_appliance(appliance_id):

    if "user_id" not in session:

        return redirect(url_for("home"))


    username = session["username"]

    user_id = session["user_id"]


    conn = get_db()


    # Delete only current user's appliance

    conn.execute(
        """
        DELETE FROM appliances

        WHERE id = ?

        AND username = ?
        """,
        (
            appliance_id,
            username
        )
    )


    conn.commit()

    conn.close()


    # Recalculate energy after deletion

    update_energy_from_appliances(

        username,

        user_id

    )


    return redirect(url_for("dashboard"))

# ==============================
# DOWNLOAD REPORT
# ==============================

@app.route("/download-report")
def download_report():

    if "user_id" not in session:
        return redirect(url_for("home"))

    conn = get_db()

    # Get energy data
    energy = conn.execute(
        """
        SELECT *
        FROM energy_data
        WHERE user_id = ?
        """,
        (session["user_id"],)
    ).fetchone()

    # Get appliances
    appliances = conn.execute(
        """
        SELECT *
        FROM appliances
        WHERE username = ?
        """,
        (session["username"],)
    ).fetchall()

    conn.close()

    # If no energy data
    if energy is None:
        energy_usage = 0
        energy_saved = 0
        cost = 0
    else:
        energy_usage = energy["energy_usage"]
        energy_saved = energy["energy_saved"]
        cost = energy["cost"]

    # Create report text
    report = f"""
========================================
           ENERGYAI REPORT
========================================

Username: {session["username"]}

----------------------------------------
ENERGY SUMMARY
----------------------------------------

Today's Energy Usage : {energy_usage} kWh
Energy Saved         : {energy_saved} %
Estimated Cost       : ₹{cost}

----------------------------------------
APPLIANCES
----------------------------------------

"""

    # Add appliances
    if appliances:

        for appliance in appliances:

            appliance_usage = (
                float(appliance["power"])
                * float(appliance["hours"])
                / 1000
            )

            report += (
                f"Appliance : {appliance['name']}\n"
                f"Power     : {appliance['power']} W\n"
                f"Usage     : {appliance['hours']} hrs/day\n"
                f"Consumption: {appliance_usage:.2f} kWh/day\n"
                f"----------------------------------------\n"
            )

    else:

        report += "No appliances added yet.\n"


    report += """
----------------------------------------
Generated by EnergyAI
========================================
"""


    # Send report as downloadable file
    from flask import Response

    return Response(
        report,
        mimetype="text/plain",
        headers={
            "Content-Disposition":
            "attachment; filename=EnergyAI_Report.txt"
        }
    )
# ==============================
# LOGOUT
# ==============================

@app.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("home"))


# ==============================
# RUN APP
# ==============================

if __name__ == "__main__":

    create_database()

    app.run(

        debug=True,

        port=8000

    )