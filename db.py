import sqlite3
import os
import click
from flask import current_app, g

def get_db_path():
    return current_app.config.get('DATABASE', 'data.db')

def get_db():
    """Connect to the application's configured database. The connection
    is unique for each request and will be reused if this is called again.
    """
    if "db" not in g:
        db_path = get_db_path()
        need_init = not os.path.exists(db_path)
        
        conn = sqlite3.connect(db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        g.db = conn
        
        if need_init:
            init_db()
        else:
            # Check if users table exists, if not, run init_db to migrate
            try:
                cur = conn.cursor()
                cur.execute("SELECT 1 FROM users LIMIT 1")
            except sqlite3.OperationalError:
                init_db()
                
    return g.db

def close_db(e=None):
    """If this request connected to the database, close the
    connection.
    """
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    
    # Create default admin if not exists
    create_user(db, "admin", "admin", "admin")
    db.commit()

@click.command('init-db')
def init_db_command():
    """Clear the existing data and create new tables."""
    init_db()
    click.echo('Initialized the database.')

def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)

# ----------------------------
# Helper Functions
# ----------------------------

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    cur.close()
    return cur.lastrowid

# ----------------------------
# User Management Helpers
# ----------------------------
from werkzeug.security import generate_password_hash, check_password_hash

def create_user(db, username, password, role="user"):
    try:
        cur = db.execute(
            "INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)",
            (username, generate_password_hash(password), role)
        )
        db.commit()
        return True
    except sqlite3.IntegrityError:
        return False

def verify_user(db, username, password):
    user = db.execute(
        "SELECT * FROM users WHERE username = ?", (username,)
    ).fetchone()
    
    if user and check_password_hash(user['password_hash'], password):
        return user
    return None

def get_user_by_id(db, user_id):
    return db.execute(
        "SELECT * FROM users WHERE id = ?", (user_id,)
    ).fetchone()
