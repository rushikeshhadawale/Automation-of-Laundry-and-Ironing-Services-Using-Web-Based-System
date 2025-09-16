# app.py
import os
import datetime
from flask import (
    Flask, request, jsonify, session,
    render_template, render_template_string, redirect, url_for, flash
)
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_cors import CORS

# -----------------------------------------------------------------------------
# App & Config
# -----------------------------------------------------------------------------
# static_url_path='/' makes /script.js resolve to static/script.js (fixes 404)
app = Flask(__name__, static_folder="static", static_url_path="/")
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "supersecretkey_for_sessions")

# ---- MySQL (adjust user/password if needed) ----
# Existing DB from your screenshot: `laundrypro`
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv(
    "DATABASE_URL",
    "mysql+pymysql://root:root@localhost/laundrypro"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
CORS(app, supports_credentials=True)

# ---- Simple admin (env overridable) ----
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@laundrypro.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")  # demo only

# -----------------------------------------------------------------------------
# Models (match your existing tables)
# -----------------------------------------------------------------------------
class User(db.Model):
    __tablename__ = "user"  # matches your table name
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(100), nullable=False)
    email    = db.Column(db.String(120), unique=True, nullable=False)
    phone    = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(200), nullable=False)  # bcrypt hash


class Booking(db.Model):
    __tablename__ = "booking"  # matches your table name
    id              = db.Column(db.Integer, primary_key=True)
    user_id         = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    service_type    = db.Column(db.String(50), nullable=False)          # 'laundry' / 'ironing' / 'dry-cleaning'
    items           = db.Column(db.Integer, nullable=False)
    express_service = db.Column(db.Boolean, default=False)
    pickup_date     = db.Column(db.Date, nullable=False)
    pickup_time     = db.Column(db.Time, nullable=False)
    address         = db.Column(db.String(255), nullable=False)
    phone           = db.Column(db.String(20), nullable=False)
    payment_method  = db.Column(db.String(50), nullable=False)          # 'cash' / 'upi' / 'card'
    status          = db.Column(db.String(50), default="PICKED_UP")     # 'PICKED_UP'...'DELIVERED'

    def to_dict(self):
        return {
            "orderId": self.id,
            "serviceType": self.service_type,
            "items": self.items,
            "expressService": bool(self.express_service),
            "pickupDate": self.pickup_date.strftime("%Y-%m-%d"),
            "pickupTime": self.pickup_time.strftime("%H:%M"),
            "address": self.address,
            "phone": self.phone,
            "paymentMethod": self.payment_method,
            "status": self.status,
        }

# -----------------------------------------------------------------------------
# Pages
# -----------------------------------------------------------------------------
@app.route("/")
def index():
    # templates/index.html → your provided HTML
    return render_template("index.html")

