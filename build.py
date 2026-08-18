#!/usr/bin/env python3
"""
Générateur statique du site de Thomas Szuwalski.

Aucune dépendance externe (uniquement la bibliothèque standard Python 3).
Lit data/content.json et produit un site statique dans dist/.

Usage :
    python3 build.py
"""
import html
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).parent
DATA_FILE = ROOT / "data" / "content.json"
ASSETS_DIR = ROOT / "assets"
DIST_DIR = ROOT / "dist"


def esc(value):
    return html.escape(str(value), quote=True)


def load_content():
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Composants
# ---------------------------------------------------------------------------

NAV_ITEMS = [
    ("Accueil", "#accueil"),
    ("À propos", "#a-propos"),
    ("Parcours", "#parcours"),
    ("Projets", "#projets"),
    ("Compétences", "#competences"),
    ("CV", "#cv"),
    ("Contact", "#contact"),
]


def render_head(data, *, title, description, canonical_path, og_image=None):
    site = data["site"]
    base = site["basePath"]
    full_url = site["url"].rstrip("/") + canonical_path
    og_image_url = site["url"].rstrip("/") + (og_image or site["ogImage"])
    return f"""<meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{esc(title)}</title>
  <meta name="description" content="{esc(description)}">
  <link rel="canonical" href="{esc(full_url)}">
  <meta name="theme-color" content="{esc(site['themeColor'])}">
  <link rel="icon" type="image/svg+xml" href="{base}{site['favicon']}">

  <meta property="og:type" content="website">
  <meta property="og:title" content="{esc(title)}">
  <meta property="og:description" content="{esc(description)}">
  <meta property="og:url" content="{esc(full_url)}">
  <meta property="og:image" content="{esc(og_image_url)}">
  <meta property="og:locale" content="{esc(site['locale'])}">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="{esc(title)}">
  <meta name="twitter:description" content="{esc(description)}">
  <meta name="twitter:image" content="{esc(og_image_url)}">

  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,400;9..144,500;9..144,600&family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{base}/assets/css/style.css">
"""


def render_header(data, base, active_is_home):
    profile = data["profile"]
    home_href = f"{base}/" if not active_is_home else "#accueil"
    prefix = "" if active_is_home else f"{base}/"
    links = "\n".join(
        f'          <li><a href="{prefix}{href}">{esc(label)}</a></li>'
        for label, href in NAV_ITEMS
    )
    return f"""  <header class="site-header">
    <div class="container">
      <a class="brand" href="{home_href}">{esc(profile['fullName'])}</a>
      <nav class="main-nav" id="main-nav">
        <ul>
{links}
        </ul>
      </nav>
      <button class="nav-toggle" aria-label="Ouvrir le menu" aria-expanded="false" aria-controls="main-nav">
        <span></span><span></span><span></span>
      </button>
    </div>
  </header>
"""


def render_footer(data, base):
    profile = data["profile"]
    footer = data["footer"]
    return f"""  <footer class="site-footer">
    <div class="container footer-grid">
      <div>
        <div class="footer-brand">{esc(profile['fullName'])}</div>
        <div class="footer-tagline">{esc(footer['tagline'])}</div>
      </div>
      <div class="footer-links">
        <a href="{esc(profile['linkedin'])}" target="_blank" rel="noopener">LinkedIn</a>
        <a href="mailto:{esc(profile['email'])}">Email</a>
      </div>
      <div class="footer-copy">{esc(footer['copyright'])}</div>
    </div>
  </footer>
"""


def render_hero(data):
    hero = data["hero"]
    profile = data["profile"]
    base = data["site"]["basePath"]
    ctas = "\n".join(
        f'        <a class="btn btn-{cta["style"]}" href="{esc(cta["href"])}">{esc(cta["label"])}</a>'
        for cta in hero["ctas"]
    )
    if profile.get("photoPlaceholder", True):
        photo = '<span class="monogram">TS</span>'
    else:
        photo = f'<img src="{base}{esc(profile["photo"])}" alt="Photo de {esc(profile["fullName"])}">'
    return f"""  <section id="accueil" class="hero invert">
    <div class="container hero-grid">
      <div class="hero-text">
        <span class="kicker reveal">{esc(hero['kicker'])}</span>
        <h1 class="reveal">{esc(hero['headline'])}</h1>
        <p class="hero-intro reveal">{esc(hero['intro'])}</p>
        <div class="btn-row reveal">
{ctas}
        </div>
        <div class="hero-links reveal">
          <a href="{esc(profile['linkedin'])}" target="_blank" rel="noopener">LinkedIn ↗</a>
          <a href="mailto:{esc(profile['email'])}">{esc(profile['email'])}</a>
        </div>
      </div>
      <div class="hero-photo reveal">
        <div class="hero-photo-inner">
          {photo}
        </div>
      </div>
    </div>
  </section>
"""


