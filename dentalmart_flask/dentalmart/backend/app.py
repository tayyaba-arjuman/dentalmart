"""
DentalMart — app.py
====================
Flask backend with MongoDB.

Folder layout expected:
  backend/
  ├── app.py
  ├── templates/   ← all HTML files
  └── static/
      ├── css/style.css
      ├── js/script.js
      └── images/

Run locally:
  cd backend
  pip install -r requirements.txt
  python app.py

Deploy on Render:
  Build command : pip install -r requirements.txt
  Start command : gunicorn app:app
"""

import os
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, redirect, url_for,
    request, session, jsonify, flash
)
from flask_pymongo import PyMongo
from werkzeug.security import generate_password_hash, check_password_hash
from bson import ObjectId

# ── App setup ────────────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dentalmart-dev-secret-change-in-prod")

# ── MongoDB ──────────────────────────────────────────────────────────────────
# Set MONGO_URI as an environment variable on Render.
# Local default: mongodb://localhost:27017/dentalmart
app.config["MONGO_URI"] = "mongodb+srv://tayyabaarjuman_db_user:ojaJEykxXvOjwXzJ@cluster0.pjzig1i.mongodb.net/dentalmart?retryWrites=true&w=majority&appName=Cluster0"
mongo = PyMongo(app)

# ── Admin credentials (set via env vars on Render) ───────────────────────────
ADMIN_EMAIL    = os.environ.get("ADMIN_EMAIL",    "admin@dentalmart.in")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "admin123")

# ── Seed products if collection is empty ─────────────────────────────────────
SEED_PRODUCTS = [
    {"id": 1,  "name": "Dental Mirror",           "category": "Examination",    "price": 250,  "badge": "Best Seller", "badge_type": "",       "image": "dental-mirror.jpg",      "desc": "Stainless steel #5 mouth mirror with front-surface reflection. Essential for intraoral examination."},
    {"id": 2,  "name": "Dental Explorer",          "category": "Examination",    "price": 300,  "badge": "Popular",     "badge_type": "",       "image": "dental-explorer.jpg",    "desc": "Curved 5/23 explorer for caries detection and cavity depth measurement."},
    {"id": 3,  "name": "Extraction Forceps",       "category": "Extraction",     "price": 1200, "badge": "New",         "badge_type": "new",    "image": "forceps.jpg",            "desc": "German steel upper molar extraction forceps. Autoclavable, mirror finish."},
    {"id": 4,  "name": "Sickle Scaler",            "category": "Periodontics",   "price": 500,  "badge": "Sale",        "badge_type": "sale",   "image": "scaler.jpg",             "desc": "Manual sickle scaler with 204S tip for supragingival debridement."},
    {"id": 5,  "name": "Impression Tray",          "category": "Prosthodontics", "price": 350,  "badge": "",            "badge_type": "",       "image": "impression-tray.jpg",    "desc": "Full-arch perforated stainless steel impression tray. Set of 3 sizes (S/M/L)."},
    {"id": 6,  "name": "College Plier",            "category": "Examination",    "price": 180,  "badge": "",            "badge_type": "",       "image": "college-plier.jpg",      "desc": "Non-serrated cotton plier for cotton roll placement and small item transfer."},
    {"id": 7,  "name": "Spoon Excavator",          "category": "Restorative",    "price": 220,  "badge": "",            "badge_type": "",       "image": "excavator.jpg",          "desc": "Double-ended spoon excavator for caries removal. Available in sizes 14 and 17."},
    {"id": 8,  "name": "Composite Instrument Set", "category": "Restorative",    "price": 850,  "badge": "Bundle",      "badge_type": "bundle", "image": "composite-set.jpg",      "desc": "4-piece PTFE-coated composite placement kit. Non-stick surface."},
    {"id": 9,  "name": "Periodontal Probe",        "category": "Periodontics",   "price": 280,  "badge": "",            "badge_type": "",       "image": "perio-probe.jpg",        "desc": "Williams-style probe with 1–10 mm markings for pocket depth assessment."},
    {"id": 10, "name": "Cement Spatula",           "category": "Restorative",    "price": 160,  "badge": "",            "badge_type": "",       "image": "cement-spatula.jpg",     "desc": "Flexible steel spatula for mixing zinc oxide, GIC and other dental cements."},
    {"id": 11, "name": "Extraction Elevator",      "category": "Extraction",     "price": 420,  "badge": "",            "badge_type": "",       "image": "elevator.jpg",           "desc": "Coupland #1 elevator for tooth luxation prior to forceps extraction."},
    {"id": 12, "name": "Carbide Bur Kit",          "category": "Handpiece",      "price": 650,  "badge": "Popular",     "badge_type": "",       "image": "bur-kit.jpg",            "desc": "10-piece carbide bur set for cavity preparation. FG shank, multiple types."},
]

