import os
import sys
import sqlite3
from flask import Flask, g, jsonify, request, send_from_directory
from threading import Timer
import webbrowser

# ----------------------------
# 1. Шляхи до файлів
# ----------------------------
if getattr(sys, "frozen", False):
    BASE_DIR = sys._MEIPASS
else:
    BASE_DIR = os.path.dirname(__file__)

DB_PATH = os.path.join(BASE_DIR, "data.db")
SCHEMA_PATH = os.path.join(BASE_DIR, "schema.sql")
STATIC_FOLDER = os.path.join(BASE_DIR, "static")

# ----------------------------
# 2. Flask app
# ----------------------------
app = Flask(__name__, static_folder=STATIC_FOLDER, static_url_path="/static")

# ----------------------------
# 3. Функції роботи з базою
# ----------------------------
def get_db():
    db = getattr(g, "_database", None)
    if db is None:
        need_init = not os.path.exists(DB_PATH)
        db = g._database = sqlite3.connect(DB_PATH, check_same_thread=False)
        db.row_factory = sqlite3.Row
        if need_init:
            init_db(db)
    return db

def init_db(db):
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        db.executescript(f.read())
    cur = db.cursor()
    cur.execute("SELECT COUNT(*) as c FROM products")
    if cur.fetchone()["c"] == 0:
        cur.executemany("INSERT INTO products (sku, name, unit) VALUES (?,?,?)", [
            ("SKU001", "Молоток", "шт"),
            ("SKU002", "Гайка M8", "шт"),
            ("SKU003", "Саморіз 4x30", "шт"),
        ])
        cur.executemany("INSERT INTO locations (code, description) VALUES (?,?)", [
            ("A1", "Полиця A ряд 1"),
            ("B1", "Полиця B ряд 1"),
        ])
        db.commit()

@app.teardown_appcontext
def close_db(exception):
    db = getattr(g, "_database", None)
    if db is not None:
        db.close()

# ----------------------------
# 4. Маршрути
# ----------------------------
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

# --- API routes: /api/products, /api/locations, /api/stock, /api/receive, /api/pick, /api/transactions
# API: products
@app.route("/api/products", methods=["GET","POST"])
def products():
    db = get_db()
    cur = db.cursor()
    if request.method == "GET":
        cur.execute("SELECT id, sku, name, unit FROM products ORDER BY sku")
        rows = [dict(r) for r in cur.fetchall()]
        return jsonify(rows)
    data = request.get_json() or {}
    sku = data.get("sku")
    name = data.get("name")
    unit = data.get("unit","шт")
    if not sku or not name:
        return jsonify({"error":"sku and name required"}),400
    try:
        cur.execute("INSERT INTO products (sku,name,unit) VALUES (?,?,?)",(sku,name,unit))
        db.commit()
        return jsonify({"ok":True}),201
    except sqlite3.IntegrityError as e:
        return jsonify({"error":str(e)}),400

# API: locations
@app.route("/api/locations", methods=["GET","POST"])
def locations():
    db = get_db()
    cur = db.cursor()
    if request.method == "GET":
        cur.execute("SELECT id, code, description FROM locations ORDER BY code")
        return jsonify([dict(r) for r in cur.fetchall()])
    data = request.get_json() or {}
    code = data.get("code")
    desc = data.get("description","")
    if not code:
        return jsonify({"error":"code required"}),400
    try:
        cur.execute("INSERT INTO locations (code,description) VALUES (?,?)",(code,desc))
        db.commit()
        return jsonify({"ok":True}),201
    except sqlite3.IntegrityError as e:
        return jsonify({"error":str(e)}),400

# API: stock
@app.route("/api/stock", methods=["GET"])
def stock():
    db = get_db()
    cur = db.cursor()
    cur.execute("""
        SELECT s.id, p.sku, p.name, p.unit, l.code as location, s.batch, s.quantity
        FROM stock s
        JOIN products p ON p.id = s.product_id
        JOIN locations l ON l.id = s.location_id
        ORDER BY p.sku, l.code
    """)
    return jsonify([dict(r) for r in cur.fetchall()])

def find_product(db, sku):
    cur = db.cursor()
    cur.execute("SELECT id FROM products WHERE sku = ?", (sku,))
    r = cur.fetchone()
    return r["id"] if r else None

def find_location(db, code):
    cur = db.cursor()
    cur.execute("SELECT id FROM locations WHERE code = ?", (code,))
    r = cur.fetchone()
    return r["id"] if r else None

