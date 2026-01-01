import os
import sys
import functools
from flask import Flask, g, jsonify, request, send_from_directory, session, redirect, url_for, render_template_string
from threading import Timer
import webbrowser
import db  # Import our new DB module

# ----------------------------
# 1. Конфігурація
# ----------------------------
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(__file__)

STATIC_FOLDER = os.path.join(BASE_DIR, "static")

app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path="/static")
app.secret_key = "dev_secret_key_change_in_prod"  # Required for session

# ----------------------------
# 2. Управління базою даних
# ----------------------------

@app.teardown_appcontext
def close_connection(exception):
    db.close_db(exception)

# ----------------------------
# 3. Аутентифікація
# ----------------------------

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('login'))
        return view(**kwargs)
    return wrapped_view

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = db.get_user_by_id(db.get_db(), user_id)

@app.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        database = db.get_db()
        error = None
        
        user = db.verify_user(database, username, password)

        if user is None:
            error = 'Невірне ім’я користувача або пароль.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('index'))

        return render_template_string('''
            <!doctype html>
            <html lang="uk">
            <head>
                <meta charset="utf-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <title>Вхід | Warehouse System</title>
                <style>
                    :root {
                        --bg-color: #121212;
                        --card-bg: #1e1e1e;
                        --primary: #ff5722;
                        --text: #e0e0e0;
                        --input-bg: #2d2d2d;
                    }
                    body {
                        background-color: var(--bg-color);
                        color: var(--text);
                        font-family: 'Inter', sans-serif;
                        display: flex;
                        justify-content: center;
                        align-items: center;
                        height: 100vh;
                        margin: 0;
                    }
                    .card {
                        background: var(--card-bg);
                        padding: 2rem;
                        border-radius: 12px;
                        box-shadow: 0 8px 24px rgba(0,0,0,0.5);
                        width: 100%;
                        max-width: 360px;
                        text-align: center;
                        border: 1px solid #333;
                    }
                    h2 { margin-bottom: 1.5rem; color: var(--primary); font-weight: 600; }
                    input {
                        width: 100%;
                        padding: 12px;
                        margin-bottom: 1rem;
                        background: var(--input-bg);
                        border: 1px solid #444;
                        border-radius: 6px;
                        color: white;
                        box-sizing: border-box;
                        font-size: 1rem;
                    }
                    input:focus { outline: 2px solid var(--primary); border-color: transparent; }
                    button {
                        width: 100%;
                        padding: 12px;
                        background: var(--primary);
                        color: white;
                        border: none;
                        border-radius: 6px;
                        font-size: 1rem;
                        font-weight: 600;
                        cursor: pointer;
                        transition: opacity 0.2s;
                    }
                    button:hover { opacity: 0.9; }
                    .error { color: #ff6b6b; margin-bottom: 1rem; font-size: 0.9rem; }
                </style>
            </head>
            <body>
                <div class="card">
                    <h2>Warehouse Login</h2>
                    {% if error %}
                        <div class="error">{{ error }}</div>
                    {% endif %}
                    <form method="post">
                        <input name="username" placeholder="Логін" required autofocus>
                        <input type="password" name="password" placeholder="Пароль" required>
                        <button type="submit">Увійти</button>
                    </form>
                </div>
            </body>
            </html>
        ''', error=error)

    return render_template_string('''
        <!doctype html>
        <html lang="uk">
        <head>
            <meta charset="utf-8">
            <meta name="viewport" content="width=device-width, initial-scale=1">
            <title>Вхід | Warehouse System</title>
            <style>
                :root {
                    --bg-color: #121212;
                    --card-bg: #1e1e1e;
                    --primary: #ff5722;
                    --text: #e0e0e0;
                    --input-bg: #2d2d2d;
                }
                body {
                    background-color: var(--bg-color);
                    color: var(--text);
                    font-family: 'Inter', sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                }
                .card {
                    background: var(--card-bg);
                    padding: 2rem;
                    border-radius: 12px;
                    box-shadow: 0 8px 24px rgba(0,0,0,0.5);
                    width: 100%;
                    max-width: 360px;
                    text-align: center;
                    border: 1px solid #333;
                }
                h2 { margin-bottom: 1.5rem; color: var(--primary); font-weight: 600; }
                input {
                    width: 100%;
                    padding: 12px;
                    margin-bottom: 1rem;
                    background: var(--input-bg);
                    border: 1px solid #444;
                    border-radius: 6px;
                    color: white;
                    box-sizing: border-box;
                    font-size: 1rem;
                }
                input:focus { outline: 2px solid var(--primary); border-color: transparent; }
                button {
                    width: 100%;
                    padding: 12px;
                    background: var(--primary);
                    color: white;
                    border: none;
                    border-radius: 6px;
                    font-size: 1rem;
                    font-weight: 600;
                    cursor: pointer;
                    transition: opacity 0.2s;
                }
                button:hover { opacity: 0.9; }
            </style>
        </head>
        <body>
            <div class="card">
                <h2>Warehouse Login</h2>
                <form method="post">
                    <input name="username" placeholder="Логін" required autofocus>
                    <input type="password" name="password" placeholder="Пароль" required>
                    <button type="submit">Увійти</button>
                </form>
            </div>
        </body>
        </html>
    ''')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ----------------------------
