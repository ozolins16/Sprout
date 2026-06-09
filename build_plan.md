# Sprout — 7-Day Build Plan

Reference document. Keep next to `CLAUDE.md`. Each day = one Claude Code session (or split into two if needed). Follow the order strictly — later days assume earlier days are done.

---

## Setup (do once, before Day 1)

1. Create folder `sprout/` somewhere on your machine
2. Drop `CLAUDE.md` inside it
3. Create `.gitignore` (content already given earlier)
4. Open Claude Code in the Claude app and point it at the `sprout/` folder
5. Run:
   ```bash
   git init
   git add CLAUDE.md .gitignore
   git commit -m "initial setup"
   ```

**Decision:** for local development use SQLite (zero setup). MySQL gets configured only when deploying to Railway on Day 7. This is a normal Django pattern.

---

## Day 1 — Project Foundation

**Goal:** Working Django project with custom User model + login/register/logout.

**Prompt:**

> Read CLAUDE.md fully before doing anything. Then set up Day 1 of the project:
>
> 1. Create a virtual environment `.venv` and install: `Django==5.0.*`, `python-decouple`, `Pillow`, `resend`
> 2. Create `requirements.txt`
> 3. Scaffold the Django project: outer name `sprout_project`, inner config module `sprout`. Create three apps inside `apps/`: `accounts`, `businesses`, `bookings`. Register them in `INSTALLED_APPS`.
> 4. Configure `settings.py`: SQLite for local dev (read from `.env`), `TIME_ZONE = 'Europe/Riga'`, `USE_TZ = True`, `LANGUAGE_CODE = 'en'`, `LANGUAGES = [('en', 'English'), ('lv', 'Latvian')]`, set up `LOCALE_PATHS`, `STATIC_URL`, `MEDIA_URL`, `MEDIA_ROOT`. Use `python-decouple` for env vars.
> 5. In `accounts`, create a custom `User` model extending `AbstractUser` with a `role` field — choices: `client`, `staff`, `owner`. Make it the `AUTH_USER_MODEL` before running any migrations.
> 6. Create `.env` and `.env.example` (commit only the example).
> 7. Create `base.html` template with a header (nav: home, login/register or logout), `{% block content %}`, and a simple plain CSS file in `static/css/main.css`. No JS frameworks.
> 8. Build register/login/logout views and templates. Registration defaults role to `client`. Use Django's built-in auth forms where possible.
> 9. Run `makemigrations` and `migrate`. Verify the server runs.
>
> Do NOT yet build: businesses, services, staff, bookings, localization strings, or email logic.
>
> Stop and tell me when done so I can test.

**Manual test:**
- `python manage.py runserver` works
- Visit `/`, see home page
- Register a new client → redirected somewhere sensible
- Logout, log back in
- Open Django admin (`/admin/`), see User model with `role` field

**Commit:** `day 1: project scaffolding, custom user model, auth`

---

## Day 2 — Business Setup + Service CRUD

**Goal:** Owner can register a business, pick a category, and manage services.

**Prompt:**

> Read CLAUDE.md. Day 1 is committed. Today is Day 2: business setup and service CRUD.
>
> 1. In `businesses` app, create `Business` model: `name`, `category` (choices: `barbershop`, `nail_salon`), `owner` (FK to User), `created_at`. One business per owner for now (OneToOne or unique FK).
> 2. Create `Service` model: `name`, `price` (Decimal), `duration_minutes` (PositiveInteger), `business` (FK), `created_at`.
> 3. Update registration: add a separate "Register as Business Owner" flow that creates a User with `role='owner'` and then redirects to a "Create Business" form. After business is created, seed default services based on category:
>    - Barbershop: Haircut (£20, 30 min), Beard Trim (£15, 20 min), Hot Towel Shave (£25, 40 min)
>    - Nail Salon: Manicure (£25, 45 min), Pedicure (£30, 60 min), Gel Extensions (£45, 90 min)
> 4. Owner dashboard at `/dashboard/`: shows business name + nav to "Services" and (later) "Staff". Owners-only — middleware or decorator that enforces role.
> 5. Service CRUD pages for owner: list, create, edit, delete. Use Django forms with proper validation. Nice URLs (`/dashboard/services/`, `/dashboard/services/<id>/edit/`, etc.).
> 6. Update `base.html` nav to show "Dashboard" link if user is owner.
>
> Do NOT yet build: staff management, staff availability, bookings, email.
>
> Stop and let me test.

