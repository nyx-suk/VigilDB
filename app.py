from flask import Flask, render_template, g, flash, request, redirect, url_for, session
import pymysql
import pymysql.cursors
from config import Config
from functools import wraps

app = Flask(__name__)
app.config.from_object(Config)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'officer_id' not in session:
            flash('Please log in to continue.', 'danger')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if 'officer_id' not in session:
            flash('Please log in to continue.', 'danger')
            return redirect(url_for('login'))
        if session.get('role') != 'admin':
            flash('Admin access required.', 'danger')
            return redirect(url_for('dashboard'))
        return f(*args, **kwargs)
    return decorated

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
    if 'officer_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('public_portal'))

@app.route('/public')
def public_portal():
    return render_template('public/landing.html')

@app.route('/public/file-complaint', methods=['GET', 'POST'])
def public_file_complaint():
    db = get_db()
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        address = request.form['address']
        dob = request.form['dob']
        id_proof_type = request.form['id_proof_type']
        id_proof_number = request.form['id_proof_number']
        station_id = request.form['station_id']
        crime_type = request.form['crime_type']
        incident_date = request.form['incident_date']
        incident_location = request.form['incident_location']
        description = request.form['description']
        
        try:
            with db.cursor() as cursor:
                # 1. Officer Auto-assignment Algorithm
                cursor.execute("""
                    SELECT o.officer_id FROM officer o
                    LEFT JOIN fir f ON o.officer_id = f.officer_id AND f.status = 'Open'
                    WHERE o.station_id = %s
                    GROUP BY o.officer_id ORDER BY COUNT(f.fir_id) ASC LIMIT 1
                """, (station_id,))
                row = cursor.fetchone()
                if not row:
                    cursor.execute("SELECT officer_id FROM officer LIMIT 1;")
                    row = cursor.fetchone()
                    if not row:
                        flash("Error: No police officers registered in the system.", "danger")
                        cursor.execute("SELECT station_id, name, district FROM station ORDER BY name ASC;")
                        stations = cursor.fetchall()
                        return render_template('public/complaint_form.html', stations=stations)
                
                officer_id = row['officer_id']
                
                # 2. Insert Complainant details
                cursor.execute("""
                    INSERT INTO complainant (name, phone, address, dob, id_proof_type, id_proof_number)
                    VALUES (%s, %s, %s, %s, %s, %s);
                """, (name, phone, address, dob, id_proof_type, id_proof_number))
                
                complainant_id = cursor.lastrowid
                
                # 3. Insert FIR details
                cursor.execute("""
                    INSERT INTO fir (complainant_id, officer_id, station_id, crime_type, incident_date, incident_location, description, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, 'Open');
                """, (complainant_id, officer_id, station_id, crime_type, incident_date, incident_location, description))
                
                fir_id = cursor.lastrowid
                
            db.commit()
            flash("Complaint successfully registered!", "success")
            return redirect(url_for('public_track', fir_id=fir_id, phone=phone))
        except Exception as e:
            db.rollback()
            flash(f"Error registering complaint: {e}", "danger")
            
    with db.cursor() as cursor:
        cursor.execute("SELECT station_id, name, district FROM station ORDER BY name ASC;")
        stations = cursor.fetchall()
    return render_template('public/complaint_form.html', stations=stations)

@app.route('/public/track')
def public_track():
    fir_id = request.args.get('fir_id')
    phone = request.args.get('phone')
    
    fir = None
    searched = False
    if fir_id and phone:
        searched = True
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute("""
                SELECT f.*, c.name AS complainant_name, c.phone, o.name AS officer_name, s.name AS station_name
                FROM fir f
                JOIN complainant c ON f.complainant_id = c.complainant_id
                JOIN officer o ON f.officer_id = o.officer_id
                JOIN station s ON f.station_id = s.station_id
                WHERE f.fir_id = %s AND c.phone = %s
            """, (fir_id, phone))
            fir = cursor.fetchone()
            
    return render_template('public/track.html', fir=fir, searched=searched)