# 4. Основні маршрути
# ----------------------------

@app.route("/")
@login_required
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

# ----------------------------
# 5. API: Товари (Products)
# ----------------------------

@app.route("/api/products", methods=["GET", "POST"])
@login_required
def products():
    if request.method == "GET":
        rows = db.query_db("SELECT id, sku, name, unit FROM products ORDER BY sku")
        return jsonify([dict(r) for r in rows])
    
    data = request.get_json() or {}
    sku = data.get("sku")
    name = data.get("name")
    unit = data.get("unit", "шт")
    
    if not sku or not name:
        return jsonify({"error": "Потрібні SKU та Назва"}), 400
    
    try:
        db.execute_db("INSERT INTO products (sku,name,unit) VALUES (?,?,?)", (sku, name, unit))
        return jsonify({"ok": True}), 201
    except Exception as e:
        return jsonify({"error": f"Помилка: {str(e)}"}), 400

@app.route("/api/products/<int:pid>", methods=["GET", "PUT", "DELETE"])
@login_required
def product_item(pid):
    if request.method == "GET":
        row = db.query_db("SELECT id, sku, name, unit FROM products WHERE id = ?", (pid,), one=True)
        if not row:
            return jsonify({"error": "Товар не знайдено"}), 404
        return jsonify(dict(row))
    
    if request.method == "PUT":
        data = request.get_json() or {}
        sku = data.get("sku")
        name = data.get("name")
        unit = data.get("unit", "шт")
        if not sku or not name:
            return jsonify({"error": "Потрібні SKU та Назва"}), 400
        try:
            db.execute_db("UPDATE products SET sku=?, name=?, unit=? WHERE id=?", (sku, name, unit, pid))
            return jsonify({"ok": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 400
            
    if request.method == "DELETE":
        # Перевірка на використання в транзакціях
        count = db.query_db("SELECT COUNT(*) as c FROM transactions WHERE product_id = ?", (pid,), one=True)
        if count["c"] > 0:
            return jsonify({"error": "Неможливо видалити: є транзакції"}), 400
        
        db.execute_db("DELETE FROM products WHERE id = ?", (pid,))
        return jsonify({"ok": True})

# ----------------------------
# 6. API: Локації (Locations)
# ----------------------------

@app.route("/api/locations", methods=["GET", "POST"])
@login_required
def locations():
    if request.method == "GET":
        rows = db.query_db("SELECT id, code, description FROM locations ORDER BY code")
        return jsonify([dict(r) for r in rows])
    
    data = request.get_json() or {}
    code = data.get("code")
    desc = data.get("description", "")
    
    if not code:
        return jsonify({"error": "Потрібен код локації"}), 400
    
    try:
        db.execute_db("INSERT INTO locations (code,description) VALUES (?,?)", (code, desc))
        return jsonify({"ok": True}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/locations/<int:lid>", methods=["GET", "PUT", "DELETE"])
@login_required
def location_item(lid):
    if request.method == "GET":
        row = db.query_db("SELECT id, code, description FROM locations WHERE id = ?", (lid,), one=True)
        if not row:
            return jsonify({"error": "Локацію не знайдено"}), 404
        return jsonify(dict(row))
        
    if request.method == "PUT":
        data = request.get_json() or {}
        code = data.get("code")
        desc = data.get("description", "")
        if not code:
            return jsonify({"error": "Потрібен код локації"}), 400
        try:
            db.execute_db("UPDATE locations SET code=?, description=? WHERE id=?", (code, desc, lid))
            return jsonify({"ok": True})
        except Exception as e:
            return jsonify({"error": str(e)}), 400
            
    if request.method == "DELETE":
        count = db.query_db("SELECT COUNT(*) as c FROM transactions WHERE location_id = ?", (lid,), one=True)
        if count["c"] > 0:
            return jsonify({"error": "Неможливо видалити: локація використовується"}), 400
        
        db.execute_db("DELETE FROM locations WHERE id = ?", (lid,))
        return jsonify({"ok": True})

# ----------------------------
# 7. API: Склад (Stock) та Операції
# ----------------------------

@app.route("/api/stock", methods=["GET"])
@login_required
def stock():
    # Інвентаризація: JOIN products + locations
    query = """
        SELECT s.id, p.sku, p.name, p.unit, l.code as location, s.batch, s.quantity
        FROM stock s
        JOIN products p ON p.id = s.product_id
        JOIN locations l ON l.id = s.location_id
        WHERE s.quantity > 0
        ORDER BY p.sku, l.code
    """
    rows = db.query_db(query)
    return jsonify([dict(r) for r in rows])

def find_product_id(sku):
    row = db.query_db("SELECT id FROM products WHERE sku = ?", (sku,), one=True)
    return row["id"] if row else None

def find_location_id(code):
    row = db.query_db("SELECT id FROM locations WHERE code = ?", (code,), one=True)
    return row["id"] if row else None

@app.route("/api/receive", methods=["POST"])
@login_required
def receive():
    """Прийом товару на склад (Reception)"""
    data = request.get_json() or {}
    sku = data.get("sku")
    loc_code = data.get("location")
    qty = int(data.get("qty", 0))
    batch = data.get("batch")
    note = data.get("note", "")
    
    if not sku or not loc_code or qty <= 0:
        return jsonify({"error": "Потрібні SKU, Локація та Кількість > 0"}), 400
    
    pid = find_product_id(sku)
    if pid is None:
        return jsonify({"error": f"Товар {sku} не знайдено"}), 404
        
    lid = find_location_id(loc_code)
    if lid is None:
        return jsonify({"error": f"Локацію {loc_code} не знайдено"}), 404
    
    database = db.get_db()
    cur = database.cursor()
    try:
        # Check if stock exists for this batch/loc
        cur.execute(
            "SELECT id, quantity FROM stock WHERE product_id=? AND location_id=? AND (batch IS ? OR batch = ?)",
            (pid, lid, batch, batch),
        )
        row = cur.fetchone()
        
        if row:
            newq = row["quantity"] + qty
            cur.execute("UPDATE stock SET quantity=? WHERE id=?", (newq, row["id"]))
        else:
            cur.execute(
                "INSERT INTO stock (product_id, location_id, batch, quantity) VALUES (?,?,?,?)",
                (pid, lid, batch, qty),
            )
            
        cur.execute(
            "INSERT INTO transactions (type, product_id, location_id, qty, batch, note) VALUES (?,?,?,?,?,?)",
            ("receive", pid, lid, qty, batch, note),
        )
        database.commit()
        return jsonify({"ok": True})
    except Exception as e:
        database.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/api/pick", methods=["POST"])
@login_required
def pick():
    """Відвантаження товару (Picking) - FIFO Logic"""
    data = request.get_json() or {}
    sku = data.get("sku")
    loc_code = data.get("location") # Optional
    qty = int(data.get("qty", 0))
    batch = data.get("batch") # Optional
    note = data.get("note", "")
    
    if not sku or qty <= 0:
        return jsonify({"error": "Потрібні SKU та Кількість > 0"}), 400
        
    pid = find_product_id(sku)
    if pid is None:
        return jsonify({"error": f"Товар {sku} не знайдено"}), 404
        
    lid = None
    if loc_code:
        lid = find_location_id(loc_code)
        if lid is None:
            return jsonify({"error": f"Локацію {loc_code} не знайдено"}), 404
            
    database = db.get_db()
    cur = database.cursor()
    try:
        # Strategy: If location specified, pick from there.
        # If not, pick from ANY location using FIFO (oldest batch/id first).
        
        if lid:
            # Specific location pick
            cur.execute(
                "SELECT id, quantity FROM stock WHERE product_id=? AND location_id=? AND (batch IS ? OR batch = ?)",
                (pid, lid, batch, batch),
            )
            row = cur.fetchone()
            if not row or row["quantity"] < qty:
                return jsonify({"error": "Недостатньо товару на вказаній локації"}), 400
            
            newq = row["quantity"] - qty
            if newq == 0:
                cur.execute("DELETE FROM stock WHERE id=?", (row["id"],))
            else:
                cur.execute("UPDATE stock SET quantity=? WHERE id=?", (newq, row["id"]))
            
        else:
            # Auto-pick (FIFO)
            # Sort by batch (if date-based) or ID (insertion order)
            cur.execute(
                "SELECT id, quantity, location_id, batch FROM stock WHERE product_id=? AND quantity > 0 ORDER BY id ASC", 
                (pid,)
            )
            rows = cur.fetchall()
            
            remaining = qty
            
            # Calculate total available first
            total_avail = sum(r["quantity"] for r in rows)
            if total_avail < qty:
                return jsonify({"error": f"Недостатньо товару на складі. Доступно: {total_avail}"}), 400
                
            for r in rows:
                if remaining <= 0:
                    break
                take = min(remaining, r["quantity"])
                newq = r["quantity"] - take
                
                if newq == 0:
                    cur.execute("DELETE FROM stock WHERE id=?", (r["id"],))
                else:
                    cur.execute("UPDATE stock SET quantity=? WHERE id=?", (newq, r["id"]))
                
                # Log transaction for each deduction (optional, but better for traceability)
                # Or we can just log one big transaction. Let's log one big one for simplicity 
                # but technically we took from multiple places. 
                # For this MVP, we will log one transaction with NULL location if multi-pick, 
                # or we should log multiple? Let's log multiple if we want precise tracking.
                # But the requirement is simple. Let's just log one generic "pick".
                
                remaining -= take
                
        cur.execute(
            "INSERT INTO transactions (type, product_id, location_id, qty, batch, note) VALUES (?,?,?,?,?,?)",
            ("pick", pid, lid, qty, batch, note),
        )
        database.commit()
        return jsonify({"ok": True})
        
    except Exception as e:
        database.rollback()
        return jsonify({"error": str(e)}), 500

@app.route("/api/transactions", methods=["GET"])
@login_required
def transactions():
    query = """
        SELECT t.id, t.type, p.sku, p.name, l.code as location, t.qty, t.batch, t.ts, t.note
        FROM transactions t
        LEFT JOIN products p ON p.id = t.product_id
        LEFT JOIN locations l ON l.id = t.location_id
        ORDER BY t.ts DESC LIMIT 200
    """
    rows = db.query_db(query)
    return jsonify([dict(r) for r in rows])

# ----------------------------
# 9. API: Користувачі (Admin)
# ----------------------------

@app.route("/api/me")
@login_required
def me():
    return jsonify({
        "id": g.user["id"],
        "username": g.user["username"],
        "role": g.user["role"]
    })

@app.route("/api/users", methods=["GET", "POST"])
@login_required
def users():
    if g.user["role"] != "admin":
        return jsonify({"error": "Доступ заборонено"}), 403
        
    if request.method == "GET":
        rows = db.query_db("SELECT id, username, role FROM users ORDER BY username")
        return jsonify([dict(r) for r in rows])
        
    data = request.get_json() or {}
    username = data.get("username")
    password = data.get("password")
    role = data.get("role", "user")
    
    if not username or not password:
        return jsonify({"error": "Потрібні ім'я та пароль"}), 400
        
    if db.create_user(db.get_db(), username, password, role):
        return jsonify({"ok": True}), 201
    else:
        return jsonify({"error": "Користувач вже існує"}), 400

@app.route("/api/users/<int:uid>", methods=["DELETE"])
@login_required
def delete_user(uid):
    if g.user["role"] != "admin":
        return jsonify({"error": "Доступ заборонено"}), 403
    
    if uid == g.user["id"]:
        return jsonify({"error": "Не можна видалити самого себе"}), 400
        
    db.execute_db("DELETE FROM users WHERE id = ?", (uid,))
    return jsonify({"ok": True})

# ----------------------------
# 8. Запуск
# ----------------------------
if __name__ == "__main__":
    port = 5555
    url = f"http://127.0.0.1:{port}/"
    # Open browser only if not reloader
    if os.environ.get("WERKZEUG_RUN_MAIN") == "true":
        Timer(1, lambda: webbrowser.open(url)).start()
    app.run(host="0.0.0.0", port=port, debug=True)
