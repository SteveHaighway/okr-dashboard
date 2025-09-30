# OKR Dashboard — Fixed "Growing Bars" Build

This build fixes Plotly re-layout loops by:
- stable `dcc.Graph` IDs per KR,
- `uirevision` in mini & drawer charts,
- `fixedrange` axes,
- transitions disabled,
- a CSS height clamp for mini charts.

## Local run
```bash
pip install -r requirements.txt
python app.py
```

## Deploy on Render
- Build Command: `pip install -r requirements.txt`
- Start Command: `gunicorn app:server -w 1 -k gthread --threads 4 -t 120`
