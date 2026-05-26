from flask import Flask, render_template, g, flash, request, redirect, url_for
import pymysql
import pymysql.cursors
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

def get_db():
    """Helper function to get or create a database connection per request."""
    if 'db' not in g:
        g.db = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB'],
            cursorclass=pymysql.cursors.DictCursor
        )
    return g.db

@app.teardown_appcontext
def teardown_db(exception):
    """Closes the database connection at the end of the request context."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

# Verification test on startup
try:
    with app.app_context():
        conn = pymysql.connect(
            host=app.config['MYSQL_HOST'],
            user=app.config['MYSQL_USER'],
            password=app.config['MYSQL_PASSWORD'],
            database=app.config['MYSQL_DB']
        )
        print("\n" + "="*60)
        print("  [SUCCESS] DATABASE CONNECTION VERIFICATION: SUCCESS!")
        print("  Connected to MySQL Database 'fir_db' successfully.")
        print("="*60 + "\n")
        conn.close()
except Exception as e:
    print("\n" + "="*60)
    print("  [FAILED] DATABASE CONNECTION VERIFICATION: FAILED!")
    print(f"  Error: {e}")
    print("="*60 + "\n")

@app.route('/')
def index():
    """Home Dashboard route displaying live metrics from the database."""
    db = get_db()
    counts = {}
    with db.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) AS cnt FROM station;")
        counts['stations'] = cursor.fetchone()['cnt']
        
        cursor.execute("SELECT COUNT(*) AS cnt FROM officer;")
        counts['officers'] = cursor.fetchone()['cnt']
        
        cursor.execute("SELECT COUNT(*) AS cnt FROM complainant;")
        counts['complainants'] = cursor.fetchone()['cnt']
        
        cursor.execute("SELECT COUNT(*) AS cnt FROM fir;")
        counts['firs'] = cursor.fetchone()['cnt']
        
    return render_template('index.html', counts=counts)

# ==========================================
# STATIONS CRUD ROUTES (Phase 1.3)
# ==========================================

@app.route('/stations')
def list_stations():
    """Fetch all stations in descending order of ID."""
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT station_id, name, district, address, phone, jurisdiction_area, established_year FROM station ORDER BY station_id DESC;")
        stations = cursor.fetchall()
    return render_template('stations/list.html', stations=stations)

@app.route('/stations/new', methods=['GET', 'POST'])
def new_station():
    """Render a blank form (GET) or insert a new station (POST)."""
    if request.method == 'POST':
        name = request.form['name']
        district = request.form['district']
        address = request.form['address']
        phone = request.form['phone']
        jurisdiction_area = request.form['jurisdiction_area']
        established_year = request.form['established_year'] or None
        
        db = get_db()
        try:
            with db.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO station (name, district, address, phone, jurisdiction_area, established_year) VALUES (%s, %s, %s, %s, %s, %s);",
                    (name, district, address, phone, jurisdiction_area, established_year)
                )
            db.commit()
            flash("Station added successfully!", "success")
            return redirect(url_for('list_stations'))
        except Exception as e:
            flash(f"Error adding station: {e}", "danger")
            
    return render_template('stations/form.html')

@app.route('/stations/<int:id>/edit', methods=['GET', 'POST'])
def edit_station(id):
    """Render a pre-filled edit form (GET) or update the station (POST)."""
    db = get_db()
    if request.method == 'POST':
        name = request.form['name']
        district = request.form['district']
        address = request.form['address']
        phone = request.form['phone']
        jurisdiction_area = request.form['jurisdiction_area']
        established_year = request.form['established_year'] or None
        
        try:
            with db.cursor() as cursor:
                cursor.execute(
                    "UPDATE station SET name=%s, district=%s, address=%s, phone=%s, jurisdiction_area=%s, established_year=%s WHERE station_id=%s;",
                    (name, district, address, phone, jurisdiction_area, established_year, id)
                )
            db.commit()
            flash("Station updated successfully!", "success")
            return redirect(url_for('list_stations'))
        except Exception as e:
            flash(f"Error updating station: {e}", "danger")
            
    with db.cursor() as cursor:
        cursor.execute("SELECT station_id, name, district, address, phone, jurisdiction_area, established_year FROM station WHERE station_id=%s;", (id,))
        station = cursor.fetchone()
        
    if not station:
        flash("Station not found.", "danger")
        return redirect(url_for('list_stations'))
        
    return render_template('stations/form.html', station=station)

@app.route('/stations/<int:id>/delete', methods=['POST'])
def delete_station(id):
    """Delete a station by ID. Catch foreign key violation if officers are assigned."""
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("DELETE FROM station WHERE station_id=%s;", (id,))
        db.commit()
        flash("Station deleted successfully!", "success")
    except pymysql.err.IntegrityError:
        flash("Cannot delete — officers are assigned to this station", "danger")
    except Exception as e:
        flash(f"Error deleting station: {e}", "danger")
    return redirect(url_for('list_stations'))

# ==========================================
# OFFICERS CRUD ROUTES (Phase 1.4)
# ==========================================

@app.route('/officers')
def list_officers():
    """Fetch all officers with a JOIN to station to get station name, ordered by ID descending."""
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("""
            SELECT o.officer_id, o.station_id, o.name, o.badge_number, o.rank, o.contact, o.email, o.join_date, s.name AS station_name
            FROM officer o 
            JOIN station s ON o.station_id = s.station_id
            ORDER BY o.officer_id DESC;
        """)
        officers = cursor.fetchall()
    return render_template('officers/list.html', officers=officers)

@app.route('/officers/new', methods=['GET', 'POST'])
def new_officer():
    """Render a blank form with station dropdown (GET) or insert a new officer (POST)."""
    db = get_db()
    if request.method == 'POST':
        station_id = request.form['station_id']
        name = request.form['name']
        badge_number = request.form['badge_number']
        rank = request.form['rank']
        contact = request.form['contact']
        email = request.form['email']
        join_date = request.form['join_date'] or None
        
        try:
            with db.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO officer (station_id, name, badge_number, `rank`, contact, email, join_date) VALUES (%s, %s, %s, %s, %s, %s, %s);",
                    (station_id, name, badge_number, rank, contact, email, join_date)
                )
            db.commit()
            flash("Officer added successfully!", "success")
            return redirect(url_for('list_officers'))
        except Exception as e:
            flash(f"Error adding officer: {e}", "danger")
            
    with db.cursor() as cursor:
        cursor.execute("SELECT station_id, name FROM station ORDER BY name ASC;")
        stations = cursor.fetchall()
    return render_template('officers/form.html', stations=stations)

@app.route('/officers/<int:id>/edit', methods=['GET', 'POST'])
def edit_officer(id):
    """Render a pre-filled form (GET) or update the officer details (POST)."""
    db = get_db()
    if request.method == 'POST':
        station_id = request.form['station_id']
        name = request.form['name']
        badge_number = request.form['badge_number']
        rank = request.form['rank']
        contact = request.form['contact']
        email = request.form['email']
        join_date = request.form['join_date'] or None
        
        try:
            with db.cursor() as cursor:
                cursor.execute(
                    "UPDATE officer SET station_id=%s, name=%s, badge_number=%s, `rank`=%s, contact=%s, email=%s, join_date=%s WHERE officer_id=%s;",
                    (station_id, name, badge_number, rank, contact, email, join_date, id)
                )
            db.commit()
            flash("Officer updated successfully!", "success")
            return redirect(url_for('list_officers'))
        except Exception as e:
            flash(f"Error updating officer: {e}", "danger")
            
    with db.cursor() as cursor:
        cursor.execute("SELECT officer_id, station_id, name, badge_number, `rank`, contact, email, join_date FROM officer WHERE officer_id=%s;", (id,))
        officer = cursor.fetchone()
        
    if not officer:
        flash("Officer not found.", "danger")
        return redirect(url_for('list_officers'))
        
    with db.cursor() as cursor:
        cursor.execute("SELECT station_id, name FROM station ORDER BY name ASC;")
        stations = cursor.fetchall()
        
    return render_template('officers/form.html', officer=officer, stations=stations)

@app.route('/officers/<int:id>/delete', methods=['POST'])
def delete_officer(id):
    """Delete an officer by ID. Catch foreign key violation if officer has FIRs or evidence linked."""
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("DELETE FROM officer WHERE officer_id=%s;", (id,))
        db.commit()
        flash("Officer deleted successfully!", "success")
    except pymysql.err.IntegrityError:
        flash("Cannot delete — this officer has FIRs or evidence linked", "danger")
    except Exception as e:
        flash(f"Error deleting officer: {e}", "danger")
    return redirect(url_for('list_officers'))

# ==========================================
# COMPLAINANTS CRUD ROUTES (Phase 1.5)
# ==========================================

@app.route('/complainants')
def list_complainants():
    """Fetch all complainants, ordered by ID descending."""
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT complainant_id, name, phone, address, dob, id_proof_type, id_proof_number FROM complainant ORDER BY complainant_id DESC;")
        complainants = cursor.fetchall()
    return render_template('complainants/list.html', complainants=complainants)

@app.route('/complainants/new', methods=['GET', 'POST'])
def new_complainant():
    """Render a blank complainant registration form (GET) or insert a new record (POST)."""
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        dob = request.form['dob'] or None
        id_proof_type = request.form['id_proof_type']
        id_proof_number = request.form['id_proof_number']
        
        db = get_db()
        try:
            with db.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO complainant (name, phone, address, dob, id_proof_type, id_proof_number) VALUES (%s, %s, %s, %s, %s, %s);",
                    (name, phone, address, dob, id_proof_type, id_proof_number)
                )
            db.commit()
            flash("Complainant registered successfully!", "success")
            return redirect(url_for('list_complainants'))
        except Exception as e:
            flash(f"Error registering complainant: {e}", "danger")
            
    return render_template('complainants/form.html')

@app.route('/complainants/<int:id>/edit', methods=['GET', 'POST'])
def edit_complainant(id):
    """Render a pre-filled form (GET) or update complainant (POST)."""
    db = get_db()
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        dob = request.form['dob'] or None
        id_proof_type = request.form['id_proof_type']
        id_proof_number = request.form['id_proof_number']
        
        try:
            with db.cursor() as cursor:
                cursor.execute(
                    "UPDATE complainant SET name=%s, phone=%s, address=%s, dob=%s, id_proof_type=%s, id_proof_number=%s WHERE complainant_id=%s;",
                    (name, phone, address, dob, id_proof_type, id_proof_number, id)
                )
            db.commit()
            flash("Complainant updated successfully!", "success")
            return redirect(url_for('list_complainants'))
        except Exception as e:
            flash(f"Error updating complainant: {e}", "danger")
            
    with db.cursor() as cursor:
        cursor.execute("SELECT complainant_id, name, phone, address, dob, id_proof_type, id_proof_number FROM complainant WHERE complainant_id=%s;", (id,))
        complainant = cursor.fetchone()
        
    if not complainant:
        flash("Complainant not found.", "danger")
        return redirect(url_for('list_complainants'))
        
    return render_template('complainants/form.html', complainant=complainant)

@app.route('/complainants/<int:id>/delete', methods=['POST'])
def delete_complainant(id):
    """Delete a complainant by ID. Catch foreign key violation if complainant has FIRs linked."""
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("DELETE FROM complainant WHERE complainant_id=%s;", (id,))
        db.commit()
        flash("Complainant deleted successfully!", "success")
    except pymysql.err.IntegrityError:
        flash("Cannot delete — this complainant has FIRs linked", "danger")
    except Exception as e:
        flash(f"Error deleting complainant: {e}", "danger")
    return redirect(url_for('list_complainants'))

if __name__ == '__main__':
    app.run(debug=True)