def render_about(data):
    about = data["about"]
    paragraphs = "\n".join(f"        <p>{esc(p)}</p>" for p in about["paragraphs"])
    return f"""  <section id="a-propos" class="alt">
    <div class="container">
      <h2 class="reveal">{esc(about['heading'])}</h2>
      <div class="about-columns reveal">
{paragraphs}
      </div>
    </div>
  </section>
"""


def render_timeline_item(item, with_skills=False, minor=False):
    skills_html = ""
    if with_skills and item.get("skills"):
        tags = "".join(f'<span class="tag">{esc(s)}</span>' for s in item["skills"])
        skills_html = f'<div class="timeline-skills">{tags}</div>'
    css_class = "timeline-item timeline-item--minor reveal" if minor else "timeline-item reveal"
    return f"""        <div class="{css_class}">
          <div class="timeline-period">{esc(item['period'])}</div>
          <h4>{esc(item['title'])}</h4>
          <div class="timeline-org">{esc(item['organization'])}</div>
          <p>{esc(item['description'])}</p>
          {skills_html}
        </div>
"""


def render_timeline(data):
    t = data["timeline"]
    formations = "\n".join(render_timeline_item(i) for i in t["formations"])
    experiences = "\n".join(render_timeline_item(i, with_skills=True) for i in t["experiences"])
    other_experiences = t.get("otherExperiences") or []
    other_html = ""
    if other_experiences:
        other_items = "\n".join(render_timeline_item(i, with_skills=True, minor=True) for i in other_experiences)
        other_html = f"""          <div class="timeline-secondary">
            <div class="timeline-secondary-title">Autres expériences</div>
{other_items}
          </div>
"""
    return f"""  <section id="parcours">
    <div class="container">
      <div class="section-head reveal">
        <h2>{esc(t['heading'])}</h2>
      </div>
      <div class="timeline-columns">
        <div class="timeline-col">
          <div class="timeline-col-title">Formation</div>
{formations}
        </div>
        <div class="timeline-col">
          <div class="timeline-col-title">Expériences</div>
{experiences}
{other_html}
        </div>
      </div>
    </div>
  </section>
"""


def render_project_card(project, base):
    draft_badge = '<span class="draft-badge">À compléter</span>' if project.get("draft") else ""
    return f"""      <a class="project-card reveal" href="{base}/projets/{project['slug']}/">
        <div class="project-thumb">
          <span class="placeholder-icon">{esc(project['title'][:2].upper())}</span>
          {draft_badge}
        </div>
        <div class="project-body">
          <span class="project-category">{esc(project['category'])}</span>
          <h3>{esc(project['title'])}</h3>
          <p>{esc(project['shortDescription'])}</p>
          <span class="project-link">Voir l'étude de cas →</span>
        </div>
      </a>
"""


def render_projects(data, base):
    p = data["projects"]
    if p["items"]:
        body = f'<div class="project-grid">\n{"".join(render_project_card(item, base) for item in p["items"])}      </div>'
    else:
        empty = p["emptyState"]
        body = f"""<div class="project-empty reveal">
        <h3>{esc(empty['title'])}</h3>
        <p>{esc(empty['text'])}</p>
        <a class="btn btn-secondary" href="{base}/#contact">Me contacter</a>
      </div>"""
    return f"""  <section id="projets" class="alt">
    <div class="container">
      <div class="section-head reveal">
        <h2>{esc(p['heading'])}</h2>
        <p class="lede">{esc(p['intro'])}</p>
      </div>
      {body}
    </div>
  </section>
"""