# -----------------------------------------------------------------------------
# Auth API (used by script.js)
# -----------------------------------------------------------------------------
@app.route("/api/auth/register", methods=["POST"])
def api_register():
    data = request.get_json(silent=True) or {}
    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    phone = (data.get("phone") or "").strip()
    password = data.get("password") or ""

    if not all([name, email, phone, password]):
        return jsonify({"message": "All fields are required"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email already exists"}), 400

    pw_hash = bcrypt.generate_password_hash(password).decode("utf-8")
    user = User(name=name, email=email, phone=phone, password=pw_hash)
    db.session.add(user)
    db.session.commit()

    session["user_id"] = user.id  # auto-login
    return jsonify({"message": "User registered successfully",
                    "user": {"id": user.id, "name": user.name}}), 201


@app.route("/api/auth/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    user = User.query.filter_by(email=email).first()
    if not user or not bcrypt.check_password_hash(user.password, password):
        return jsonify({"message": "Invalid credentials"}), 401

    session["user_id"] = user.id
    return jsonify({"message": "Login successful",
                    "user": {"id": user.id, "name": user.name}}), 200


@app.route("/api/auth/logout", methods=["POST"])
def api_logout():
    session.pop("user_id", None)
    return jsonify({"message": "Logged out successfully"}), 200

# -----------------------------------------------------------------------------
# Bookings API (used by script.js)
# -----------------------------------------------------------------------------
@app.route("/api/bookings", methods=["POST"])
def create_booking():
    data = request.get_json(silent=True) or {}

    try:
        pickup_date = datetime.datetime.strptime(data.get("pickupDate"), "%Y-%m-%d").date()
        pickup_time = datetime.datetime.strptime(data.get("pickupTime"), "%H:%M").time()
        
    except Exception:
        return jsonify({"message": "Invalid pickup date or time"}), 400

    booking = Booking(
        user_id=session.get("user_id"),  # may be None for guest
        service_type=data.get("serviceType"),
        items=int(data.get("items") or 0),
        express_service=bool(data.get("expressService", False)),
        pickup_date=pickup_date,
        pickup_time=pickup_time,
        address=data.get("address"),
        phone=data.get("phone"),
        payment_method=data.get("paymentMethod"),
        status="PICKED_UP",
    )

    # quick validations
    if not booking.service_type or booking.items <= 0:
        return jsonify({"message": "Service type and items are required"}), 400
    if not booking.address or not booking.phone or not booking.payment_method:
        return jsonify({"message": "Address, phone and payment method are required"}), 400

    db.session.add(booking)
    db.session.commit()
    return jsonify({"message": "Booking created", "orderId": booking.id}), 201


@app.route("/api/bookings/<int:order_id>", methods=["GET"])
def get_booking(order_id):
    booking = Booking.query.get(order_id)
    if not booking:
        return jsonify({"message": "Booking not found"}), 404
    return jsonify(booking.to_dict()), 200

# -----------------------------------------------------------------------------
# Admin (form posts from your Admin modal)
# -----------------------------------------------------------------------------
@app.route("/admin/login", methods=["POST"])
def admin_login():
    # The modal posts form-encoded fields: adminEmail, adminPassword
    email = request.form.get("adminEmail", "").strip().lower()
    password = request.form.get("adminPassword", "")

    if email == ADMIN_EMAIL and password == ADMIN_PASSWORD:
        session["admin"] = email
        return redirect(url_for("admin_dashboard"))
    flash("Invalid admin credentials!", "danger")
    return redirect(url_for("index"))


@app.route("/admin/dashboard")
def admin_dashboard():
    if "admin" not in session:
        flash("Please login as admin first.", "warning")
        return redirect(url_for("index"))

    bookings = Booking.query.order_by(Booking.id.desc()).all()

    # Inline template so you don't need admin_dashboard.html as a file
    return render_template_string(
        """
        <!doctype html>
        <html>
        <head>
          <meta charset="utf-8"/>
          <title>Admin Dashboard · LaundryPro</title>
          <link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
          <style>
            table{width:100%;border-collapse:collapse}
            th,td{padding:10px;border-bottom:1px solid #eee;text-align:left}
            .status{font-weight:600}
            .toolbar{display:flex;justify-content:space-between;align-items:center;margin:20px 0}
            a.btn, button.btn{padding:8px 14px;border-radius:8px;text-decoration:none;border:none;cursor:pointer}
            .btn-primary{background:#2563eb;color:#fff}
            .btn-muted{background:#eee}
            form.inline{display:inline}
            .container{max-width:1060px;margin:0 auto;padding:24px}
          </style>
        </head>
        <body>
          <div class="container">
            <div class="toolbar">
              <h2>Admin Dashboard</h2>
              <div>
                <span>Logged in as: {{ session["admin"] }}</span>
                <a class="btn btn-muted" href="{{ url_for('admin_logout') }}">Logout</a>
              </div>
            </div>

            {% if bookings|length == 0 %}
              <p>No bookings yet.</p>
            {% else %}
              <table>
                <thead>
                  <tr>
                    <th>ID</th>
                    <th>Service</th>
                    <th>Items</th>
                    <th>Express</th>
                    <th>Pickup Date</th>
                    <th>Pickup Time</th>
                    <th>Phone</th>
                    <th>Payment</th>
                    <th>Status</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {% for b in bookings %}
                    <tr>
                      <td>{{ b.id }}</td>
                      <td>{{ b.service_type }}</td>
                      <td>{{ b.items }}</td>
                      <td>{{ "Yes" if b.express_service else "No" }}</td>
                      <td>{{ b.pickup_date.strftime("%Y-%m-%d") }}</td>
                      <td>{{ b.pickup_time.strftime("%H:%M") }}</td>
                      <td>{{ b.phone }}</td>
                      <td>{{ b.payment_method }}</td>
                      <td class="status">{{ b.status }}</td>
                      <td>
                        <form class="inline" method="post" action="{{ url_for('admin_update_status', order_id=b.id) }}">
                          <select name="status">
                            {% for s in ["PICKED_UP","IN_PROCESS","OUT_FOR_DELIVERY","DELIVERED"] %}
                              <option value="{{ s }}" {% if s==b.status %}selected{% endif %}>{{ s }}</option>
                            {% endfor %}
                          </select>
                          <button class="btn btn-primary" type="submit">Update</button>
                        </form>
                      </td>
                    </tr>
                  {% endfor %}
                </tbody>
              </table>
            {% endif %}
          </div>
        </body>
        </html>
        """,
        bookings=bookings
    )


@app.route("/admin/bookings/<int:order_id>/status", methods=["POST"])
def admin_update_status(order_id):
    if "admin" not in session:
        flash("Please login as admin first.", "warning")
        return redirect(url_for("index"))

    new_status = request.form.get("status")
    if new_status not in {"PICKED_UP", "IN_PROCESS", "OUT_FOR_DELIVERY", "DELIVERED"}:
        flash("Invalid status.", "danger")
        return redirect(url_for("admin_dashboard"))

    booking = Booking.query.get_or_404(order_id)
    booking.status = new_status
    db.session.commit()
    flash(f"Booking #{order_id} status updated to {new_status}.", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin", None)
    flash("Logged out successfully!", "info")
    return redirect(url_for("index"))

# -----------------------------------------------------------------------------
# Error handlers (clean JSON for API)
# -----------------------------------------------------------------------------
@app.errorhandler(404)
def not_found(e):
    # If it's an API route, return JSON
    if request.path.startswith("/api/"):
        return jsonify({"message": "Not found"}), 404
    return render_template("index.html"), 404  # fallback to home

@app.errorhandler(500)
def server_error(e):
    if request.path.startswith("/api/"):
        return jsonify({"message": "Server error"}), 500
    return render_template("index.html"), 500

# -----------------------------------------------------------------------------
# Bootstrap
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    with app.app_context():
        # Creates tables if they don't exist (safe for your existing DB)
        db.create_all()
    app.run(debug=True)