**Manual test:**
- Register as a new owner → asked to create business → pick "Barbershop"
- After creation, dashboard shows business + 3 default services
- Add a new service → appears in list
- Edit a service → changes persist
- Delete a service → confirmation works
- Log out, log in as the client from Day 1 → no access to `/dashboard/`

**Commit:** `day 2: business model + service CRUD for owner`

---

## Day 3 — Staff Management + Availability

**Goal:** Owner can add/remove staff. Staff can log in and set their weekly availability.

**Prompt:**

> Read CLAUDE.md. Day 2 is committed. Today is Day 3: staff management + availability.
>
> 1. In `businesses` app, create `Staff` model: `user` (OneToOne to User), `business` (FK), `bio` (TextField, optional), `photo` (ImageField, optional — leave upload logic for Day 5, just add the field).
> 2. Add availability fields directly to Staff: `working_days` (CharField storing comma-separated day numbers 0-6, e.g. "0,1,2,3"), `start_time` (TimeField, default 09:00), `end_time` (TimeField, default 18:00).
> 3. Owner pages at `/dashboard/staff/`:
>    - List staff
>    - Add staff: form takes username, email, password, name → creates a new User with `role='staff'`, creates Staff record linked to owner's business
>    - Remove staff: deletes Staff and the linked User (with confirmation)
> 4. Staff dashboard at `/staff/`: shows greeting, link to "My Schedule".
> 5. Staff schedule page: form with checkboxes for working days + start/end time pickers. Saves to Staff model.
> 6. Add role-based redirect after login: owner → `/dashboard/`, staff → `/staff/`, client → `/`.
>
> Do NOT yet build: photo upload (just the field), bookings, AJAX, email.
>
> Stop and let me test.

**Manual test:**
- As owner, go to `/dashboard/staff/`, add a new staff member
- Log out, log in as that staff user → redirected to `/staff/`
- Open "My Schedule", uncheck Friday-Sunday, set hours 10:00-17:00, save
- Reload, values persisted
- Log back in as owner → see staff member listed

**Commit:** `day 3: staff management + weekly availability`

---

## Day 4 — Public Booking Flow with AJAX

**Goal:** Clients can browse services, pick a staff member, and book an available slot.

**Prompt:**

> Read CLAUDE.md. Day 3 is committed. Today is Day 4: the public booking flow — this is the most important day, take it carefully.
>
> 1. In `bookings` app, create `Appointment` model: `client` (FK to User), `staff` (FK to Staff), `service` (FK to Service), `start_datetime` (DateTimeField), `status` (choices: `confirmed`, `cancelled`, default `confirmed`), `created_at`.
> 2. Public business page at `/book/<business_id>/`: lists services for that business with name, price, duration. User clicks a service → next step.
> 3. Staff selection page `/book/<business_id>/service/<service_id>/`: lists all staff at that business. User clicks one → next step.
> 4. Date + time picker page `/book/<business_id>/service/<service_id>/staff/<staff_id>/`:
>    - Date picker (default today, can go forward up to 30 days)
>    - On date change, fetch available slots via AJAX from `/api/slots/?staff=<id>&service=<id>&date=YYYY-MM-DD`
>    - Slots are 15-min intervals between staff's start_time and end_time, on staff's working_days only, with no overlapping confirmed appointments. Account for service duration when computing availability.
>    - Render slots as clickable buttons. Clicking → confirm page.
> 5. AJAX endpoint returns JSON: `{"slots": ["09:00", "09:15", ...]}`.
> 6. Booking confirmation: if user is not logged in or not a client, redirect to login with `?next=` pointing back. If logged in as client, show "Confirm: [Service] with [Staff] on [Date] at [Time]" + button. POST creates the Appointment with `status='confirmed'`.
> 7. After booking, redirect to a simple success page showing the appointment details. (Email comes Day 5.)
>
> Use plain `fetch()` for AJAX. No external JS libraries. CSRF token included in the headers.
>
> Do NOT yet build: email, photo upload, cancellation, history page.
>
> Stop and let me test the full booking flow.