# API: receive
@app.route("/api/receive", methods=["POST"])
def receive():
    db = get_db()
    data = request.get_json() or {}
    sku = data.get("sku")
    loc = data.get("location")
    qty = int(data.get("qty",0))
    batch = data.get("batch")
    note = data.get("note","")
    if not sku or not loc or qty<=0:
        return jsonify({"error":"sku, location and qty>0 required"}),400
    pid = find_product(db, sku)
    if pid is None:
        return jsonify({"error":"product not found"}),404
    lid = find_location(db, loc)
    if lid is None:
        return jsonify({"error":"location not found"}),404
    cur = db.cursor()
    try:
        cur.execute("SELECT id, quantity FROM stock WHERE product_id=? AND location_id=? AND (batch IS ? OR batch = ?)", (pid,lid,batch,batch))
        row = cur.fetchone()
        if row:
            newq = row["quantity"] + qty
            cur.execute("UPDATE stock SET quantity=? WHERE id=?", (newq, row["id"]))
        else:
            cur.execute("INSERT INTO stock (product_id, location_id, batch, quantity) VALUES (?,?,?,?)", (pid,lid,batch,qty))
        cur.execute("INSERT INTO transactions (type, product_id, location_id, qty, batch, note) VALUES (?,?,?,?,?,?)", ("receive", pid, lid, qty, batch, note))
        db.commit()
        return jsonify({"ok":True})
    except Exception as e:
        db.rollback()
        return jsonify({"error":str(e)}),500

# API: pick
@app.route("/api/pick", methods=["POST"])
def pick():
    db = get_db()
    data = request.get_json() or {}
    sku = data.get("sku")
    loc = data.get("location")
    qty = int(data.get("qty",0))
    batch = data.get("batch")
    note = data.get("note","")
    if not sku or qty<=0:
        return jsonify({"error":"sku and qty>0 required"}),400
    pid = find_product(db, sku)
    if pid is None:
        return jsonify({"error":"product not found"}),404
    lid = None
    if loc:
        lid = find_location(db, loc)
        if lid is None:
            return jsonify({"error":"location not found"}),404
    cur = db.cursor()
    try:
        if lid:
            cur.execute("SELECT id, quantity FROM stock WHERE product_id=? AND location_id=? AND (batch IS ? OR batch = ?)", (pid,lid,batch,batch))
            row = cur.fetchone()
            if not row or row["quantity"] < qty:
                return jsonify({"error":"insufficient qty at location"}),400
            newq = row["quantity"] - qty
            cur.execute("UPDATE stock SET quantity=? WHERE id=?", (newq, row["id"]))
        else:
            cur.execute("SELECT id, quantity FROM stock WHERE product_id=? ORDER BY id", (pid,))
            remaining = qty
            rows = cur.fetchall()
            for r in rows:
                if remaining<=0: break
                take = min(remaining, r["quantity"])
                newq = r["quantity"] - take
                cur.execute("UPDATE stock SET quantity=? WHERE id=?", (newq, r["id"]))
                remaining -= take
            if remaining>0:
                return jsonify({"error":"insufficient total qty"}),400
        cur.execute("INSERT INTO transactions (type, product_id, location_id, qty, batch, note) VALUES (?,?,?,?,?,?)", ("pick", pid, lid, qty, batch, note))
        db.commit()
        return jsonify({"ok":True})
    except Exception as e:
        db.rollback()
        return jsonify({"error":str(e)}),500

# API: transactions
@app.route("/api/transactions", methods=["GET"])
def transactions():
    db = get_db()
    cur = db.cursor()
    cur.execute("""SELECT t.id, t.type, p.sku, p.name, l.code as location, t.qty, t.batch, t.ts, t.note
                   FROM transactions t
                   LEFT JOIN products p ON p.id = t.product_id
                   LEFT JOIN locations l ON l.id = t.location_id
                   ORDER BY t.ts DESC LIMIT 200""")
    return jsonify([dict(r) for r in cur.fetchall()])

# ----------------------------
# 5. Допоміжні функції find_product, find_location
# ----------------------------

def find_product(db, sku):
    cur = db.cursor()
    cur.execute("SELECT id FROM products WHERE sku = ?", (sku,))
    r = cur.fetchone()
    return r["id"] if r else None

def find_location(db, code):
    cur = db.cursor()
    cur.execute("SELECT id FROM locations WHERE code = ?", (code,))
    r = cur.fetchone()
    return r["id"] if r else None

# ----------------------------
# 6. Запуск сервера і відкриття браузера
# ----------------------------
if __name__ == "__main__":
    port = 5000
    url = f"http://127.0.0.1:{port}/"
    if os.environ.get("THE MAIN START-UP TOOL") == "true":  
        Timer(1, lambda: webbrowser.open(url)).start()
    app.run(host="0.0.0.0", port=port, debug=True)
