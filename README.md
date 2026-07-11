# Workboard — Backend

Django + Django REST Framework API powering **Workboard**: a Kanban task manager
(`/api/tasks/`, `/api/tags/`) and an image annotation tool (`/api/images/`,
`/api/shapes/`), plus two AI-powered endpoints built on Gemini
(`/api/tasks/parse/` for natural-language task entry, and
`/api/annotate/suggest-label/` for auto-labeling drawn shapes).

- **Live API:** https://workboard-backend-h6em.onrender.com
- **Frontend repo:** https://github.com/Shafayatur/workboard-frontend
- **Live app:** https://workboard-frontend-live.vercel.app
- **Demo login:** `demo@workboard.app` / `DemoPass123!`

---

## Stack

- Django 4.2.30 (LTS) + Django REST Framework
- SimpleJWT for auth (email + password login)
- PostgreSQL in production (Neon, via `DATABASE_URL`), SQLite for local dev
- Cloudinary for uploaded image storage in production
- Gemini API (`gemini-2.5-flash`) for the two AI features
- Deployed on Render (gunicorn + whitenoise for static files)

## Requirements

- **Python 3.9–3.12** (developed with 3.11.9 — the project deliberately avoids
  any package version that requires 3.10+, so it also runs on plain Python 3.9)
- pip

## Setup

```bash
git clone https://github.com/Shafayatur/workboard-backend.git
cd workboard-backend

python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# then fill in .env — see "Environment variables" below

python manage.py migrate
python manage.py seed_demo_user  # creates demo@workboard.app / DemoPass123!
python manage.py runserver
```

API will be live at `http://127.0.0.1:8000`.

## Environment variables

See `.env.example` for the full list. The only ones required to run locally
with basic functionality are the defaults already in that file. To exercise
every feature locally you'll also want:

- `CLOUDINARY_URL` — free account at cloudinary.com (optional locally; without
  it, uploaded images just save to local disk instead)
- `GEMINI_API_KEY` — free key at https://aistudio.google.com/apikey (required
  for quick-add task parsing and shape auto-labeling; both features degrade
  gracefully without it — task creation still works via the manual "+ Manual"
  form, shapes just keep a generic "Region N" label)

## Running tests / sanity checks

```bash
python manage.py check
python manage.py collectstatic --noinput   # only needed to verify prod static setup
```

---

## Villains faced (and how they were beaten)

**Scaffolded on Django 6, but the only Python available locally was 3.9.**
Rather than fight the environment, downgraded to Django 4.2.30 (the current
LTS) — but the naive fix (`pip freeze` from a Python 3.12 environment) quietly
pinned `requests`, `urllib3`, `Pillow`, and `python-dotenv` at versions that
themselves required Python 3.10+, even though nothing about the actual app
needed them. Fixed by rewriting `requirements.txt` to pin only *direct*
dependencies, each individually verified (via `pip download --python-version
3.9 --only-binary=:all:`) against the real constraint, and leaving transitive
dependencies unpinned so pip resolves them correctly for whichever Python
actually runs the project.

**Django 6→4.2 also silently broke image storage.** The scaffold used
`DEFAULT_FILE_STORAGE`, which Django deprecated in 4.2 and removed outright in
5.1 — meaning it was already a no-op before the downgrade even started.
Replaced with the modern `STORAGES` dict, which has worked since 4.2.

**Render's free tier has an ephemeral disk.** SQLite would lose every task
and image on the first restart or redeploy. Solved by adding Postgres
(Neon, for a permanent free tier) via `DATABASE_URL` / `dj-database-url`,
falling back to SQLite automatically when that variable isn't set — so local
dev is completely unaffected.

**Production 500 errors were undiagnosable.** `DEBUG=False` silences Django's
default exception logging, so a real bug (see Cloudinary, below) showed up in
Render's logs as nothing but a bare `POST ... 500` with no traceback. Fixed by
adding an explicit `LOGGING` config so unhandled exceptions actually print —
which is what made every subsequent bug in this list possible to diagnose at
all.

**Cloudinary uploads failed with `Invalid api_key`.** Turned out the angle
brackets from Cloudinary's dashboard template (`<your_api_key>`) had been
copied into the environment variable along with the real key. An easy trap —
the brackets are just UI scaffolding, not part of the value.

**Gemini calls returned a 404 for a model that definitely existed.** Google
had just migrated AI Studio's default key format from `AIzaSy...` ("Standard")
to `AQ.Ab...` ("Auth") keys. Rather than guess, isolated the problem with raw
`curl` against Gemini's REST API directly (bypassing Django entirely): first
confirmed the key could list available models, then confirmed the exact
failing request actually succeeded outside the app. That proved the key and
model were both fine — the real cause was simply testing against a Render
deploy that hadn't picked up the latest code yet.

**A hydration error on the `/tasks` page traced back here too:** a nested
`<form>` (the tag-creation control inside the task modal's own form) is
invalid HTML and silently broke client/server rendering — not a backend bug,
but diagnosed via the same "read the actual error, don't guess" approach as
everything above.