def render_skills(data):
    s = data["skills"]
    cols = []
    for cat in s["categories"]:
        items = "\n".join(f"          <li>{esc(i)}</li>" for i in cat["items"])
        cols.append(f"""        <div class="skills-col reveal">
          <div class="skills-col-title">{esc(cat['title'])}</div>
          <ul>
{items}
          </ul>
        </div>""")
    cols_html = "\n".join(cols)

    tools = s["tools"]["items"]
    if tools:
        tools_html = "".join(f'<span class="tag">{esc(t)}</span>' for t in tools)
        tools_block = f'<div class="tools-list">{tools_html}</div>'
    else:
        tools_block = '<p class="tools-empty">Liste à compléter.</p>'

    return f"""  <section id="competences">
    <div class="container">
      <div class="section-head reveal">
        <h2>{esc(s['heading'])}</h2>
      </div>
      <div class="skills-grid">
{cols_html}
      </div>
      <div class="tools-row reveal">
        <div class="skills-col-title">{esc(s['tools']['title'])}</div>
        {tools_block}
      </div>
    </div>
  </section>
"""


def render_alternance(data):
    a = data["alternance"]
    items = "\n".join(
        f"""        <div class="alternance-item">
          <div class="label">{esc(i['label'])}</div>
          <div class="value">{esc(i['value'])}</div>
        </div>"""
        for i in a["items"]
    )
    return f"""  <section id="alternance" class="invert">
    <div class="container">
      <div class="alternance-box reveal">
        <h2>{esc(a['heading'])}</h2>
        <p class="lede">{esc(a['intro'])}</p>
        <div class="alternance-grid">
{items}
        </div>
        <a class="btn btn-primary" href="{esc(a['cta']['href'])}">{esc(a['cta']['label'])}</a>
      </div>
    </div>
  </section>
"""


def render_cv(data, base):
    cv = data["cv"]
    if cv["available"]:
        btn = f'<a class="btn btn-primary" href="{base}{esc(cv["fileUrl"])}" download>{esc(cv["downloadLabel"])}</a>'
        note = ""
    else:
        btn = f'<span class="btn btn-primary is-disabled" aria-disabled="true">{esc(cv["downloadLabel"])}</span>'
        note = f'<p class="cv-note">{esc(cv["unavailableNote"])}</p>'
    preview = f'<img src="{base}{esc(cv["previewImage"])}" alt="Aperçu du CV de {esc(data["profile"]["fullName"])}">'
    return f"""  <section id="cv">
    <div class="container cv-layout">
      <div class="cv-preview reveal">{preview}</div>
      <div class="reveal">
        <div class="btn-row">{btn}</div>
        {note}
      </div>
    </div>
  </section>
"""


def render_contact(data):
    c = data["contact"]
    profile = data["profile"]; form_enabled = c.get("formEnabled", True)
    fields_map = {
        "Nom": ("nom", "text"),
        "Email": ("email", "email"),
        "Entreprise": ("entreprise", "text"),
    }
    inputs = []
    for label in c["form"]["fields"]:
        if label == "Message":
            continue
        name, itype = fields_map.get(label, (label.lower(), "text"))
        inputs.append(f"""        <div class="form-field">
          <label for="field-{name}">{esc(label)}</label>
          <input type="{itype}" id="field-{name}" name="{name}" {"required" if name in ("nom", "email") else ""}>
        </div>""")
    inputs_html = "\n".join(inputs)

    return f"""  <section id="contact" class="alt">
    <div class="container {'contact-grid' if form_enabled else 'contact-grid contact-grid--solo'}">
      <div class="reveal">
        <h2>{esc(c['heading'])}</h2>
        <p class="lede">{esc(c['intro'])}</p>
        <ul class="contact-info-list">
          <li><span class="label">Email</span><a href="mailto:{esc(profile['email'])}">{esc(profile['email'])}</a></li>
          <li><span class="label">Téléphone</span><a href="tel:{esc(profile['phone'].replace(' ', ''))}">{esc(profile['phone'])}</a></li>
          <li><span class="label">LinkedIn</span><a href="{esc(profile['linkedin'])}" target="_blank" rel="noopener">{esc(profile['linkedin'])}</a></li>
          <li><span class="label">Localisation</span><span>{esc(profile['location'])}</span></li>
        </ul>
      </div>
      <form class="reveal" id="contact-form" data-contact-email="{esc(profile['email'])}">
        <div class="form-grid">
{inputs_html}
          <div class="form-field full">
            <label for="field-message">Message</label>
            <textarea id="field-message" name="message" required></textarea>
          </div>
        </div>
        <button type="submit" class="btn btn-primary">{esc(c['form']['submitLabel'])}</button>
        <p class="form-note">Ce formulaire ouvre votre messagerie pour envoyer le message directement à {esc(profile['email'])}.</p>
      </form>
    </div>
  </section>
"""