def seed_db():
    if mongo.db.products.count_documents({}) == 0:
        mongo.db.products.insert_many(SEED_PRODUCTS)
        print("✅  Products seeded into MongoDB.")

# ── Helpers ───────────────────────────────────────────────────────────────────
def doc(d):
    """Make a MongoDB doc JSON-serialisable."""
    d = dict(d)
    d.pop("_id", None)
    return d

def current_user():
    email = session.get("user_email")
    if not email:
        return None
    return mongo.db.users.find_one({"email": email}, {"_id": 0, "password": 0})

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("user_email"):
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login_page"))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("is_admin"):
            return redirect(url_for("admin_login"))
        return f(*args, **kwargs)
    return decorated

# ═══════════════════════════════════════════════════════════════════════════════
#  PAGE ROUTES  (render HTML templates)
# ═══════════════════════════════════════════════════════════════════════════════

@app.route("/")
def index():
    featured = list(mongo.db.products.find(
        {"badge": {"$ne": ""}}, {"_id": 0}
    ).limit(4))
    user = current_user()
    return render_template("index.html", featured=featured, user=user)


@app.route("/catalog")
def catalog():
    category = request.args.get("cat", "")
    search   = request.args.get("search", "")
    query    = {}
    if category and category != "All":
        query["category"] = category
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
    products   = list(mongo.db.products.find(query, {"_id": 0}))
    categories = mongo.db.products.distinct("category")
    user       = current_user()
    return render_template(
        "catalog.html",
        products=products,
        categories=["All"] + sorted(categories),
        active_cat=category or "All",
        search=search,
        user=user,
    )


@app.route("/cart")
@login_required
def cart():
    user = current_user()
    return render_template("cart.html", user=user)


@app.route("/login", methods=["GET"])
def login_page():
    if session.get("user_email"):
        return redirect(url_for("index"))
    tab = request.args.get("tab", "login")
    return render_template("login.html", tab=tab)


@app.route("/payment")
@login_required
def payment():
    user = current_user()
    return render_template("payment.html", user=user)


# ── Admin pages ───────────────────────────────────────────────────────────────
@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "")
        if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
            session["is_admin"]    = True
            session["admin_email"] = email
            return redirect(url_for("admin_dashboard"))
        flash("Invalid admin credentials.", "danger")
    return render_template("admin.html", view="login")


@app.route("/admin")
@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    # Summary stats
    total_users    = mongo.db.users.count_documents({})
    total_orders   = mongo.db.orders.count_documents({})
    total_products = mongo.db.products.count_documents({})
    revenue        = sum(
        o.get("total", 0)
        for o in mongo.db.orders.find({}, {"total": 1, "_id": 0})
    )

    recent_orders = [
        doc(o) for o in mongo.db.orders.find(
            {}, {"_id": 0}
        ).sort("created_at", -1).limit(10)
    ]
    all_users = [
        doc(u) for u in mongo.db.users.find(
            {}, {"_id": 0, "password": 0}
        ).sort("created_at", -1).limit(20)
    ]
    all_products = list(mongo.db.products.find({}, {"_id": 0}))

    return render_template(
        "admin.html",
        view="dashboard",
        stats={
            "users":    total_users,
            "orders":   total_orders,
            "products": total_products,
            "revenue":  revenue,
        },
        recent_orders=recent_orders,
        all_users=all_users,
        all_products=all_products,
    )


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    session.pop("admin_email", None)
    return redirect(url_for("admin_login"))


# ═══════════════════════════════════════════════════════════════════════════════
#  API ROUTES  (JSON responses for frontend JS)
# ═══════════════════════════════════════════════════════════════════════════════

