
import os, sqlite3, secrets, string, time, hmac, hashlib, base64, json
from datetime import datetime, timezone
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from werkzeug.utils import secure_filename
import requests

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "elroi.db")
UPLOAD_DIR = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key-in-render")
app.config["MAX_CONTENT_LENGTH"] = 8 * 1024 * 1024
ALLOWED_EXTENSIONS = {"png","jpg","jpeg","webp"}

DEFAULT_PRODUCTS = [
("Normal QL","Sphatlo/Kota","Polony, chips & steak + gravy",15,"Polony,Chips,Steak,Gravy"),
("Cheese QL","Sphatlo/Kota","Polony, chips & steak gravy with cheese",20,"Polony,Chips,Steak,Gravy,Cheese"),
("Egg QL","Sphatlo/Kota","Polony, chips & steak gravy with egg",20,"Polony,Chips,Steak,Gravy,Egg"),
("Egg & Cheese","Sphatlo/Kota","Polony, egg & cheese, steak gravy",25,"Polony,Egg,Cheese,Steak,Gravy"),
("Steak QL","Sphatlo/Kota","Steak, polony, cheese & steak gravy",45,"Steak,Polony,Cheese,Gravy"),
("Party Cheese","Sphatlo/Kota","Steak, cheese, polony, steak & gravy",45,"Steak,Cheese,Polony,Gravy"),
("Russian QL","Sphatlo/Kota","Russian, polony, chips & steak gravy",40,"Russian,Polony,Chips,Gravy"),
("Russian & Cheese","Sphatlo/Kota","Russian, polony, chips & steak gravy with cheese",45,"Russian,Polony,Chips,Gravy,Cheese"),
("Elroi QL","Sphatlo/Kota","Chips, patty, polony, cheese, egg, Russian, steak & gravy",60,"Chips,Patty,Polony,Cheese,Egg,Russian,Steak,Gravy"),
("Small Chips","Box Specials","Small chips",15,"Chips"),
("Medium Chips","Box Specials","Medium chips",25,"Chips"),
("Large Chips","Box Specials","Large chips",30,"Chips"),
("Extra Large Chips","Box Specials","Extra large chips",40,"Chips"),
("Polony & Chips","Box Specials","Polony & chips",30,"Polony,Chips"),
("Polony & Chips","Box Specials","Polony & chips",50,"Polony,Chips"),
("Russian & Chips","Box Specials","Russian & chips",15,"Russian,Chips"),
("Vienna & Chips","Box Specials","Vienna & chips",15,"Vienna,Chips"),
("Sausage & Chips","Box Specials","Sausage & chips",15,"Sausage,Chips"),
("Boerewors & Chips","Box Specials","Boerewors & chips",45,"Boerewors,Chips"),
("1/4 Chicken & Chips","Box Specials","Quarter chicken & chips",40,"Chicken,Chips"),
("Half Chicken & Chips","Box Specials","Half chicken & chips",70,"Chicken,Chips"),
("Full Chicken & Chips","Box Specials","Full chicken & chips",120,"Chicken,Chips"),
("Steak & Chips","Box Specials","Steak & chips",70,"Steak,Chips"),
("Small Club Special","Club Specials","Medium chips, polony, steak and gravy sausage",60,"Chips,Polony,Steak,Gravy,Sausage"),
("Large Club Special","Club Specials","Large chips, polony, steak, sausages, gravy",120,"Chips,Polony,Steak,Sausage,Gravy"),
("Breakfast","Club Specials","2 eggs, Vienna, sausage, chips, 2 slices toast, fried tomatoes, T-bone & chips or pap",60,"Eggs,Vienna,Sausage,Chips,Toast,Tomatoes,T-bone,Pap"),
("Normal Chips Burger","Burgers","2 slices of bread, chips & steak gravy",12,"Bread,Chips,Gravy"),
("Chip Burger with Cheese","Burgers","2 slices, chips & cheese & steak gravy",15,"Bread,Chips,Cheese,Gravy"),
("Chip Burger Special","Burgers","2 slices, chips, polony & cheese, steak gravy",20,"Bread,Chips,Polony,Cheese,Gravy"),
("Burger Plain","Burgers","Patty, lettuce, onion, tomato",30,"Patty,Lettuce,Onion,Tomato"),
("Cheese Burger","Burgers","Patty, cheese, lettuce, onion, tomato",35,"Patty,Cheese,Lettuce,Onion,Tomato"),
("Burger Special","Burgers","Patty, cheese, polony, lettuce, onion, tomato & chips",40,"Patty,Cheese,Polony,Lettuce,Onion,Tomato,Chips"),
("Daywood","Toasted Sandwich","Patty, polony, cheese, egg, Russian",50,"Patty,Polony,Cheese,Egg,Russian"),
("Toasted Steak Special","Toasted Sandwich","Steak, cheese, polony & chips on the side",50,"Steak,Cheese,Polony,Chips"),
("Toasted Steak, Cheese & Chips","Toasted Sandwich","Toasted steak, cheese and chips on the side",45,"Steak,Cheese,Chips"),
("Plain Toasted","Toasted Sandwich","Steak, steak and chips",40,"Steak,Chips"),
("T-Bone & All Salad","Pap","T-Bone with all salad",70,"T-Bone,Salad"),
("Steak & All Salad","Pap","Steak with all salad",70,"Steak,Salad"),
("Beef Stew & All Salad","Pap","Beef stew with all salad",70,"Beef Stew,Salad"),
("Boerewors & All Salad","Pap","Boerewors with all salad",45,"Boerewors,Salad"),
("Quarter Chicken & All Salad","Pap","Quarter chicken with all salad",40,"Chicken,Salad"),
("Half Grilled Chicken & All Salad","Pap","Half grilled chicken with all salad",60,"Chicken,Salad"),
("Full Grilled Chicken & All Salad","Pap","Full grilled chicken with all salad",120,"Chicken,Salad"),
("Steak & Wors & All Salad","Pap","Steak, wors & all salad",110,"Steak,Wors,Salad"),
("Steak, Wors & Chicken & All Salad","Pap","Steak, wors, chicken & all salad",150,"Steak,Wors,Chicken,Salad"),
("Beef Stew & All Salad","Rice","Beef stew with all salad",50,"Beef Stew,Salad"),
("1/4 Grilled Chicken & All Salad","Rice","Quarter grilled chicken with all salad",40,"Chicken,Salad"),
("1/5 Grilled Chicken & All Salad","Rice","One-fifth grilled chicken with all salad",60,"Chicken,Salad"),
("Full Grilled Chicken & All Salad","Rice","Full grilled chicken with all salad",120,"Chicken,Salad"),
("Steak & All Salad","Rice","Steak with all salad",70,"Steak,Salad"),
("Ice Cream Cone","Ice Cream","Ice cream cone",9,"Ice Cream"),
("Ice Cream Cup","Ice Cream","Ice cream cup",11,"Ice Cream")
]

