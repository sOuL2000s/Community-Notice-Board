import sqlite3
from flask import Flask, render_template, request, url_for, flash, redirect, g, session
from datetime import datetime # Make sure this import is at the top of app.py
import functools

# --- Application Setup ---
app = Flask(__name__)
app.config['SECRET_KEY'] = 'd512faa2cba84c4c8bd6f17d4f171dab9306e40795177ef0' # Change this to a strong, random key!
DATABASE = 'community_notice_board.db'

@app.context_processor
def inject_now():
    """Injects the datetime object into all templates."""
    return {'datetime': datetime}

# --- Database Helper Functions ---
def get_db():
    """Establishes a database connection or returns the existing one."""
    if 'db' not in g:
        g.db = sqlite3.connect(
            DATABASE,
            # REMOVE OR COMMENT OUT THIS LINE: detect_types=sqlite3.PARSE_DECLTYPES
        )
        g.db.row_factory = sqlite3.Row # Allows accessing columns by name
    return g.db

def close_db(e=None):
    """Closes the database connection at the end of the request."""
    db = g.pop('db', None)
    if db is not None:
        db.close()

def init_db():
    """Initializes the database from schema.sql."""
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()

@app.cli.command('init-db')
def init_db_command():
    """Clears the existing data and creates new tables."""
    init_db()
    #flash('Initialized the database.') # This message won't show in CLI, but good practice.
    print("Database initialized successfully.")

app.teardown_appcontext(close_db) # Register close_db to be called after each request

# --- Authentication Decorator ---
def login_required(view):
    """Decorator to ensure a user is logged in before accessing a view."""
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if session.get('logged_in') is None:
            flash('Please log in to access this page.', 'warning')
            return redirect(url_for('admin_login'))
        return view(**kwargs)
    return wrapped_view

# --- Hardcoded Admin Credentials (For MVP - In production, use hashed passwords!) ---
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'password' # **DO NOT USE THIS IN PRODUCTION**

# --- Routes ---

@app.route('/')
def index():
    """Public facing page: Displays active notices."""
    db = get_db()
    now_iso = datetime.now().isoformat() # Renamed to avoid confusion with `now` in SQL
    raw_notices = db.execute(
        """
        SELECT id, title, content, category, is_urgent, created_at, expires_at,
               event_date, event_time, event_location
        FROM notices
        WHERE is_active = 1 AND (expires_at IS NULL OR expires_at > ?)
        ORDER BY is_urgent DESC, created_at DESC
        """,
        (now_iso,) # Use now_iso here
    ).fetchall()

    processed_notices = []
    for notice_row in raw_notices:
        notice = dict(notice_row) # Convert Row object to a mutable dictionary
        if notice['expires_at']:
            # Convert to datetime object only if it's not None
            notice['expires_at'] = datetime.fromisoformat(notice['expires_at'])
        # created_at should always have a value and needs conversion too
        notice['created_at'] = datetime.fromisoformat(notice['created_at'])
        processed_notices.append(notice)

    return render_template('index.html', notices=processed_notices)


