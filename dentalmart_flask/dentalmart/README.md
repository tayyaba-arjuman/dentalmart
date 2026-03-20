# 🦷 DentalMart – Flask Project

## 📁 Folder Structure

```
backend/
├── app.py                          ← Flask app, all routes, MongoDB
├── requirements.txt                ← Python dependencies
├── render.yaml                     ← Render deployment config
│
├── templates/
│   ├── base.html                   ← Shared navbar, footer, scripts
│   ├── index.html                  ← Homepage
│   ├── catalog.html                ← Product catalog
│   ├── cart.html                   ← Shopping cart
│   ├── login.html                  ← Login & Register
│   ├── payment.html                ← Checkout & payment
│   └── admin.html                  ← Admin dashboard
│
└── static/
    ├── css/
    │   └── style.css               ← All styles
    ├── js/
    │   └── script.js               ← Shared JS (cart, API, UI)
    └── images/
        ├── placeholder.jpg         ← Fallback image
        ├── dental-mirror.jpg
        └── ... (your product images)
```

---

## ⚡ Run Locally in VS Code

### Step 1 — Open the project
Open the `backend/` folder in VS Code.

### Step 2 — Create a virtual environment
```bash
cd backend
python -m venv venv

# Activate:
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### Step 3 — Install dependencies
```bash
pip install -r requirements.txt
```

### Step 4 — Start MongoDB
```bash
# macOS/Linux:
mongod --dbpath /data/db

# Windows (run as Administrator):
"C:\Program Files\MongoDB\Server\7.0\bin\mongod.exe" --dbpath "C:\data\db"
```

### Step 5 — Run Flask
```bash
python app.py
```

Open **http://127.0.0.1:5000** in your browser.

---

## 🔐 Admin Panel

URL: **http://127.0.0.1:5000/admin**

Default credentials (change via environment variables):
- Email: `admin@dentalmart.in`
- Password: `admin123`

The admin panel shows:
- 📊 Overview — stats (users, orders, revenue, products)
- 📦 Orders — all customer orders with details
- 🛠️ Products — full product list with images
- 👤 Users — all registered users

---

## 🖼️ Adding Product Images

1. Drop your image files into `backend/static/images/`
2. Name them exactly as listed in `static/images/README.txt`
3. If an image is missing, `placeholder.jpg` is shown automatically

---

## 🚀 Deploy on Render

1. Push your `backend/` folder to a GitHub repo
2. Create a new **Web Service** on [render.com](https://render.com)
3. Set:
   - **Build command**: `pip install -r requirements.txt`
   - **Start command**: `gunicorn app:app`
4. Add environment variables in Render dashboard:
   - `MONGO_URI` → your MongoDB Atlas connection string
   - `SECRET_KEY` → any long random string
   - `ADMIN_EMAIL` → your admin email
   - `ADMIN_PASSWORD` → your admin password

### MongoDB Atlas (free cloud DB for Render):
1. Go to [mongodb.com/atlas](https://mongodb.com/atlas) → create free cluster
2. Create a database user
3. Whitelist all IPs: `0.0.0.0/0`
4. Copy the connection string → paste as `MONGO_URI` in Render

---

## 📋 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET    | `/api/products` | All products |
| GET    | `/api/products?category=X` | Filter by category |
| GET    | `/api/products?search=term` | Search products |
| POST   | `/api/auth/register` | Register user |
| POST   | `/api/auth/login` | Login |
| POST   | `/api/auth/logout` | Logout |
| GET    | `/api/auth/me` | Current user info |
| POST   | `/api/orders` | Place order |
| GET    | `/api/orders/my` | My orders |

---

## ✏️ Change Prices or Products

Open `app.py` and find `SEED_PRODUCTS` near the top.
Edit the `price`, `name`, `desc`, `badge`, or `image` fields.

> Note: Seed only runs if the products collection is empty.
> To re-seed: drop the `products` collection in MongoDB Compass, then restart Flask.

---

*© 2025 DentalMart*