def db():
    con = sqlite3.connect(DB_PATH)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys=ON")
    return con

def init_db():
    con=db()
    con.executescript("""
    CREATE TABLE IF NOT EXISTS products(
      id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, category TEXT NOT NULL,
      description TEXT, price REAL NOT NULL, options TEXT DEFAULT '', image TEXT DEFAULT '',
      active INTEGER DEFAULT 1, created_at TEXT DEFAULT CURRENT_TIMESTAMP
    );
    CREATE TABLE IF NOT EXISTS orders(
      id INTEGER PRIMARY KEY AUTOINCREMENT, order_no TEXT UNIQUE NOT NULL, customer_name TEXT NOT NULL,
      phone TEXT NOT NULL, notes TEXT DEFAULT '', total REAL NOT NULL, payment_method TEXT NOT NULL,
      payment_status TEXT DEFAULT 'Pending', status TEXT DEFAULT 'Preparing',
      created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
      yoco_checkout_id TEXT DEFAULT '', yoco_payment_id TEXT DEFAULT ''
    );
    CREATE TABLE IF NOT EXISTS order_items(
      id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER NOT NULL, product_id INTEGER,
      name TEXT NOT NULL, price REAL NOT NULL, quantity INTEGER NOT NULL,
      additions TEXT DEFAULT '', removals TEXT DEFAULT '', FOREIGN KEY(order_id) REFERENCES orders(id) ON DELETE CASCADE
    );
    CREATE TABLE IF NOT EXISTS settings(
      key TEXT PRIMARY KEY, value TEXT
    );
    """)
    # Safe migrations for databases created by earlier versions.
    for col, ddl in [("yoco_checkout_id", "TEXT DEFAULT ''"), ("yoco_payment_id", "TEXT DEFAULT ''")]:
        try:
            con.execute(f"ALTER TABLE orders ADD COLUMN {col} {ddl}")
        except sqlite3.OperationalError:
            pass
    count=con.execute("SELECT COUNT(*) c FROM products").fetchone()["c"]
    if count==0:
        con.executemany("INSERT INTO products(name,category,description,price,options) VALUES(?,?,?,?,?)", DEFAULT_PRODUCTS)
    defaults={
      "site_name":"ELROI FAST FOOD","whatsapp":"+27643981061","maintenance":"0",
      "maintenance_message":"We are temporarily closed for maintenance. Please check back soon.",
      "card_payment_link":"","card_instructions":"Pay securely on the Yoco-hosted card checkout. Never send card details by WhatsApp.",
      "yoco_secret_key":"","yoco_webhook_secret":"","yoco_webhook_id":"",
      "delivery_status":"Coming Soon","pickup_address":"Local collection point — address can be updated by admin."
    }
    for k,v in defaults.items():
        con.execute("INSERT OR IGNORE INTO settings(key,value) VALUES(?,?)",(k,v))
    con.commit(); con.close()

