# Yeeun Kim — personal website

Static site for GitHub Pages. No framework: `build.py` turns `data/site.toml` into `index.html`.

## Update
1. Edit `data/site.toml` (publications, news, experience, ...). Wording follows the latest CV docx.
2. New paper thumbnail → `assets/pubs/<venue><year>-<keyword>.jpg`, then set `image = ...` on the entry.
3. New CV → export a copy with the phone number removed (the original docx stays untouched) to `assets/cv.pdf`. The public site never carries the phone number.
4. `python3 build.py`, preview with `python3 -m http.server 8765`, then commit and push.

## Layout
- `data/site.toml` – all content
- `build.py` – generator (Python 3.11+, standard library only)
- `assets/style.css`, `assets/img/`, `assets/pubs/` – styles and images
- `index.html` – generated; do not edit by hand
