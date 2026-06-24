# M UMAR Natural Remedies — Flask Website

A complete, production-ready Flask website for **M UMAR Natural Remedies**, a traditional
herbal wellness business based in Kano, Nigeria.

## Features

- Public website: Home, Products, Appointment booking (Contact)
- Admin panel: secure login, dashboard with stats, appointment management, full product CRUD with image upload
- SQLite database (`database.db`) with `admin`, `products`, and `appointments` tables
- Tailwind CSS (CDN) + AOS scroll animations
- Fully responsive, green & gold premium herbal design
- Floating WhatsApp button + per-product WhatsApp ordering links

## Folder Structure

```
M_UMAR_NATURAL_REMEDIES/
├── app.py                  # Main Flask application
├── init_db.py               # Run once to create & seed the database
├── database.db              # SQLite database (created by init_db.py)
├── templates/                # All standalone HTML pages
├── static/
│   ├── css/style.css         # All custom styling
│   ├── js/main.js            # All custom JavaScript
│   ├── uploads/               # Uploaded product images land here
│   └── images/                 # Static site images (optional)
```

## Setup & Run

1. Install dependencies:
   ```bash
   pip install flask werkzeug
   ```

2. Initialize the database (creates tables + a default admin + 6 sample products):
   ```bash
   python init_db.py
   ```

3. Run the app:
   ```bash
   python app.py
   ```

4. Visit the site:
   - Public site: http://127.0.0.1:5000/
   - Admin login: http://127.0.0.1:5000/login

## Default Admin Login

| Username | Password    |
|----------|-------------|
| admin    | Admin@2026  |

**Important:** Change this password before deploying to production. The simplest way is to
open a Python shell, hash a new password with `werkzeug.security.generate_password_hash`,
and update the `admin` table in `database.db` directly, or add an account-settings route.

## Business Information

- **Business:** M UMAR Natural Remedies
- **Location:** Kano, Nigeria
- **Phone / WhatsApp:** +2348036924570

## Notes on Production Deployment

- Replace `app.secret_key` in `app.py` with a long, random, secret value (e.g. via an environment variable).
- Turn off `debug=True` in `app.run()`.
- Consider moving from SQLite to PostgreSQL/MySQL for higher concurrency in production.
- Serve the app behind a production WSGI server (e.g. Gunicorn) and a reverse proxy (e.g. Nginx).
