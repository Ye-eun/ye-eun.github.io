"""Build index.html from data/site.toml. Usage: python3 build.py"""
import html
import os
import tomllib

ROOT = os.path.dirname(os.path.abspath(__file__))
ME = "Yeeun Kim"

with open(os.path.join(ROOT, "data", "site.toml"), "rb") as f:
    d = tomllib.load(f)
p = d["profile"]
esc = html.escape


def authors(names):
    out = []
    for n in names:
        star = n.endswith("*")
        n = n.rstrip("*")
        s = f"<b>{esc(n)}</b>" if n == ME else esc(n)
        out.append(s + ("<sup>*</sup>" if star else ""))
    return ", ".join(out[:-1]) + (", and " if len(out) > 2 else " and ") + out[-1] if len(out) > 1 else out[0]


def v(path):
    """Append the file's mtime so browsers fetch updated images and CSS."""
    return f"{path}?v={int(os.path.getmtime(os.path.join(ROOT, path)))}"


def pub_card(x):
    first = x["authors"][0].rstrip("*") == ME
    corr = any(a.rstrip("*") == ME and a.endswith("*") for a in x["authors"])
    tags = " ".join(t for t, on in [("selected", x.get("selected")), ("lead", first or corr)] if on)
    url = f"https://doi.org/{x['doi']}"
    # Figures only for papers she led (first or corresponding author); co-authored papers stay compact.
    if first or corr:
        img = x.get("image")
        thumb = (f'<img src="{v(img)}" alt="" loading="lazy">' if img and os.path.exists(os.path.join(ROOT, img))
                 else f'<span class="ph">{esc(x["venue"])}</span>')
        cls, thumb = "pub", f'<a class="thumb" href="{url}" target="_blank" rel="noopener">{thumb}</a>'
    else:
        cls, thumb = "pub compact", ""
    return f"""
    <article class="{cls}" data-tags="{tags}">
      {thumb}
      <div class="meta">
        <h3><a href="{url}" target="_blank" rel="noopener">{esc(x["title"])}</a></h3>
        <p class="au">{authors(x["authors"])}</p>
        <p class="venue"><i>{esc(x["venue"])}</i>, {esc(x["details"])}, {x["year"]}</p>
        <p class="btns"><a href="{url}" target="_blank" rel="noopener">DOI</a></p>
      </div>
    </article>"""


def rows(items, left, right):
    return "\n".join(f'<li><span class="when">{esc(i[left])}</span><div>{right(i)}</div></li>' for i in items)


pubs = sorted(d["pubs"], key=lambda x: -x["year"])
initials = "".join(w[0] for w in ME.split())
photo = (f'<img class="photo" src="{v(p["photo"])}" alt="{esc(ME)}">' if os.path.exists(os.path.join(ROOT, p["photo"]))
         else f'<div class="photo ph-photo">{initials}</div>')

page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(p["name"])}</title>
<meta name="description" content="{esc(p['title'])}, {esc(p['affiliation'])}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Overpass:wght@400;600;700;800&family=Source+Serif+4:ital,opsz,wght@0,8..60,400;0,8..60,600;1,8..60,400&display=swap">
<link rel="stylesheet" href="{v("assets/style.css")}">
</head>
<body>
<nav class="top"><div class="wrap">
  <a class="brand" href="#">{esc(ME)}</a>
  <div class="links"><a href="#research">Research</a><a href="#publications">Publications</a><a href="#experience">Experience</a><a href="#teaching">Teaching</a><a href="{p["cv"]}" target="_blank">CV</a></div>
</div></nav>

<main class="wrap">
<header class="hero">
  {photo}
  <div>
    <h1>{esc(p["name"])}</h1>
    <p class="role">{esc(p["title"])}</p>
    <p class="aff">{esc(p["affiliation"])}</p>
    <p class="contact">{"".join(f'<a href="mailto:{e}">{e}</a>' for e in p["emails"])}</p>
    <p class="quick"><a class="btn" href="{p["cv"]}" target="_blank">CV (PDF)</a><a class="btn ghost" href="{p["scholar"]}" target="_blank" rel="noopener">Google Scholar</a><a class="btn ghost" href="{p["linkedin"]}" target="_blank" rel="noopener">LinkedIn</a></p>
  </div>