**Manual test:**
- Log out
- Visit `/book/<business_id>/` (get ID from admin)
- Pick a service → pick the staff from Day 3 → pick today (or tomorrow if today doesn't match staff's working days)
- Slots appear without page reload
- Click a slot → asked to log in
- Log in as client → redirected back to confirm page
- Confirm → success page
- Try booking the same slot again → it should no longer appear

**Commit:** `day 4: public booking flow with ajax slot loading`

---

## Day 5 — Email + Photo Upload + Client History

**Goal:** Confirmation emails, staff photos visible, clients can see and cancel their bookings.

**Prompt:**

> Read CLAUDE.md. Day 4 is committed. Today is Day 5: emails, file upload, client features.
>
> 1. Resend integration:
>    - Add `RESEND_API_KEY` to `.env` and `settings.py`
>    - After a booking is created (Day 4 flow), send a confirmation email via Resend to the client's email. Plain text + simple HTML. Include service name, staff name, business name, date and time.
>    - Wrap the send in a try/except — never let an email failure break the booking. Log errors.
> 2. Staff photo upload:
>    - On the staff schedule page, add a "Profile" form with photo upload. Save to `Staff.photo`.
>    - Show staff photo on the staff selection page in the booking flow (placeholder image if none).
>    - Make sure `MEDIA_URL` and `MEDIA_ROOT` are wired up in `urls.py` for local dev.
> 3. Client booking history at `/my/bookings/`:
>    - List all of the client's appointments, newest first
>    - For each: service, staff, business, datetime, status
>    - If `start_datetime` is in the future and status is `confirmed`, show a "Cancel" button
>    - Cancel button (POST with CSRF) sets status to `cancelled`
>    - Add nav link for clients to access this page
> 4. The booking confirmation page on success should also link to `/my/bookings/`.
>
> Do NOT yet build: localization, reminder emails, owner calendar view.
>
> Stop and let me test.

**Manual test:**
- Make a booking as a client → check the email arrives
- As staff, upload a photo → visible on the booking page
- As client, visit `/my/bookings/` → see the booking
- Cancel it → status updates, slot frees up
- Try to book the same slot again → should work since it's cancelled

**Commit:** `day 5: email confirmation, photo upload, client booking history`

---

## Day 6 — Localization + Polish

**Goal:** EN/LV language switch works. HTML/CSS validates. UI feels finished.

**Prompt:**

> Read CLAUDE.md. Day 5 is committed. Today is Day 6: localization and polish.
>
> 1. Set up Django i18n:
>    - Make sure `LocaleMiddleware` is in `MIDDLEWARE`
>    - Set `USE_I18N = True`
>    - Set up URL patterns with `i18n_patterns` (for nice URLs like `/lv/dashboard/` and `/en/dashboard/`)
> 2. Wrap every user-facing string in templates with `{% trans %}` (load `i18n` at the top of each template).
> 3. Wrap user-facing strings in Python code (form labels, error messages, etc.) with `gettext_lazy as _`.
> 4. Run `django-admin makemessages -l lv` to generate `.po` file. Translate every string into Latvian. Then `compilemessages`.
> 5. Add a language switcher to `base.html` — a small form (`set_language` view) with EN / LV options, persists via session/cookie.
> 6. Validate HTML and CSS:
>    - Make sure every page has `<!DOCTYPE html>`, `<html lang="...">`, `<meta charset="utf-8">`, proper `<title>`
>    - Run a few pages through the W3C validator mentally — fix unclosed tags, missing alt attrs, etc.
> 7. General polish: make sure the layout is consistent across pages, forms have proper labels, error messages display nicely, success messages use Django's messages framework.
>
> Do NOT add new features. Today is purely translation + polish.
>
> Stop and let me test.

