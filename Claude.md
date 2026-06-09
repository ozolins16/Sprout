# Sprout — Appointment Booking Platform

Django web app for small beauty businesses (barbershops, nail salons) to manage appointments. **University coursework — Web Technologies II, University of Latvia.** Solo project, hard deadline: 1 week from project start.

## Tech stack

- **Backend:** Django 5.x, Python 3.12
- **DB:** MySQL 8 (use `mysqlclient` driver)
- **Email:** Resend API (`resend` Python SDK)
- **Hosting:** Railway, with custom subdomain
- **VCS:** Git / GitHub
- **Frontend:** Django templates + vanilla JS (Fetch API for AJAX). No SPA, no React.

## Project rules (course requirements — these are graded)

These are not preferences. Breaking any of them lowers the grade:

1. **MVC separation must be clean.** Models = data, Views = templates, Controllers = Django views. No business logic in templates. No DB queries in templates.
2. **Database is in 3rd Normal Form.** 5 related tables minimum.
3. **All four CRUD operations** must exist for at least one main entity (services and appointments both qualify).
4. **Localization required:** users can switch between English and Latvian. Use Django's i18n (`{% trans %}`, `gettext`).
5. **At least 4 user roles** with distinct permissions: guest, client, staff, owner.
6. **Passwords never stored in plain text.** Use Django's built-in auth — never write custom password handling.
7. **Nice URLs.** No `?page=...` or script names in paths. Use Django URL patterns with slugs/IDs only when needed.
8. **UTF-8 everywhere.** All templates declare `<meta charset="utf-8">`. DB collation `utf8mb4_unicode_ci`.
9. **HTML and CSS must validate** against W3C validators.
10. **Git: at least 3 commits with different timestamps.** Commit after every meaningful unit of work, not all at once at the end.

## Roles

- **Guest** — browse services, view available slots. Cannot book.
- **Client** — registered user. Can book, view booking history, cancel own appointments.
- **Staff** — works at one business. Sets own weekly availability. Sees own appointments only.
- **Owner** — manages one business. Adds/removes staff, manages services, sees all appointments. Also acts as admin.

## Data model (5 tables, 3NF)

- `users` — Django's built-in `User` + role field
- `businesses` — name, category (`barbershop` / `nail_salon`), owner FK
- `services` — name, price, duration_minutes, business FK
- `staff` — user FK, business FK, photo, working days (e.g. bitmask or JSON), start/end time
- `appointments` — client FK, staff FK, service FK, datetime, status (`pending` / `confirmed` / `cancelled`)

## Features to build (in priority order)

**Must have (in this order):**
1. User model with roles, auth (login/register/logout)
2. Owner creates business, picks category, default services seeded
3. Owner manages services (CRUD) and staff (add/remove)
4. Staff sets weekly availability (working days + start/end time)
5. Public booking flow: service → staff → date/time (AJAX slot loading)
6. Client registration + view own bookings + cancel own bookings
7. Staff photo upload (advanced requirement)
8. Confirmation email via Resend (advanced + i-option)
9. EN/LV language switch
10. Railway deployment with subdomain

**Do NOT build (out of scope):**
- 24h reminder emails (needs Celery, too much setup)
- Lunch breaks / ad-hoc schedule blocks
- Reviews / ratings
- Public business directory
- Payments
- Multi-location businesses
- Mobile app
- Real-time updates (WebSockets)

## Coding style

- **Python:** PEP 8. Type hints on function signatures where helpful, not everywhere.
- **Django:** class-based views where they reduce code, function-based otherwise. No mixing without reason.
- **Forms:** always use Django forms or ModelForms for validation. Never trust request data directly.
- **Templates:** extend a single `base.html`. Keep partials in `templates/partials/`.
- **Static files:** `static/css/`, `static/js/`, `static/img/`. One CSS file is fine — don't fragment unnecessarily.
- **No JS framework.** Vanilla JS with `fetch()` for AJAX. Keep JS in dedicated files, not inline in templates.
- **Comments:** explain *why*, not *what*. Skip obvious ones.
- **Variable/function names in English.** User-facing strings go through `gettext` for translation.

## Project structure

```
sprout/
├── manage.py
├── requirements.txt
├── .env                  # never commit
├── sprout/               # project config
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── accounts/         # custom user model, auth views
│   ├── businesses/       # business + services + staff
│   └── bookings/         # appointments + booking flow
├── templates/
│   ├── base.html
│   └── <app>/
├── static/
├── locale/               # translation files
│   ├── en/
│   └── lv/
└── media/                # user uploads (staff photos)
```

## Git workflow

- One branch (`main`) is fine for solo project. No need for feature branches.
- **Commit after each numbered feature above.** That gives 10+ commits with different timestamps, well over the required 3.
- Commit messages: short and present-tense. e.g. `add staff availability form`, `wire up booking confirmation email`.

## Common commands

```bash
# setup
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser

# dev
python manage.py runserver
python manage.py makemigrations && python manage.py migrate
python manage.py compilemessages          # rebuild translations

# translations
django-admin makemessages -l lv
django-admin makemessages -l en

# deploy (Railway uses Procfile or railway.json)
git push origin main                      # Railway auto-deploys
```

## Things to remember

- **Never store secrets in code.** Use `.env` + `python-decouple` or `django-environ`. Resend API key, DB password, Django secret all go in env vars.
- **Use Django's auth.** Don't roll custom password hashing, custom sessions, or custom login forms unless absolutely needed.
- **CSRF tokens on all forms.** Django does this automatically with `{% csrf_token %}` — never disable.
- **Always escape output** in templates. Django auto-escapes by default — don't use `|safe` unless content is trusted.
- **Time zones:** set `TIME_ZONE = 'Europe/Riga'` and `USE_TZ = True`. Store all datetimes in UTC.
- **When stuck, ask before assuming.** I (Linards) am the developer — if a requirement is unclear or a design choice has tradeoffs, ask rather than picking silently.

## Out of scope reminders

If I ask for any of these, push back first — they're explicitly cut from scope:
- Reminder emails, reviews, payments, public directory, multi-location, real-time, lunch blocks.
- New user roles beyond the 4 listed.
- Extra DB tables beyond the 5 listed (unless adding a true many-to-many through-table that's required).