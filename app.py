"""
app.py
M UMAR Natural Remedies - Main Flask Application

Run with:
    python init_db.py     (first time only, creates database.db)
    python app.py
"""

import os
from datetime import datetime
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, flash, g
)
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import sqlite3

# --------------------------------------------------------------------------
# APP CONFIGURATION
# --------------------------------------------------------------------------

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "database.db")
UPLOAD_FOLDER = os.path.join(BASE_DIR, "static", "uploads")
ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

app = Flask(__name__)
app.secret_key = "mumar-natural-remedies-secret-key-2026-kano-change-in-production"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024  # 5 MB max upload

# Business information (used across all templates)
BUSINESS_NAME = "M UMAR Natural Remedies"
BUSINESS_LOCATION = "Kano, Nigeria"
PHONE_NUMBER = "+2348036924570"
WHATSAPP_NUMBER = "2348036924570"  # no '+' for wa.me links

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# --------------------------------------------------------------------------
# DATABASE HELPERS
# --------------------------------------------------------------------------

def get_db():
    """Open a new database connection for the current request context."""
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(exception=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


def save_uploaded_image(file_storage):
    """Safely save an uploaded image and return its stored filename, or None."""
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_file(file_storage.filename):
        return None

    safe_name = secure_filename(file_storage.filename)
    base, ext = os.path.splitext(safe_name)
    unique_name = f"{base}_{int(datetime.now().timestamp())}{ext}"
    file_storage.save(os.path.join(app.config["UPLOAD_FOLDER"], unique_name))
    return unique_name


def delete_uploaded_image(filename):
    if not filename:
        return
    path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
    if os.path.exists(path):
        try:
            os.remove(path)
        except OSError:
            pass


# --------------------------------------------------------------------------
# AUTH DECORATOR
# --------------------------------------------------------------------------

def login_required(view_func):
    @wraps(view_func)
    def wrapped_view(*args, **kwargs):
        if not session.get("admin_logged_in"):
            flash("Please log in to access the admin area.", "error")
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    return wrapped_view


# --------------------------------------------------------------------------
# GLOBAL TEMPLATE VARIABLES
# --------------------------------------------------------------------------

@app.context_processor
def inject_globals():
    return dict(
        business_name=BUSINESS_NAME,
        business_location=BUSINESS_LOCATION,
        phone_number=PHONE_NUMBER,
        whatsapp_number=WHATSAPP_NUMBER,
        current_year=datetime.now().year,
    )


# --------------------------------------------------------------------------
# PUBLIC ROUTES
# --------------------------------------------------------------------------

@app.route("/")
def index():
    db = get_db()
    featured_products = db.execute(
        "SELECT * FROM products ORDER BY id DESC LIMIT 6"
    ).fetchall()
    return render_template("index.html", products=featured_products)


@app.route("/products")
def products():
    db = get_db()
    all_products = db.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
    return render_template("products.html", products=all_products)


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip()
        service = request.form.get("service", "").strip()
        preferred_date = request.form.get("preferred_date", "").strip()
        preferred_time = request.form.get("preferred_time", "").strip()
        message = request.form.get("message", "").strip()

        errors = []
        if len(name) < 2:
            errors.append("Please enter your full name.")
        if len(phone) < 7:
            errors.append("Please enter a valid phone number.")
        if not preferred_date:
            errors.append("Please choose a preferred appointment date.")
        if not service:
            errors.append("Please select a service.")

        if errors:
            for err in errors:
                flash(err, "error")
            return render_template("contact.html", form_data=request.form)

        db = get_db()
        db.execute(
            """INSERT INTO appointments
               (name, phone, email, service, preferred_date, preferred_time, message, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                name, phone, email, service, preferred_date,
                preferred_time, message,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            ),
        )
        db.commit()
        return redirect(url_for("appointment_success"))

    return render_template("contact.html", form_data={})


@app.route("/appointment-success")
def appointment_success():
    return render_template("appointment_success.html")


# --------------------------------------------------------------------------
# ADMIN AUTH ROUTES
# --------------------------------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Please enter both username and password.", "error")
            return render_template("login.html")

        db = get_db()
        admin_row = db.execute(
            "SELECT * FROM admin WHERE username = ?", (username,)
        ).fetchone()

        if admin_row and check_password_hash(admin_row["password"], password):
            session["admin_logged_in"] = True
            session["admin_username"] = admin_row["username"]
            flash(f"Welcome back, {admin_row['username']}!", "success")
            return redirect(url_for("admin"))

        flash("Invalid username or password.", "error")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("login"))


# --------------------------------------------------------------------------
# ADMIN DASHBOARD
# --------------------------------------------------------------------------

@app.route("/admin")
@login_required
def admin():
    db = get_db()
    total_products = db.execute("SELECT COUNT(*) AS c FROM products").fetchone()["c"]
    total_appointments = db.execute("SELECT COUNT(*) AS c FROM appointments").fetchone()["c"]
    appointments = db.execute(
        "SELECT * FROM appointments ORDER BY id DESC"
    ).fetchall()
    return render_template(
        "admin.html",
        total_products=total_products,
        total_appointments=total_appointments,
        appointments=appointments,
    )


@app.route("/admin/appointments/delete/<int:appointment_id>", methods=["POST"])
@login_required
def delete_appointment(appointment_id):
    db = get_db()
    db.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
    db.commit()
    flash("Appointment deleted successfully.", "success")
    return redirect(url_for("admin"))


# --------------------------------------------------------------------------
# ADMIN PRODUCT MANAGEMENT
# --------------------------------------------------------------------------

@app.route("/admin/products")
@login_required
def admin_products():
    db = get_db()
    all_products = db.execute("SELECT * FROM products ORDER BY id DESC").fetchall()
    return render_template("admin_products.html", products=all_products)


@app.route("/admin/products/add", methods=["GET", "POST"])
@login_required
def add_product():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        price_raw = request.form.get("price", "").strip()

        errors = []
        if len(name) < 2:
            errors.append("Please enter a valid product name.")
        if len(description) < 5:
            errors.append("Please enter a product description.")

        price = None
        if not price_raw:
            errors.append("Please enter a price.")
        else:
            try:
                price = float(price_raw)
                if price < 0:
                    errors.append("Price cannot be negative.")
            except ValueError:
                errors.append("Price must be a valid number.")

        image_file = request.files.get("image")
        if image_file and image_file.filename and not allowed_file(image_file.filename):
            errors.append("Image must be PNG, JPG, JPEG, GIF, or WEBP.")

        if errors:
            for err in errors:
                flash(err, "error")
            return render_template("add_product.html", form_data=request.form)

        image_filename = save_uploaded_image(image_file)

        db = get_db()
        db.execute(
            "INSERT INTO products (name, description, price, image, created_at) VALUES (?, ?, ?, ?, ?)",
            (name, description, price, image_filename, datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
        )
        db.commit()
        flash("Product added successfully.", "success")
        return redirect(url_for("admin_products"))

    return render_template("add_product.html", form_data={})


@app.route("/admin/products/edit/<int:product_id>", methods=["GET", "POST"])
@login_required
def edit_product(product_id):
    db = get_db()
    product = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()

    if not product:
        flash("Product not found.", "error")
        return redirect(url_for("admin_products"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        description = request.form.get("description", "").strip()
        price_raw = request.form.get("price", "").strip()

        errors = []
        if len(name) < 2:
            errors.append("Please enter a valid product name.")
        if len(description) < 5:
            errors.append("Please enter a product description.")

        price = None
        if not price_raw:
            errors.append("Please enter a price.")
        else:
            try:
                price = float(price_raw)
                if price < 0:
                    errors.append("Price cannot be negative.")
            except ValueError:
                errors.append("Price must be a valid number.")

        image_file = request.files.get("image")
        if image_file and image_file.filename and not allowed_file(image_file.filename):
            errors.append("Image must be PNG, JPG, JPEG, GIF, or WEBP.")

        if errors:
            for err in errors:
                flash(err, "error")
            return render_template("edit_product.html", product=product)

        image_filename = product["image"]
        if image_file and image_file.filename and allowed_file(image_file.filename):
            delete_uploaded_image(product["image"])
            image_filename = save_uploaded_image(image_file)

        db.execute(
            "UPDATE products SET name = ?, description = ?, price = ?, image = ? WHERE id = ?",
            (name, description, price, image_filename, product_id),
        )
        db.commit()
        flash("Product updated successfully.", "success")
        return redirect(url_for("admin_products"))

    return render_template("edit_product.html", product=product)


@app.route("/admin/products/delete/<int:product_id>", methods=["POST"])
@login_required
def delete_product(product_id):
    db = get_db()
    product = db.execute("SELECT * FROM products WHERE id = ?", (product_id,)).fetchone()
    if product:
        delete_uploaded_image(product["image"])
    db.execute("DELETE FROM products WHERE id = ?", (product_id,))
    db.commit()
    flash("Product deleted successfully.", "success")
    return redirect(url_for("admin_products"))


# --------------------------------------------------------------------------
# ENTRY POINT
# --------------------------------------------------------------------------

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        print("database.db not found. Please run 'python init_db.py' first.")
    app.run(debug=True)