@app.route('/dashboard')
@login_required
def dashboard():
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
        
        cursor.execute("SELECT COUNT(*) AS cnt FROM fir WHERE status = 'Open';")
        counts['open_firs'] = cursor.fetchone()['cnt']
        
    return render_template('index.html', counts=counts)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'officer_id' in session:
        return redirect(url_for('dashboard'))
        
    if request.method == 'POST':
        badge_number = request.form['badge_number']
        password = request.form['password']
        
        db = get_db()
        with db.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM officer WHERE badge_number = %s AND password_hash = SHA2(%s, 256)",
                (badge_number, password)
            )
            officer = cursor.fetchone()
            
        if officer:
            session['officer_id'] = officer['officer_id']
            session['officer_name'] = officer['name']
            session['role'] = officer['role']
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid badge number or password", "danger")
            
    return render_template('auth/login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ==========================================
# STATIONS CRUD ROUTES (Phase 1.3)
# ==========================================

@app.route('/stations')
@login_required
@admin_required
def list_stations():
    """Fetch all stations in descending order of ID."""
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT station_id, name, district, address, phone, jurisdiction_area, established_year FROM station ORDER BY station_id DESC;")
        stations = cursor.fetchall()
    return render_template('stations/list.html', stations=stations)

@app.route('/stations/new', methods=['GET', 'POST'])
@login_required
@admin_required
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
@login_required
@admin_required
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
@login_required
@admin_required
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
@login_required
@admin_required
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
@login_required
@admin_required
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
@login_required
@admin_required
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
@login_required
@admin_required
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
@login_required
def list_complainants():
    """Fetch all complainants, ordered by ID descending."""
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT complainant_id, name, phone, address, dob, id_proof_type, id_proof_number FROM complainant ORDER BY complainant_id DESC;")
        complainants = cursor.fetchall()
    return render_template('complainants/list.html', complainants=complainants)

@app.route('/complainants/new', methods=['GET', 'POST'])
@login_required
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
@login_required
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
@login_required
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

# ==========================================
# FIR CRUD & LIFE CYCLE ROUTES (Phase 2 & 3)
# ==========================================

@app.route('/firs')
@login_required
def list_firs():
    search = request.args.get('q', '').strip()
    status = request.args.get('status', '')

    db = get_db()
    base_query = """
        SELECT f.*, c.name AS complainant_name, o.name AS officer_name, s.name AS station_name
        FROM fir f
        JOIN complainant c ON f.complainant_id = c.complainant_id
        JOIN officer o ON f.officer_id = o.officer_id
        JOIN station s ON f.station_id = s.station_id
        WHERE 1=1
    """
    params = []

    if search:
        base_query += """ AND (
            f.fir_id LIKE %s OR f.crime_type LIKE %s OR
            c.name LIKE %s OR o.name LIKE %s OR
            f.incident_location LIKE %s
        )"""
        like = f"%{search}%"
        params.extend([like, like, like, like, like])

    if status:
        base_query += " AND f.status = %s"
        params.append(status)

    base_query += " ORDER BY f.fir_id DESC"

    with db.cursor() as cursor:
        cursor.execute(base_query, tuple(params))
        firs = cursor.fetchall()

    return render_template('firs/list.html', firs=firs, search=search, status=status)

@app.route('/firs/new', methods=['GET', 'POST'])
@login_required
def new_fir():
    """Render new FIR form with database dropdowns or insert a new FIR."""
    db = get_db()
    is_admin = session.get('role') == 'admin'
    
    if request.method == 'POST':
        complainant_id = request.form['complainant_id']
        officer_id = session['officer_id'] if session.get('role') == 'officer' else request.form['officer_id']
        station_id = request.form['station_id']
        crime_type = request.form['crime_type']
        incident_date = request.form['incident_date']
        incident_location = request.form['incident_location']
        description = request.form['description']

        try:
            with db.cursor() as cursor:
                cursor.execute(
                    """INSERT INTO fir (complainant_id, officer_id, station_id, crime_type, incident_date, incident_location, description, status) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s, 'Open');""",
                    (complainant_id, officer_id, station_id, crime_type, incident_date, incident_location, description)
                )
            db.commit()
            flash("FIR registered successfully!", "success")
            return redirect(url_for('list_firs'))
        except Exception as e:
            flash(f"Error registering FIR: {e}", "danger")

    with db.cursor() as cursor:
        cursor.execute("SELECT complainant_id, name, phone FROM complainant ORDER BY name ASC;")
        complainants = cursor.fetchall()
        cursor.execute("SELECT officer_id, name, badge_number FROM officer ORDER BY name ASC;")
        officers = cursor.fetchall()
        cursor.execute("SELECT station_id, name FROM station ORDER BY name ASC;")
        stations = cursor.fetchall()

    return render_template('firs/form.html', complainants=complainants, officers=officers, stations=stations, is_admin=is_admin)

@app.route('/firs/<int:id>')
@login_required
def view_fir(id):
    """View the case folder for a specific FIR, including accused, evidence, and investigation logs."""
    db = get_db()
    with db.cursor() as cursor:
        # 1. Fetch FIR Details
        cursor.execute("""
            SELECT f.fir_id, f.complainant_id, f.officer_id, f.station_id, f.crime_type, f.incident_date, f.incident_location, f.description, f.status, f.filing_date,
                   c.name AS complainant_name, c.phone AS complainant_phone, c.address AS complainant_address,
                   o.name AS officer_name, o.badge_number AS officer_badge, o.rank AS officer_rank, o.contact AS officer_contact,
                   s.name AS station_name, s.district AS station_district, s.address AS station_address
            FROM fir f
            JOIN complainant c ON f.complainant_id = c.complainant_id
            JOIN officer o ON f.officer_id = o.officer_id
            JOIN station s ON f.station_id = s.station_id
            WHERE f.fir_id = %s;
        """, (id,))
        fir = cursor.fetchone()

        if not fir:
            flash("FIR not found.", "danger")
            return redirect(url_for('list_firs'))

        # 2. Fetch Accused list (using SELECT * to capture 'nationality' if DDL has run)
        cursor.execute("SELECT * FROM accused WHERE fir_id = %s;", (id,))
        accused_list = cursor.fetchall()

        # Check if 'nationality' column is present in DDL schema
        cursor.execute("SHOW COLUMNS FROM accused;")
        cols = [c['Field'] for c in cursor.fetchall()]
        has_nationality = 'nationality' in cols

        # 3. Fetch Evidence items
        cursor.execute("""
            SELECT e.evidence_id, e.type, e.description, e.collected_date, e.storage_location, e.status,
                   o.name AS officer_name
            FROM evidence e
            JOIN officer o ON e.collected_by = o.officer_id
            WHERE e.fir_id = %s ORDER BY e.evidence_id DESC;
        """, (id,))
        evidence_list = cursor.fetchall()

        # 4. Fetch Investigation Timeline logs
        cursor.execute("""
            SELECT i.investigation_id, i.log_date, i.remarks, i.next_action, i.next_hearing_date, i.outcome,
                   o.name AS officer_name
            FROM investigation i
            JOIN officer o ON i.officer_id = o.officer_id
            WHERE i.fir_id = %s ORDER BY i.log_date DESC;
        """, (id,))
        investigation_logs = cursor.fetchall()

    return render_template('firs/detail.html', fir=fir, accused_list=accused_list,
                           evidence_list=evidence_list, investigation_logs=investigation_logs,
                           has_nationality=has_nationality)

@app.route('/firs/<int:id>/status', methods=['POST'])
@login_required
def update_fir_status(id):
    new_status = request.form['status']
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("UPDATE fir SET status = %s WHERE fir_id = %s", (new_status, id))
        db.commit()
        flash(f"FIR status updated to {new_status}", "success")
    except Exception as e:
        flash(f"Error updating status: {e}", "danger")
    return redirect(url_for('view_fir', id=id))

# ==========================================
# ACCUSED SUB-ROUTES
# ==========================================

@app.route('/firs/<int:fir_id>/accused/new', methods=['GET', 'POST'])
@login_required
def new_accused(fir_id):
    db = get_db()
    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob'] or None
        address = request.form['address'] or None
        contact = request.form['contact'] or None
        prior_record = request.form['prior_record']
        arrest_status = request.form['arrest_status']

        fields = ["fir_id", "name", "dob", "address", "contact", "prior_record", "arrest_status"]
        values = [fir_id, name, dob, address, contact, prior_record, arrest_status]

        if 'nationality' in request.form:
            fields.append("nationality")
            values.append(request.form['nationality'] or None)

        placeholders = ", ".join(["%s"] * len(values))
        columns_str = ", ".join(fields)
        query = f"INSERT INTO accused ({columns_str}) VALUES ({placeholders});"

        try:
            with db.cursor() as cursor:
                cursor.execute(query, tuple(values))
            db.commit()
            flash("Accused added", "success")
            return redirect(url_for('view_fir', id=fir_id))
        except Exception as e:
            flash(f"Error adding accused: {e}", "danger")

    with db.cursor() as cursor:
        cursor.execute("SHOW COLUMNS FROM accused LIKE 'nationality';")
        nationality_exists = cursor.fetchone() is not None

    return render_template('accused/form.html', fir_id=fir_id, nationality_exists=nationality_exists)

@app.route('/accused/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_accused(id):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM accused WHERE accused_id = %s;", (id,))
        accused = cursor.fetchone()
        
        if not accused:
            flash("Accused record not found.", "danger")
            return redirect(url_for('list_firs'))

        cursor.execute("SHOW COLUMNS FROM accused LIKE 'nationality';")
        nationality_exists = cursor.fetchone() is not None

    if request.method == 'POST':
        name = request.form['name']
        dob = request.form['dob'] or None
        address = request.form['address'] or None
        contact = request.form['contact'] or None
        prior_record = request.form['prior_record']
        arrest_status = request.form['arrest_status']
        fir_id = accused['fir_id']

        updates = ["name=%s", "dob=%s", "address=%s", "contact=%s", "prior_record=%s", "arrest_status=%s"]
        values = [name, dob, address, contact, prior_record, arrest_status]

        if 'nationality' in request.form:
            updates.append("nationality=%s")
            values.append(request.form['nationality'] or None)

        values.append(id)
        updates_str = ", ".join(updates)
        query = f"UPDATE accused SET {updates_str} WHERE accused_id=%s;"

        try:
            with db.cursor() as cursor:
                cursor.execute(query, tuple(values))
            db.commit()
            flash("Accused record updated", "success")
            return redirect(url_for('view_fir', id=fir_id))
        except Exception as e:
            flash(f"Error updating accused: {e}", "danger")

    return render_template('accused/form.html', accused=accused, fir_id=accused['fir_id'], nationality_exists=nationality_exists)

@app.route('/accused/<int:id>/delete', methods=['POST'])
@login_required
def delete_accused(id):
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT fir_id FROM accused WHERE accused_id = %s;", (id,))
            record = cursor.fetchone()
            if not record:
                flash("Accused not found.", "danger")
                return redirect(url_for('list_firs'))
            fir_id = record['fir_id']
            cursor.execute("DELETE FROM accused WHERE accused_id = %s;", (id,))
        db.commit()
        flash("Accused record removed", "success")
        return redirect(url_for('view_fir', id=fir_id))
    except Exception as e:
        flash(f"Error removing accused: {e}", "danger")
        return redirect(url_for('list_firs'))

# ==========================================
# EVIDENCE SUB-ROUTES
# ==========================================

@app.route('/firs/<int:fir_id>/evidence/new', methods=['GET', 'POST'])
@login_required
def new_evidence(fir_id):
    db = get_db()
    if request.method == 'POST':
        collected_by = request.form['collected_by']
        type = request.form['type']
        description = request.form['description']
        collected_date = request.form['collected_date']
        storage_location = request.form['storage_location'] or None
        status = request.form['status']

        try:
            with db.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO evidence (fir_id, collected_by, type, description, collected_date, storage_location, status)
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                """, (fir_id, collected_by, type, description, collected_date, storage_location, status))
            db.commit()
            flash("Evidence logged", "success")
            return redirect(url_for('view_fir', id=fir_id))
        except Exception as e:
            flash(f"Error logging evidence: {e}", "danger")

    with db.cursor() as cursor:
        cursor.execute("SELECT officer_id, name, badge_number FROM officer ORDER BY name ASC;")
        officers = cursor.fetchall()

    return render_template('evidence/form.html', fir_id=fir_id, officers=officers)

@app.route('/evidence/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_evidence(id):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM evidence WHERE evidence_id = %s;", (id,))
        evidence = cursor.fetchone()
        
        if not evidence:
            flash("Evidence not found.", "danger")
            return redirect(url_for('list_firs'))

    if request.method == 'POST':
        collected_by = request.form['collected_by']
        type = request.form['type']
        description = request.form['description']
        collected_date = request.form['collected_date']
        storage_location = request.form['storage_location'] or None
        status = request.form['status']
        fir_id = evidence['fir_id']

        try:
            with db.cursor() as cursor:
                cursor.execute("""
                    UPDATE evidence 
                    SET collected_by=%s, type=%s, description=%s, collected_date=%s, storage_location=%s, status=%s
                    WHERE evidence_id=%s;
                """, (collected_by, type, description, collected_date, storage_location, status, id))
            db.commit()
            flash("Evidence updated", "success")
            return redirect(url_for('view_fir', id=fir_id))
        except Exception as e:
            flash(f"Error updating evidence: {e}", "danger")

    with db.cursor() as cursor:
        cursor.execute("SELECT officer_id, name, badge_number FROM officer ORDER BY name ASC;")
        officers = cursor.fetchall()

    return render_template('evidence/form.html', evidence=evidence, fir_id=evidence['fir_id'], officers=officers)

@app.route('/evidence/<int:id>/delete', methods=['POST'])
@login_required
def delete_evidence(id):
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT fir_id FROM evidence WHERE evidence_id = %s;", (id,))
            record = cursor.fetchone()
            if not record:
                flash("Evidence not found.", "danger")
                return redirect(url_for('list_firs'))
            fir_id = record['fir_id']
            cursor.execute("DELETE FROM evidence WHERE evidence_id = %s;", (id,))
        db.commit()
        flash("Evidence entry removed", "success")
        return redirect(url_for('view_fir', id=fir_id))
    except Exception as e:
        flash(f"Error deleting evidence: {e}", "danger")
        return redirect(url_for('list_firs'))

# ==========================================
# INVESTIGATION PROGRESS TIMELINE ROUTES
# ==========================================

@app.route('/firs/<int:fir_id>/investigation/new', methods=['GET', 'POST'])
@login_required
def new_investigation_log(fir_id):
    db = get_db()
    if request.method == 'POST':
        officer_id = request.form['officer_id']
        log_date = request.form['log_date']
        remarks = request.form['remarks']
        next_action = request.form['next_action'] or None
        next_hearing_date = request.form['next_hearing_date'] or None
        outcome = request.form['outcome']

        try:
            with db.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO investigation (fir_id, officer_id, log_date, remarks, next_action, next_hearing_date, outcome)
                    VALUES (%s, %s, %s, %s, %s, %s, %s);
                """, (fir_id, officer_id, log_date, remarks, next_action, next_hearing_date, outcome))
            db.commit()
            flash("Investigation entry added", "success")
            return redirect(url_for('view_fir', id=fir_id))
        except Exception as e:
            flash(f"Error logging progress: {e}", "danger")

    with db.cursor() as cursor:
        cursor.execute("SELECT officer_id, name, badge_number FROM officer ORDER BY name ASC;")
        officers = cursor.fetchall()

    return render_template('investigation/form.html', fir_id=fir_id, officers=officers)

@app.route('/investigation/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_investigation(id):
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM investigation WHERE investigation_id = %s;", (id,))
        investigation = cursor.fetchone()
        
        if not investigation:
            flash("Investigation record not found.", "danger")
            return redirect(url_for('list_firs'))

    if request.method == 'POST':
        officer_id = request.form['officer_id']
        log_date = request.form['log_date']
        remarks = request.form['remarks']
        next_action = request.form['next_action'] or None
        next_hearing_date = request.form['next_hearing_date'] or None
        outcome = request.form['outcome']
        fir_id = investigation['fir_id']

        try:
            with db.cursor() as cursor:
                cursor.execute("""
                    UPDATE investigation 
                    SET officer_id=%s, log_date=%s, remarks=%s, next_action=%s, next_hearing_date=%s, outcome=%s
                    WHERE investigation_id=%s;
                """, (officer_id, log_date, remarks, next_action, next_hearing_date, outcome, id))
            db.commit()
            flash("Investigation log updated", "success")
            return redirect(url_for('view_fir', id=fir_id))
        except Exception as e:
            flash(f"Error updating investigation log: {e}", "danger")

    with db.cursor() as cursor:
        cursor.execute("SELECT officer_id, name, badge_number FROM officer ORDER BY name ASC;")
        officers = cursor.fetchall()

    # Format log_date and next_hearing_date for date inputs if they exist
    if investigation['log_date']:
        if hasattr(investigation['log_date'], 'strftime'):
            investigation['log_date_str'] = investigation['log_date'].strftime('%Y-%m-%d')
        else:
            investigation['log_date_str'] = str(investigation['log_date'])[:10]
            
    if investigation['next_hearing_date']:
        if hasattr(investigation['next_hearing_date'], 'strftime'):
            investigation['next_hearing_date_str'] = investigation['next_hearing_date'].strftime('%Y-%m-%d')
        else:
            investigation['next_hearing_date_str'] = str(investigation['next_hearing_date'])[:10]

    return render_template('investigation/form.html', investigation=investigation, fir_id=investigation['fir_id'], officers=officers)

# ==========================================
# REPORTS & ALTER TABLE DEMO ROUTES (Phase 3.1)
# ==========================================

@app.route('/reports')
@login_required
@admin_required
def reports():
    db = get_db()
    with db.cursor() as cursor:
        cursor.execute("SELECT * FROM open_firs;")
        open_firs_rows = cursor.fetchall()

        cursor.execute("SELECT crime_type, COUNT(*) AS total FROM fir GROUP BY crime_type ORDER BY total DESC;")
        crime_stats = cursor.fetchall()

        cursor.execute("SHOW COLUMNS FROM accused;")
        columns = cursor.fetchall()
        nationality_exists = any(c['Field'] == 'nationality' for c in columns)

    return render_template('reports.html', open_firs_rows=open_firs_rows, crime_stats=crime_stats, nationality_exists=nationality_exists)

@app.route('/reports/alter/add-nationality', methods=['POST'])
@login_required
@admin_required
def add_nationality():
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("ALTER TABLE accused ADD COLUMN nationality VARCHAR(50) DEFAULT 'Indian';")
        db.commit()
        flash("Column 'nationality' added to accused table", "success")
    except pymysql.err.OperationalError as e:
        if e.args[0] == 1060:
            flash("Column already exists", "warning")
        else:
            flash(f"Error: {e}", "danger")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    return redirect(url_for('reports'))

@app.route('/reports/alter/drop-nationality', methods=['POST'])
@login_required
@admin_required
def drop_nationality():
    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("ALTER TABLE accused DROP COLUMN nationality;")
        db.commit()
        flash("Column 'nationality' removed", "warning")
    except Exception as e:
        flash(f"Error: {e}", "danger")
    return redirect(url_for('reports'))

@app.route('/firs/<int:id>/delete', methods=['GET', 'POST'])
@login_required
def delete_fir(id):
    if request.method == 'GET':
        return redirect(url_for('view_fir', id=id))

    db = get_db()
    try:
        with db.cursor() as cursor:
            cursor.execute("SELECT status FROM fir WHERE fir_id = %s;", (id,))
            fir = cursor.fetchone()
            if not fir:
                flash("FIR not found.", "danger")
                return redirect(url_for('list_firs'))

            if fir['status'] != 'Open':
                flash("Only Open FIRs can be deleted", "danger")
                return redirect(url_for('view_fir', id=id))

            cursor.execute("DELETE FROM investigation WHERE fir_id = %s;", (id,))
            cursor.execute("DELETE FROM evidence WHERE fir_id = %s;", (id,))
            cursor.execute("DELETE FROM accused WHERE fir_id = %s;", (id,))
            cursor.execute("DELETE FROM fir WHERE fir_id = %s;", (id,))
        db.commit()
        flash("FIR deleted", "success")
        return redirect(url_for('list_firs'))
    except pymysql.err.IntegrityError as e:
        db.rollback()
        flash(f"Database integrity error: {e}", "danger")
        return redirect(url_for('view_fir', id=id))
    except pymysql.err.OperationalError as e:
        db.rollback()
        flash("Database error — please try again", "danger")
        return redirect(url_for('view_fir', id=id))
    except Exception as e:
        db.rollback()
        flash(f"Error: {e}", "danger")
        return redirect(url_for('view_fir', id=id))

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)