init_db()

def setting(k, default=""):
    con=db(); row=con.execute("SELECT value FROM settings WHERE key=?",(k,)).fetchone(); con.close()
    return row["value"] if row else default

@app.context_processor
def inject():
    return {"site_name":setting("site_name","ELROI FAST FOOD"), "whatsapp":setting("whatsapp","+27643981061")}

@app.before_request
def maintenance_guard():
    public_allowed = request.endpoint in {"home","static","health","customer_login","customer_dashboard","order_lookup","favicon"}
    if setting("maintenance","0")=="1" and not session.get("creator") and not session.get("admin") and not public_allowed:
        return render_template("maintenance.html", message=setting("maintenance_message")), 503

@app.get("/health")
def health(): return "OK", 200

def admin_required(f):
    @wraps(f)
    def w(*a,**kw):
        if not session.get("admin"):
            return redirect(url_for("admin_login", next=request.path))
        return f(*a,**kw)
    return w

def creator_required(f):
    @wraps(f)
    def w(*a,**kw):
        if not session.get("creator"):
            return redirect(url_for("creator_login", next=request.path))
        return f(*a,**kw)
    return w

def new_order_no():
    while True:
        code="ELR-"+''.join(secrets.choice(string.ascii_uppercase+string.digits) for _ in range(6))
        con=db(); exists=con.execute("SELECT 1 FROM orders WHERE order_no=?",(code,)).fetchone(); con.close()
        if not exists: return code

@app.route("/")
def home():
    con=db(); cats=con.execute("SELECT DISTINCT category FROM products WHERE active=1 ORDER BY id").fetchall(); con.close()
    return render_template("index.html", categories=cats, delivery_status=setting("delivery_status"))

@app.get("/menu")
def menu():
    con=db(); products=con.execute("SELECT * FROM products WHERE active=1 ORDER BY id").fetchall(); con.close()
    return render_template("menu.html", products=products)

@app.get("/product/<int:pid>")
def product(pid):
    con=db(); p=con.execute("SELECT * FROM products WHERE id=? AND active=1",(pid,)).fetchone(); con.close()
    if not p: return "Product not found",404
    return render_template("product.html", p=p)

@app.get("/checkout")
def checkout():
    yoco_connected=bool(setting("yoco_secret_key"))
    return render_template("checkout.html", card_link=setting("card_payment_link"), card_instructions=setting("card_instructions"), pickup=setting("pickup_address"), yoco_connected=yoco_connected)