</header>

<section id="about">
  {"".join(f"<p>{esc(b)}</p>" for b in p["bio"])}
  <ul class="chips">{"".join(f"<li>{esc(i)}</li>" for i in p["interests"])}</ul>
</section>

<section id="news">
  <h2>News</h2>
  <ul class="news">{rows(d["news"], "date", lambda i: i["text"])}</ul>
</section>

<section id="research">
  <h2>Research</h2>
  <div class="areas">{"".join(f'''
    <article class="area">
      <div class="thumb"><img src="{v(r["image"])}" alt="" loading="lazy"></div>
      <h3>{esc(r["title"])}</h3>
      <ul>{"".join(f"<li>{esc(x)}</li>" for x in r["points"])}</ul>
    </article>''' for r in d["research"])}
  </div>
</section>

<section id="publications">
  <h2>Publications</h2>
  <div class="filter" role="group" aria-label="Filter publications">
    <button data-f="all" aria-pressed="true">All ({len(pubs)})</button>
    <button data-f="selected" aria-pressed="false">Selected</button>
    <button data-f="lead" aria-pressed="false">First / corresponding author</button>
  </div>
  <p class="note"><sup>*</sup> corresponding author</p>
  <div class="pubs">{"".join(pub_card(x) for x in pubs)}</div>


  <h3 class="sub">Manuscripts under review</h3>
  <ol class="plain">{"".join(f'<li>{authors(x["authors"])}. {esc(x["title"])}. <i>{esc(x["venue"])}</i> ({esc(x["status"])}).</li>' for x in d["under_review"])}</ol>

  <details><summary>Presentations ({len(d["presentations"])})</summary>
  <ol class="plain">{"".join(f'<li>{esc(x["text"]).replace(ME, f"<b>{ME}</b>")}</li>' for x in d["presentations"])}</ol>
  </details>
</section>

<section id="experience">
  <h2>Experience</h2>
  <ul class="timeline">{rows(d["appointments"], "period", lambda i: f'<b>{esc(i["role"])}</b>, {esc(i["org"])}' + (f'<br><span class="muted">{esc(i["detail"])}</span>' if i["detail"] else ""))}</ul>
  <h3 class="sub">Education</h3>
  <ul class="timeline">{rows(d["education"], "period", lambda i: f'<b>{esc(i["degree"])}</b>, {esc(i["org"])}' + (f'<br><span class="muted">{esc(i["detail"])}</span>' if i["detail"] else ""))}</ul>
</section>

<section id="teaching">
  <h2>Teaching</h2>
  <ul class="plain bullets">{"".join(f"<li>{t['text']}</li>" for t in d["teaching"])}</ul>
</section>

<section id="awards">
  <h2>Honors &amp; Awards</h2>
  <ul class="timeline">{rows(d["awards"], "year", lambda i: esc(i["text"]))}</ul>
</section>

<section id="service">
  <h2>Service</h2>
  <p><b>Journal reviewer:</b> {esc(d["service"]["journals"])}</p>
  <p><b>Conference reviewer:</b> {esc(d["service"]["conferences"])}</p>
</section>

<section id="references">
  <h2>References</h2>
  <p>{esc(d["references"]["text"])}</p>
</section>

</main>

<footer class="wrap">© {pubs[0]["year"]} {esc(ME)}</footer>
<script>
document.querySelectorAll('.filter button').forEach(b => b.onclick = () => {{
  document.querySelectorAll('.filter button').forEach(x => x.setAttribute('aria-pressed', x === b));
  document.querySelectorAll('.pub').forEach(c => c.hidden = b.dataset.f !== 'all' && !c.dataset.tags.split(' ').includes(b.dataset.f));
}});
</script>
</body>
</html>
"""

with open(os.path.join(ROOT, "index.html"), "w") as f:
    f.write(page)
print(f"index.html built: {len(pubs)} publications")