def render_page_shell(data, *, body, head_extra, base, active_is_home):
    return f"""<!doctype html>
<html lang="fr">
<head>
{head_extra}</head>
<body>
{render_header(data, base, active_is_home)}
{body}
{render_footer(data, base)}
  <script src="{base}/assets/js/main.js"></script>
</body>
</html>
"""


def render_home(data):
    base = data["site"]["basePath"]
    head = render_head(
        data,
        title=data["site"]["title"],
        description=data["site"]["description"],
        canonical_path="/",
    )
    body = "\n".join([
        render_hero(data),
        render_about(data),
        render_timeline(data),
        render_projects(data, base),
        render_skills(data),
        render_alternance(data),
        render_cv(data, base),
        render_contact(data),
    ])
    return render_page_shell(data, body=body, head_extra=head, base=base, active_is_home=True)


def render_case_study(data, project):
    base = data["site"]["basePath"]
    cs = project["caseStudy"]
    title = f"{project['title']} | {data['profile']['fullName']}"
    description = project["shortDescription"]
    head = render_head(
        data,
        title=title,
        description=description,
        canonical_path=f"/projets/{project['slug']}/",
    )
    draft_badge = '<span class="tag">Étude de cas à compléter</span>' if project.get("draft") else ""
    realisations = "\n".join(f"          <li>{esc(r)}</li>" for r in cs["realisations"])
    competences = "\n".join(f'<span class="tag">{esc(c)}</span>' for c in cs["competences"])

    body = f"""  <section class="case-hero">
    <div class="container">
      <a class="back-link" href="{base}/#projets">← Retour aux projets</a>
      <div class="case-meta">
        <span class="tag">{esc(project['category'])}</span>
        {draft_badge}
      </div>
      <h1>{esc(project['title'])}</h1>
      <p class="lede">{esc(project['shortDescription'])}</p>

      <div class="case-grid">
        <div class="case-block reveal">
          <h4>Contexte</h4>
          <p>{esc(cs['contexte'])}</p>
        </div>
        <div class="case-block reveal">
          <h4>Objectif</h4>
          <p>{esc(cs['objectif'])}</p>
        </div>
        <div class="case-block reveal">
          <h4>Mon rôle</h4>
          <p>{esc(cs['monRole'])}</p>
        </div>
        <div class="case-block reveal">
          <h4>Réalisations</h4>
          <ul>
{realisations}
          </ul>
        </div>
        <div class="case-block reveal">
          <h4>Résultats</h4>
          <p>{esc(cs['resultats'])}</p>
        </div>
        <div class="case-block reveal">
          <h4>Compétences mobilisées</h4>
          <div class="timeline-skills">{competences}</div>
        </div>
      </div>
    </div>
  </section>
"""
    return render_page_shell(data, body=body, head_extra=head, base=base, active_is_home=False)


def render_sitemap(data, project_slugs):
    site = data["site"]
    base_url = site["url"].rstrip("/")
    urls = [f"{base_url}/"] + [f"{base_url}/projets/{slug}/" for slug in project_slugs]
    entries = "\n".join(f"  <url><loc>{esc(u)}</loc></url>" for u in urls)
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{entries}
</urlset>
"""


def render_robots(data):
    base_url = data["site"]["url"].rstrip("/")
    return f"""User-agent: *
Allow: /

Sitemap: {base_url}/sitemap.xml
"""


# ---------------------------------------------------------------------------
# Build
# ---------------------------------------------------------------------------

def main():
    data = load_content()

    if DIST_DIR.exists():
        shutil.rmtree(DIST_DIR)
    DIST_DIR.mkdir(parents=True)

    shutil.copytree(ASSETS_DIR, DIST_DIR / "assets")

    (DIST_DIR / "index.html").write_text(render_home(data), encoding="utf-8")

    project_slugs = []
    for project in data["projects"]["items"]:
        slug = project["slug"]
        project_slugs.append(slug)
        page_dir = DIST_DIR / "projets" / slug
        page_dir.mkdir(parents=True, exist_ok=True)
        (page_dir / "index.html").write_text(render_case_study(data, project), encoding="utf-8")

    (DIST_DIR / "sitemap.xml").write_text(render_sitemap(data, project_slugs), encoding="utf-8")
    (DIST_DIR / "robots.txt").write_text(render_robots(data), encoding="utf-8")
    (DIST_DIR / ".nojekyll").write_text("", encoding="utf-8")

    print(f"Site généré dans {DIST_DIR} ({1 + len(project_slugs)} pages).")


if __name__ == "__main__":
    main()