@app.post("/api/order")
def create_order():
    data=request.get_json(silent=True) or {}
    items=data.get("items",[])
    if not items: return jsonify(error="Your cart is empty."),400
    name=(data.get("name") or "").strip(); phone=(data.get("phone") or "").strip()
    payment=data.get("payment") or "cash"
    if payment not in {"cash","card"}: return jsonify(error="Invalid payment method."),400
    if not name or not phone: return jsonify(error="Name and phone are required."),400
    con=db(); total=0; validated=[]
    for item in items:
        try: pid=int(item["id"]); qty=max(1,min(50,int(item.get("quantity",1))))
        except: continue
        p=con.execute("SELECT * FROM products WHERE id=? AND active=1",(pid,)).fetchone()
        if not p: continue
        additions=", ".join(item.get("additions",[]) or [])
        removals=", ".join(item.get("removals",[]) or [])
        total += float(p["price"])*qty
        validated.append((p,qty,additions,removals))
    if not validated: con.close(); return jsonify(error="No valid products found."),400
    order_no=new_order_no()
    cur=con.execute("""INSERT INTO orders(order_no,customer_name,phone,notes,total,payment_method,payment_status,status)
                       VALUES(?,?,?,?,?,?,?,?)""",(order_no,name,phone,data.get("notes",""),total,payment,"Pending","Preparing"))
    oid=cur.lastrowid
    for p,qty,adds,rems in validated:
        con.execute("""INSERT INTO order_items(order_id,product_id,name,price,quantity,additions,removals)
                       VALUES(?,?,?,?,?,?,?)""",(oid,p["id"],p["name"],p["price"],qty,adds,rems))
    con.commit(); con.close()

    if payment == "card":
        secret=setting("yoco_secret_key")
        if not secret:
            con=db(); con.execute("DELETE FROM orders WHERE id=?",(oid,)); con.commit(); con.close()
            return jsonify(error="Online card payment is not connected yet. The admin must connect Yoco in Admin → Settings."),400
        try:
            base=request.url_root.rstrip("/")
            payload={
                "amount": int(round(total*100)),
                "currency":"ZAR",
                "successUrl": f"{base}/payment/yoco/success?order={order_no}",
                "cancelUrl": f"{base}/payment/yoco/cancel?order={order_no}",
                "failureUrl": f"{base}/payment/yoco/failure?order={order_no}",
                "metadata":{"orderNo":order_no,"orderId":str(oid)}
            }
            r=requests.post("https://payments.yoco.com/api/checkouts", json=payload, headers={"Authorization":f"Bearer {secret}","Content-Type":"application/json"}, timeout=20)
            body=r.json() if r.content else {}
            if r.status_code >= 400 or not body.get("redirectUrl"):
                raise RuntimeError(body.get("message") or body.get("error") or f"Yoco HTTP {r.status_code}")
            checkout_id=body.get("id") or body.get("checkoutId") or ""
            con=db(); con.execute("UPDATE orders SET yoco_checkout_id=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",(checkout_id,oid)); con.commit(); con.close()
            return jsonify(order_no=order_no,total=total,status="Preparing",payment="card",redirect_url=body["redirectUrl"])
        except Exception as e:
            con=db(); con.execute("UPDATE orders SET payment_status='Payment Setup Failed',updated_at=CURRENT_TIMESTAMP WHERE id=?",(oid,)); con.commit(); con.close()
            return jsonify(error=f"Could not start secure card payment: {e}"),502

    return jsonify(order_no=order_no, total=total, status="Preparing", payment="cash")

@app.get("/payment/yoco/success")
def yoco_success():
    order_no=request.args.get("order","").upper()
    return redirect(url_for("order_lookup", order_no=order_no))

@app.get("/payment/yoco/cancel")
def yoco_cancel():
    order_no=request.args.get("order","").upper()
    return redirect(url_for("order_lookup", order_no=order_no))

@app.get("/payment/yoco/failure")
def yoco_failure():
    order_no=request.args.get("order","").upper()
    return redirect(url_for("order_lookup", order_no=order_no))

