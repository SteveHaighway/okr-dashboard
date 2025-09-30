# OKR Dashboard — Dash Deploy Package (Objectives → KRs)

A minimal Dash app with Objective cards (click to filter) and Key Result cards showing mini charts.
A right-side drawer displays the full KR trend + notes.

## Run locally
```bash
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python app.py
# http://127.0.0.1:8050
```

## Deploy (Render/Railway/Heroku)
- This repo includes `Procfile` and exposes `server = app.server` for Gunicorn.

### Heroku
```bash
heroku create your-okr-app
git init && git add . && git commit -m "init"
heroku buildpacks:set heroku/python
git push heroku main   # or 'master' depending on your git default
heroku ps:scale web=1
heroku open
```

### Render (free tier)
- New Web Service → Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:server`

### Railway
- Create a New Service from repo/zip, set Start Command: `gunicorn app:server`

## Notes
- Update dummy data in `app.py` (DATA constant) or wire to your store (e.g., WorkBoard/Jira) later.
- Pin Python in `runtime.txt` if your platform needs it (3.10 is safe for Dash).