@app.route('/admin', methods=['GET', 'POST'])
def admin_login():
    """Admin login page."""
    if session.get('logged_in'):
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        error = None

        if username != ADMIN_USERNAME or password != ADMIN_PASSWORD:
            error = 'Invalid Credentials.'

        if error is None:
            session['logged_in'] = True
            flash('Logged in successfully!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash(error, 'danger')

    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    """Logs the admin out."""
    session.pop('logged_in', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    db = get_db()
    raw_notices = db.execute(
        """
        SELECT id, title, category, is_urgent, created_at,
               expires_at,
               event_date, event_time, event_location, is_active
        FROM notices
        ORDER BY created_at DESC
        """
    ).fetchall()

    # Post-process the notices to convert datetime strings
    processed_notices = []
    for notice_row in raw_notices:
        notice = dict(notice_row) # Convert Row object to a mutable dictionary
        if notice['expires_at']:
            notice['expires_at'] = datetime.fromisoformat(notice['expires_at'])
        
        # created_at should always have a value, so direct conversion is fine
        notice['created_at'] = datetime.fromisoformat(notice['created_at'])
        processed_notices.append(notice)

    return render_template('admin_dashboard.html', notices=processed_notices)

def get_notice(notice_id, check_active=True):
    db = get_db()
    query = """
        SELECT id, title, content, category, is_urgent, created_at,
               expires_at,
               event_date, event_time, event_location, is_active
        FROM notices
        WHERE id = ?
    """
    if check_active:
        query += " AND is_active = 1"
    
    notice_row = db.execute(query, (notice_id,)).fetchone()

    if notice_row is None:
        flash('Notice not found.', 'danger')
        return None
    
    # Convert Row object to a mutable dictionary
    notice = dict(notice_row)

    # Convert datetime strings to datetime objects
    if notice['expires_at']:
        notice['expires_at'] = datetime.fromisoformat(notice['expires_at'])
    notice['created_at'] = datetime.fromisoformat(notice['created_at']) # Should always exist

    return notice

@app.route('/admin/notice/new', methods=['GET', 'POST'])
@login_required
def create_notice():
    """Admin route to create a new notice."""
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category = request.form['category']
        is_urgent = 'is_urgent' in request.form
        expires_at = request.form.get('expires_at') or None
        event_date = request.form.get('event_date') or None
        event_time = request.form.get('event_time') or None
        event_location = request.form.get('event_location') or None
        is_active = 'is_active' in request.form # For admin to control visibility

        error = None
        if not title:
            error = 'Title is required.'
        if not content:
            error = 'Content is required.'

        if error is not None:
            flash(error, 'danger')
        else:
            db = get_db()
            db.execute(
                """
                INSERT INTO notices (title, content, category, is_urgent, created_at, expires_at,
                                     event_date, event_time, event_location, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (title, content, category, is_urgent, datetime.now().isoformat(), expires_at,
                 event_date, event_time, event_location, is_active)
            )
            db.commit()
            flash('Notice created successfully!', 'success')
            return redirect(url_for('admin_dashboard'))

    return render_template('create_edit_notice.html', notice=None)

@app.route('/admin/notice/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_notice(id):
    """Admin route to edit an existing notice."""
    notice = get_notice(id, check_active=False) # Get notice regardless of active status
    if notice is None:
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        category = request.form['category']
        is_urgent = 'is_urgent' in request.form
        expires_at = request.form.get('expires_at') or None
        event_date = request.form.get('event_date') or None
        event_time = request.form.get('event_time') or None
        event_location = request.form.get('event_location') or None
        is_active = 'is_active' in request.form

        error = None
        if not title:
            error = 'Title is required.'
        if not content:
            error = 'Content is required.'

        if error is not None:
            flash(error, 'danger')
        else:
            db = get_db()
            db.execute(
                """
                UPDATE notices
                SET title = ?, content = ?, category = ?, is_urgent = ?, expires_at = ?,
                    event_date = ?, event_time = ?, event_location = ?, is_active = ?
                WHERE id = ?
                """,
                (title, content, category, is_urgent, expires_at,
                 event_date, event_time, event_location, is_active, id)
            )
            db.commit()
            flash('Notice updated successfully!', 'success')
            return redirect(url_for('admin_dashboard'))

    return render_template('create_edit_notice.html', notice=notice)

@app.route('/admin/notice/<int:id>/delete', methods=['POST'])
@login_required
def delete_notice(id):
    """Admin route to delete a notice."""
    notice = get_notice(id, check_active=False) # Get notice regardless of active status
    if notice is None:
        return redirect(url_for('admin_dashboard'))

    db = get_db()
    db.execute('DELETE FROM notices WHERE id = ?', (id,))
    db.commit()
    flash('Notice deleted successfully!', 'success')
    return redirect(url_for('admin_dashboard'))

# --- Run the application ---
if __name__ == '__main__':
    app.run(debug=True) # Set debug=False for production!