@app.post("/api/webhooks/yoco")
def yoco_webhook():
    secret=setting("yoco_webhook_secret")
    if not secret:
        return "Webhook secret not configured",503
    raw=request.get_data(as_text=True)
    webhook_id=request.headers.get("webhook-id")
    timestamp=request.headers.get("webhook-timestamp")
    signature_header=request.headers.get("webhook-signature","")
    if not webhook_id or not timestamp or not signature_header:
        return "Missing webhook headers",400
    try:
        if abs(time.time()-int(timestamp)) > 180:
            return "Expired webhook",403
        secret_bytes=base64.b64decode(secret.split("_",1)[1])
        signed_content=f"{webhook_id}.{timestamp}.{raw}"
        expected=base64.b64encode(hmac.new(secret_bytes,signed_content.encode(),hashlib.sha256).digest()).decode()
        signatures=[]
        for part in signature_header.split(" "):
            if "," in part:
                version,value=part.split(",",1)
                if version == "v1": signatures.append(value)
        if not any(hmac.compare_digest(value,expected) for value in signatures):
            return "Invalid signature",403
    except Exception:
        return "Invalid webhook",403
    try:
        event=json.loads(raw)
        event_type=event.get("type","")
        payload=event.get("payload") or event.get("data") or {}
        metadata=payload.get("metadata") or {}
        order_no=(metadata.get("orderNo") or metadata.get("order_no") or "").upper()
        checkout_id=metadata.get("checkoutId") or metadata.get("checkout_id") or payload.get("checkoutId") or payload.get("checkout_id") or ""
        payment_id=payload.get("id") or payload.get("paymentId") or ""
        con=db()
        if order_no:
            o=con.execute("SELECT id FROM orders WHERE order_no=?",(order_no,)).fetchone()
        elif checkout_id:
            o=con.execute("SELECT id FROM orders WHERE yoco_checkout_id=?",(checkout_id,)).fetchone()
        else:
            o=None
        if o:
            if event_type == "payment.succeeded":
                con.execute("UPDATE orders SET payment_status='Paid', yoco_payment_id=?, updated_at=CURRENT_TIMESTAMP WHERE id=?",(payment_id,o["id"]))
            elif event_type in {"payment.failed","payment.cancelled"}:
                con.execute("UPDATE orders SET payment_status='Failed', updated_at=CURRENT_TIMESTAMP WHERE id=?",(o["id"],))
            elif event_type == "refund.succeeded":
                con.execute("UPDATE orders SET payment_status='Refunded', updated_at=CURRENT_TIMESTAMP WHERE id=?",(o["id"],))
            con.commit()
        con.close()
    except Exception:
        return "",200
    return "",200

@app.get("/order/<order_no>")
def order_lookup(order_no):
    con=db(); o=con.execute("SELECT * FROM orders WHERE order_no=?",(order_no.upper(),)).fetchone()
    if not o: con.close(); return render_template("order_not_found.html"),404
    items=con.execute("SELECT * FROM order_items WHERE order_id=?",(o["id"],)).fetchall(); con.close()
    return render_template("order_status.html", order=o, items=items, card_link=setting("card_payment_link"), card_instructions=setting("card_instructions"), yoco_connected=bool(setting("yoco_secret_key")))

@app.route("/customer/login", methods=["GET","POST"])
def customer_login():
    if request.method=="POST":
        no=request.form.get("order_no","").strip().upper(); phone=request.form.get("phone","").strip()
        con=db(); o=con.execute("SELECT * FROM orders WHERE order_no=? AND phone=?",(no,phone)).fetchone(); con.close()
        if o:
            session["customer_order"]=no; return redirect(url_for("customer_dashboard"))
        flash("Order number and phone do not match.")
    return render_template("customer_login.html")

@app.get("/customer/dashboard")
def customer_dashboard():
    no=session.get("customer_order")
    if not no: return redirect(url_for("customer_login"))
    con=db(); o=con.execute("SELECT * FROM orders WHERE order_no=?",(no,)).fetchone()
    if not o: session.pop("customer_order",None); con.close(); return redirect(url_for("customer_login"))
    items=con.execute("SELECT * FROM order_items WHERE order_id=?",(o["id"],)).fetchall(); con.close()
    return render_template("customer_dashboard.html", order=o, items=items)

@app.get("/admin/login")
def admin_login():
    return render_template("admin_login.html", role="admin")

@app.post("/admin/login")
def admin_login_post():
    password=request.form.get("password","")
    if secrets.compare_digest(password, os.environ.get("ADMIN_PASSWORD","admin123")):
        session["admin"]=True; return redirect(request.args.get("next") or url_for("admin_dashboard"))
    flash("Invalid admin password."); return redirect(url_for("admin_login"))

