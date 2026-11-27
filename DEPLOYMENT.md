# Deployment Guide

CarePulse ships with everything needed to deploy to **Render**, **Railway**,
or **PythonAnywhere**. All three approaches rely on the same environment
variables (see `.env.example`) and the same production settings module,
`carepulse.settings.production`.

Before deploying anywhere:

1. Generate a real secret key:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(50))"
   ```
2. Decide on a database. SQLite is fine for a demo but a managed Postgres
   instance is strongly recommended for anything real — set `DATABASE_URL`
   accordingly (e.g. `postgres://USER:PASSWORD@HOST:5432/DBNAME`).
3. Never commit `.env` — it's already git-ignored.

---

## Option A — Render

Render can read `render.yaml` directly ("Blueprint" deploy) or you can set
it up manually as a Web Service.

### Blueprint deploy (recommended)
1. Push this repository to GitHub.
2. In the Render dashboard, choose **New → Blueprint** and point it at your
   repo. Render will read `render.yaml`, provision a free Postgres database
   (`carepulse-db`), and create the web service automatically.
3. Render runs `build.sh` (installs dependencies, runs `collectstatic`, runs
   `migrate`) and then starts `gunicorn -c gunicorn.conf.py carepulse.wsgi:application`.
4. Once live, open a shell (Render dashboard → your service → **Shell**) and run:
   ```bash
   python manage.py createsuperuser
   python manage.py seed_demo_data   # optional demo data
   ```

### Manual setup
1. **New → Web Service**, connect your repo.
2. Runtime: Python 3. Build command: `./build.sh`. Start command:
   `gunicorn -c gunicorn.conf.py carepulse.wsgi:application`.
3. Add environment variables:
   - `DJANGO_SETTINGS_MODULE=carepulse.settings.production`
   - `DJANGO_SECRET_KEY=<generated above>`
   - `DJANGO_DEBUG=False`
   - `DJANGO_ALLOWED_HOSTS=<your-app>.onrender.com`
   - `DJANGO_CSRF_TRUSTED_ORIGINS=https://<your-app>.onrender.com`
   - `DATABASE_URL=<your Postgres connection string>`
4. Deploy, then run migrations/superuser from the Render shell as above.

Static files are served by WhiteNoise directly from the app — no separate
static site or CDN configuration is required.

---

## Option B — Railway

1. Push this repository to GitHub and create a **New Project → Deploy from
   GitHub repo** in Railway.
2. Add a **PostgreSQL** plugin from Railway's plugin marketplace; Railway
   will inject a `DATABASE_URL` variable automatically.
3. In your service's **Variables** tab, add:
   - `DJANGO_SETTINGS_MODULE=carepulse.settings.production`
   - `DJANGO_SECRET_KEY=<generated above>`
   - `DJANGO_DEBUG=False`
   - `DJANGO_ALLOWED_HOSTS=<your-app>.up.railway.app`
   - `DJANGO_CSRF_TRUSTED_ORIGINS=https://<your-app>.up.railway.app`
4. Railway auto-detects the `Procfile`. It will run the `release` step
   (`python manage.py migrate --no-input`) before starting the `web`
   process (`gunicorn -c gunicorn.conf.py carepulse.wsgi:application`).
   If you'd rather run `collectstatic` as part of the build, add a
   **Build Command** of:
   ```bash
   pip install -r requirements.txt && python manage.py collectstatic --no-input
   ```
5. Open the Railway shell (or use `railway run`) to create a superuser and
   optionally seed demo data:
   ```bash
   railway run python manage.py createsuperuser
   railway run python manage.py seed_demo_data
   ```

---

## Option C — PythonAnywhere

PythonAnywhere runs WSGI apps directly rather than via Gunicorn, so the
setup differs slightly from Render/Railway.

1. **Upload the code.** Easiest via a GitHub clone from a PythonAnywhere Bash
   console:
   ```bash
   git clone https://github.com/<your-username>/carepulse.git
   cd carepulse
   ```
2. **Create a virtualenv** (PythonAnywhere convention):
   ```bash
   mkvirtualenv --python=/usr/bin/python3.12 carepulse-env
   pip install -r requirements.txt
   ```
3. **Create your `.env`** (or set the same variables as PythonAnywhere
   "environment variables" under the Web tab, depending on your plan):
   ```bash
   cp .env.example .env
   # edit DJANGO_SETTINGS_MODULE=carepulse.settings.production,
   # DJANGO_SECRET_KEY, DJANGO_ALLOWED_HOSTS=<you>.pythonanywhere.com, etc.
   ```
   SQLite works fine here since PythonAnywhere gives you a persistent
   filesystem — just make sure `DATABASE_URL` is left unset (or points at
   `sqlite:////home/<you>/carepulse/db.sqlite3`) if you don't want to pay for
   a separate MySQL/Postgres add-on.
4. **Run migrations and collect static files:**
   ```bash
   python manage.py migrate
   python manage.py collectstatic --no-input
   python manage.py createsuperuser
   ```
5. **Configure the Web app** (Web tab → Add a new web app → Manual
   configuration → Python 3.12):
   - **Virtualenv:** point at `/home/<you>/.virtualenvs/carepulse-env`
   - **WSGI configuration file:** edit the generated file to import
     CarePulse's WSGI application:
     ```python
     import os
     import sys

     path = "/home/<you>/carepulse"
     if path not in sys.path:
         sys.path.insert(0, path)

     os.environ.setdefault("DJANGO_SETTINGS_MODULE", "carepulse.settings.production")

     from django.core.wsgi import get_wsgi_application
     application = get_wsgi_application()
     ```
   - **Static files mapping** (Web tab → Static files section):
     | URL | Directory |
     |---|---|
     | `/static/` | `/home/<you>/carepulse/staticfiles` |
     | `/media/`  | `/home/<you>/carepulse/media` |

     (WhiteNoise still works here too if you prefer not to configure this
     mapping — either approach is fine.)
6. Click **Reload** on the Web tab.

---

## Post-deploy checklist

- [ ] `DJANGO_DEBUG=False` in production
- [ ] `DJANGO_SECRET_KEY` is a real random value, not the placeholder
- [ ] `DJANGO_ALLOWED_HOSTS` / `DJANGO_CSRF_TRUSTED_ORIGINS` match your real domain
- [ ] `python manage.py check --deploy` reports no unresolved warnings
- [ ] Migrations applied (`python manage.py migrate`)
- [ ] Static files collected (`python manage.py collectstatic --no-input`)
- [ ] A real superuser created (don't rely on seeded demo credentials in production)
- [ ] `logs/` is writable, or logging is redirected to your platform's log stream