**Manual test:**
- Switch language to LV — every page reads in Latvian
- Switch back to EN — same
- Go through register → login → booking → cancellation in both languages
- Visit https://validator.w3.org/ and paste a page's HTML — no errors

**Commit:** `day 6: en/lv localization + html validation polish`

---

## Day 7 — Railway Deployment

**Goal:** Live, accessible at a public subdomain. MySQL in production.

**Prompt:**

> Read CLAUDE.md. Day 6 is committed. Today is Day 7: deployment to Railway.
>
> 1. Add MySQL production config:
>    - Update `settings.py` so the DB engine reads from `.env` (defaults to SQLite if not set)
>    - Add MySQL settings reading `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` from env
>    - Make sure `mysqlclient` is in `requirements.txt`
> 2. Add production-readiness:
>    - `DEBUG = False` when `ENV=production`
>    - `ALLOWED_HOSTS` reads from env, comma-separated
>    - Configure `whitenoise` for static files (install + add to MIDDLEWARE + set STATIC_ROOT)
>    - Run `collectstatic` as part of deploy
> 3. Create `Procfile`:
>    ```
>    web: gunicorn sprout.wsgi
>    release: python manage.py migrate
>    ```
>    Add `gunicorn` to `requirements.txt`.
> 4. Tell me exactly what steps I need to do on Railway's website (create project, add MySQL plugin, link GitHub repo, set env vars list, attach custom subdomain).
>
> Do NOT push to a remote yet — I'll create the GitHub repo and Railway project myself, then come back.

**After Claude Code finishes the config part, you do this manually:**

1. Push the project to a new GitHub repo:
   ```bash
   gh repo create sprout --private --source=. --push
   ```
   (or use the GitHub web UI)
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub repo
3. Add MySQL plugin to the project
4. Set env vars in Railway: `SECRET_KEY`, `DEBUG=False`, `ENV=production`, `ALLOWED_HOSTS=<your-subdomain>.up.railway.app`, `RESEND_API_KEY`, and the DB vars (Railway auto-injects MySQL credentials — copy them across)
5. In Railway settings, generate a public domain (subdomain)
6. Wait for deploy → visit URL

**Then back in Claude Code:**

> The site is deployed at `<URL>`. Help me debug any issues I see. After everything works, do final polish: check for broken links, error pages (404, 500), verify the booking flow end-to-end on production.

**Commit:** `day 7: railway deployment + production config`

---

## When things go wrong

If a prompt produces broken or wrong code, don't try to fix it manually. Paste the issue back to Claude Code:

> The X page is showing error Y. Here's the traceback: [paste]. Fix it without changing unrelated files.

Or for design issues:

> The Z is not working as expected. I wanted it to do A, but it does B. Reread the relevant section of CLAUDE.md and the Day N prompt, then fix.

---

## Final checklist before submitting

- [ ] 4 roles: guest, client, staff, owner
- [ ] 5 tables in 3NF
- [ ] CRUD on services + appointments
- [ ] Auth (Django built-in, no plain text passwords)
- [ ] Nice URLs (no `?page=...`)
- [ ] UTF-8 throughout
- [ ] EN/LV language switch
- [ ] HTML/CSS validates
- [ ] At least 3 Git commits with different timestamps (you'll have 7+)
- [ ] File upload working (staff photos)
- [ ] Email notifications working (booking confirmation)
- [ ] AJAX working (slot loading)
- [ ] Deployed to Railway with custom subdomain
- [ ] 3rd-party API integration (Resend)

That's all 10 basic + 3 advanced + both i-option requirements. Full marks territory.