@app.get("/admin/logout")
def admin_logout(): session.pop("admin",None); return redirect(url_for("home"))

@app.get("/admin")
@admin_required
def admin_dashboard():
    con=db()
    stats={
      "products":con.execute("SELECT COUNT(*) c FROM products WHERE active=1").fetchone()["c"],
      "orders":con.execute("SELECT COUNT(*) c FROM orders").fetchone()["c"],
      "pending":con.execute("SELECT COUNT(*) c FROM orders WHERE status!='Collect Now'").fetchone()["c"],
      "sales":con.execute("SELECT COALESCE(SUM(total),0) s FROM orders WHERE payment_status='Paid'").fetchone()["s"]
    }
    orders=con.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 50").fetchall()
    products=con.execute("SELECT * FROM products ORDER BY id DESC").fetchall(); con.close()
    return render_template("admin.html",stats=stats,orders=orders,products=products)

@app.post("/admin/order/<int:oid>/status")
@admin_required
def update_status(oid):
    status=request.form.get("status","Preparing")
    allowed={"Preparing","Almost Done","Collect Now","Completed","Cancelled"}
    if status not in allowed: return redirect(url_for("admin_dashboard"))
    con=db(); con.execute("UPDATE orders SET status=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",(status,oid)); con.commit(); con.close()
    return redirect(url_for("admin_dashboard"))

@app.post("/admin/order/<int:oid>/payment")
@admin_required
def update_payment(oid):
    pay=request.form.get("payment_status","Pending")
    con=db(); con.execute("UPDATE orders SET payment_status=?,updated_at=CURRENT_TIMESTAMP WHERE id=?",(pay,oid)); con.commit(); con.close()
    return redirect(url_for("admin_dashboard"))

@app.route("/admin/products/new", methods=["GET","POST"])
@admin_required
def product_new():
    if request.method=="POST":
        name=request.form["name"]; cat=request.form["category"]; desc=request.form.get("description","")
        price=float(request.form["price"]); options=request.form.get("options","")
        image=""
        f=request.files.get("image")
        if f and f.filename:
            ext=f.filename.rsplit(".",1)[-1].lower()
            if ext in ALLOWED_EXTENSIONS:
                image=secure_filename(f.filename); f.save(os.path.join(UPLOAD_DIR,image))
        con=db(); con.execute("INSERT INTO products(name,category,description,price,options,image) VALUES(?,?,?,?,?,?)",(name,cat,desc,price,options,image)); con.commit(); con.close()
        return redirect(url_for("admin_dashboard"))
    return render_template("product_form.html",p=None)

@app.route("/admin/products/<int:pid>/edit", methods=["GET","POST"])
@admin_required
def product_edit(pid):
    con=db(); p=con.execute("SELECT * FROM products WHERE id=?",(pid,)).fetchone()
    if not p: con.close(); return "Not found",404
    if request.method=="POST":
        image=p["image"]; f=request.files.get("image")
        if f and f.filename:
            ext=f.filename.rsplit(".",1)[-1].lower()
            if ext in ALLOWED_EXTENSIONS:
                image=secure_filename(f.filename); f.save(os.path.join(UPLOAD_DIR,image))
        con.execute("""UPDATE products SET name=?,category=?,description=?,price=?,options=?,image=?,active=? WHERE id=?""",
                    (request.form["name"],request.form["category"],request.form.get("description",""),float(request.form["price"]),request.form.get("options",""),image,1 if request.form.get("active") else 0,pid))
        con.commit(); con.close(); return redirect(url_for("admin_dashboard"))
    con.close(); return render_template("product_form.html",p=p)

@app.post("/admin/products/<int:pid>/delete")
@admin_required
def product_delete(pid):
    con=db(); con.execute("UPDATE products SET active=0 WHERE id=?",(pid,)); con.commit(); con.close(); return redirect(url_for("admin_dashboard"))

@app.get("/admin/scan")
@admin_required
def scanner(): return render_template("scanner.html")