# ── Auth API ──────────────────────────────────────────────────────────────────
@app.route("/api/auth/register", methods=["POST"])
def api_register():
    data     = request.get_json() or {}
    name     = data.get("name",     "").strip()
    email    = data.get("email",    "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({"success": False, "message": "All fields are required."}), 400
    if len(password) < 6:
        return jsonify({"success": False, "message": "Password must be at least 6 characters."}), 400
    if mongo.db.users.find_one({"email": email}):
        return jsonify({"success": False, "message": "Email already registered."}), 409

    mongo.db.users.insert_one({
        "name":       name,
        "email":      email,
        "password":   generate_password_hash(password),
        "created_at": datetime.utcnow().isoformat(),
    })
    return jsonify({"success": True, "message": "Account created successfully."}), 201


@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data     = request.get_json() or {}
    email    = data.get("email",    "").strip().lower()
    password = data.get("password", "")

    user = mongo.db.users.find_one({"email": email})
    if not user or not check_password_hash(user["password"], password):
        return jsonify({"success": False, "message": "Invalid email or password."}), 401

    session["user_email"] = email
    return jsonify({
        "success": True,
        "user": {"name": user["name"], "email": user["email"]},
    })


@app.route("/api/auth/logout", methods=["POST"])
def api_logout():
    session.pop("user_email", None)
    return jsonify({"success": True, "message": "Logged out."})


@app.route("/api/auth/me")
def api_me():
    user = current_user()
    if not user:
        return jsonify({"success": False, "message": "Not logged in."}), 401
    return jsonify({"success": True, "user": user})


# ── Products API ──────────────────────────────────────────────────────────────
@app.route("/api/products")
def api_products():
    category = request.args.get("category", "")
    search   = request.args.get("search",   "")
    query    = {}
    if category and category != "All":
        query["category"] = category
    if search:
        query["name"] = {"$regex": search, "$options": "i"}
    products = [doc(p) for p in mongo.db.products.find(query, {"_id": 0})]
    return jsonify({"success": True, "products": products})


@app.route("/api/products/<int:product_id>")
def api_product(product_id):
    p = mongo.db.products.find_one({"id": product_id}, {"_id": 0})
    if not p:
        return jsonify({"success": False, "message": "Product not found."}), 404
    return jsonify({"success": True, "product": doc(p)})


# ── Orders API ────────────────────────────────────────────────────────────────
@app.route("/api/orders", methods=["POST"])
@login_required
def api_place_order():
    data  = request.get_json() or {}
    user  = current_user()
    order = {
        "order_id":   "DM" + str(int(datetime.utcnow().timestamp()))[-8:],
        "user_email": user["email"],
        "user_name":  user["name"],
        "items":      data.get("items",      []),
        "address":    data.get("address",    {}),
        "pay_method": data.get("pay_method", "cod"),
        "subtotal":   data.get("subtotal",   0),
        "shipping":   data.get("shipping",   0),
        "discount":   data.get("discount",   0),
        "total":      data.get("total",      0),
        "status":     "confirmed",
        "created_at": datetime.utcnow().isoformat(),
    }
    mongo.db.orders.insert_one(order)
    return jsonify({"success": True, "order_id": order["order_id"]}), 201


@app.route("/api/orders/my")
@login_required
def api_my_orders():
    user   = current_user()
    orders = [doc(o) for o in mongo.db.orders.find(
        {"user_email": user["email"]}, {"_id": 0}
    ).sort("created_at", -1)]
    return jsonify({"success": True, "orders": orders})


# ── Admin API (product management) ───────────────────────────────────────────
@app.route("/api/admin/products", methods=["POST"])
@admin_required
def api_admin_add_product():
    data = request.get_json() or {}
    last = mongo.db.products.find_one(sort=[("id", -1)])
    new_id = (last["id"] + 1) if last else 1
    data["id"] = new_id
    mongo.db.products.insert_one(data)
    return jsonify({"success": True, "id": new_id}), 201


@app.route("/api/admin/products/<int:product_id>", methods=["PUT"])
@admin_required
def api_admin_update_product(product_id):
    data = request.get_json() or {}
    data.pop("id", None)
    mongo.db.products.update_one({"id": product_id}, {"$set": data})
    return jsonify({"success": True})


@app.route("/api/admin/products/<int:product_id>", methods=["DELETE"])
@admin_required
def api_admin_delete_product(product_id):
    mongo.db.products.delete_one({"id": product_id})
    return jsonify({"success": True})


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    with app.app_context():
        seed_db()
    print("\n🦷  DentalMart running → http://127.0.0.1:5000\n")
    app.run(debug=True, port=5000)