@app.get("/admin/settings")
@admin_required
def admin_settings():
    keys=["site_name","whatsapp","card_payment_link","card_instructions","delivery_status","pickup_address","yoco_secret_key","yoco_webhook_secret","yoco_webhook_id"]
    return render_template("settings.html", settings={k:setting(k) for k in keys}, yoco_connected=bool(setting("yoco_secret_key")), webhook_connected=bool(setting("yoco_webhook_secret")))

@app.post("/admin/settings")
@admin_required
def save_settings():
    fields=["site_name","whatsapp","card_payment_link","card_instructions","delivery_status","pickup_address"]
    con=db()
    for k in fields: con.execute("INSERT OR REPLACE INTO settings(key,value) VALUES(?,?)",(k,request.form.get(k,"" ).strip()))
    yoco_secret=request.form.get("yoco_secret_key","").strip()
    if yoco_secret:
        con.execute("INSERT OR REPLACE INTO settings(key,value) VALUES('yoco_secret_key',?)",(yoco_secret,))
    con.commit(); con.close(); return redirect(url_for("admin_settings"))

@app.post("/admin/yoco/connect")
@admin_required
def connect_yoco():
    secret=request.form.get("yoco_secret_key","").strip() or setting("yoco_secret_key")
    if not secret:
        flash("Enter your Yoco Secret API Key first.")
        return redirect(url_for("admin_settings"))
    base=request.url_root.rstrip("/")
    webhook_url=f"{base}/api/webhooks/yoco"
    try:
        # Save the merchant key first so the connection can be reused.
        con=db(); con.execute("INSERT OR REPLACE INTO settings(key,value) VALUES('yoco_secret_key',?)",(secret,)); con.commit(); con.close()
        r=requests.post("https://payments.yoco.com/api/webhooks",json={"name":"Elroi Fast Food Payments","url":webhook_url},headers={"Authorization":f"Bearer {secret}","Content-Type":"application/json"},timeout=20)
        body=r.json() if r.content else {}
        if r.status_code >= 400:
            raise RuntimeError(body.get("message") or body.get("error") or f"Yoco HTTP {r.status_code}")
        con=db()
        con.execute("INSERT OR REPLACE INTO settings(key,value) VALUES('yoco_webhook_secret',?)",(body.get("secret", ""),))
        con.execute("INSERT OR REPLACE INTO settings(key,value) VALUES('yoco_webhook_id',?)",(body.get("id", ""),))
        con.commit(); con.close()
        flash("Yoco is connected. Secure card checkout and payment confirmation are enabled.")
    except Exception as e:
        flash(f"Could not connect Yoco: {e}")
    return redirect(url_for("admin_settings"))

@app.get("/creator/login")
def creator_login(): return render_template("admin_login.html", role="creator")

@app.post("/creator/login")
def creator_login_post():
    password=request.form.get("password","")
    if secrets.compare_digest(password, os.environ.get("CREATOR_PASSWORD","creator123")):
        session["creator"]=True; return redirect(url_for("creator_dashboard"))
    flash("Invalid creator password."); return redirect(url_for("creator_login"))

@app.get("/creator/logout")
def creator_logout(): session.pop("creator",None); return redirect(url_for("home"))

@app.get("/creator")
@creator_required
def creator_dashboard():
    return render_template("creator.html", maintenance=setting("maintenance")=="1")

@app.post("/creator/maintenance")
@creator_required
def creator_maintenance():
    val="1" if request.form.get("maintenance")=="on" else "0"
    con=db(); con.execute("INSERT OR REPLACE INTO settings(key,value) VALUES('maintenance',?)",(val,)); con.commit(); con.close()
    return redirect(url_for("creator_dashboard"))

@app.post("/creator/message")
@creator_required
def creator_message():
    con=db(); con.execute("INSERT OR REPLACE INTO settings(key,value) VALUES('maintenance_message',?)",(request.form.get("message",""),)); con.commit(); con.close()
    return redirect(url_for("creator_dashboard"))

@app.get("/api/order/<order_no>")
def order_api(order_no):
    con=db(); o=con.execute("SELECT order_no,status,payment_status,total,updated_at FROM orders WHERE order_no=?",(order_no.upper(),)).fetchone(); con.close()
    if not o: return jsonify(error="Order not found"),404
    return jsonify(dict(o))

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",5000)), debug=False)
