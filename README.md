# Site portfolio — Thomas Szuwalski

Site vitrine professionnel statique (HTML/CSS/JS pur), généré à partir d'un
seul fichier de contenu grâce à un petit script Python (aucune dépendance
externe, aucune installation nécessaire).

## Structure du projet

```
data/content.json      → TOUT le contenu du site (textes, expériences, projets, contact...)
build.py                → génère le site dans dist/ à partir de content.json
assets/
  css/style.css         → direction artistique (couleurs, typographie, mise en page)
  js/main.js             → menu mobile, animations légères, formulaire de contact
  img/                    → favicon, image de partage (og-image), photo de profil
  cv/                     → déposez ici votre CV au format PDF
dist/                    → site généré (ne pas modifier à la main, régénéré à chaque build)
.github/workflows/deploy.yml → déploiement automatique sur GitHub Pages
```

## Aperçu en local

Aucune installation requise, seul Python 3 (déjà présent sur macOS) est utilisé.

```bash
python3 build.py
cd dist && python3 -m http.server 8000
```

Puis ouvrez http://localhost:8000 dans votre navigateur.

À chaque modification de `data/content.json`, relancez `python3 build.py`
pour régénérer le site.

## Modifier le contenu

Tout se passe dans **`data/content.json`**. C'est le seul fichier à modifier
au quotidien.

### Ajouter une expérience ou une formation
Dans `timeline.experiences` (ou `timeline.formations`), ajoutez un objet :
```json
{
  "title": "Intitulé du poste",
  "organization": "Nom de la structure",
  "period": "2025 – 2026",
  "description": "Description courte des missions.",
  "skills": ["Compétence 1", "Compétence 2"]
}
```

### Ajouter un projet
Dans `projects.items`, dupliquez un bloc existant et changez `slug` (utilisé
dans l'URL, sans espaces ni accents), `title`, `category`, `shortDescription`
et le contenu de `caseStudy`. Une page dédiée est générée automatiquement à
l'adresse `/projets/<slug>/`.

Tant qu'un projet contient des mentions `[À compléter]`, laissez `"draft": true`
— un badge "À compléter" s'affiche alors sur la vignette et la page détail,
pour ne jamais présenter du contenu inventé comme réel. Passez `"draft": false`
une fois les informations réelles renseignées.

### Remplacer la photo
1. Déposez votre photo dans `assets/img/profile.jpg` (ou `.png`).
2. Dans `content.json`, mettez à jour `profile.photo` avec le bon chemin et
   passez `profile.photoPlaceholder` à `false`.

### Ajouter le CV
1. Déposez le PDF dans `assets/cv/` (le chemin par défaut attendu est
   `assets/cv/thomas-szuwalski-cv.pdf`, modifiable dans `cv.fileUrl`).
2. Dans `content.json`, passez `cv.available` à `true`.

### Modifier les coordonnées, la recherche d'alternance, les compétences, etc.
Toutes ces informations sont regroupées dans les sections correspondantes de
`content.json` (`profile`, `alternance`, `skills`, `contact`...). Éditez
directement le texte entre guillemets.

⚠️ Le JSON est sensible à la syntaxe : chaque valeur doit être entre
guillemets `"..."`, chaque élément d'une liste séparé par une virgule (mais
pas de virgule après le dernier élément). En cas de doute, faites relire le
fichier par un outil de validation JSON en ligne avant de le publier.

## Modifier le design

Toutes les couleurs, polices et espacements sont centralisés en haut de
`assets/css/style.css` dans le bloc `:root { ... }` — modifier une valeur
là suffit à changer tout le site de façon cohérente.

## Éléments à compléter avant mise en ligne définitive

- [ ] Photo de profil (`assets/img/profile.jpg` + `content.json`)
- [ ] CV au format PDF (`assets/cv/` + `content.json`)
- [ ] Dates précises des expériences marquées `[Période à préciser]`
- [ ] Détails réels des 6 projets (actuellement en `"draft": true`)
- [ ] Liste des logiciels maîtrisés (`skills.tools.items`, actuellement vide)
- [ ] `site.url` dans `content.json` (URL définitive du site)
- [ ] Remplacer `assets/img/og-image.svg` par une version PNG/JPG : certains
      réseaux (dont LinkedIn) affichent mal les images de partage au format
      SVG. Vous pouvez exporter une image 1200×630 depuis Canva ou Figma en
      reprenant le même visuel, puis mettre à jour `site.ogImage`.

## Déploiement sur GitHub Pages

1. Créez un dépôt sur GitHub (public ou privé, un dépôt privé fonctionne
   aussi avec GitHub Pages sur les plans qui le permettent) et poussez ce
   projet :
   ```bash
   git add .
   git commit -m "Site portfolio initial"
   git branch -M main
   git remote add origin https://github.com/<votre-utilisateur>/<votre-repo>.git
   git push -u origin main
   ```
2. Dans le dépôt GitHub : **Settings → Pages → Build and deployment → Source**,
   choisissez **GitHub Actions**. Le workflow `.github/workflows/deploy.yml`
   déjà présent se charge de lancer `python3 build.py` et de publier `dist/`
   à chaque `push` sur `main`.
3. Si le dépôt s'appelle `<votre-utilisateur>.github.io`, le site sera servi
   à la racine (`basePath: ""` dans `content.json`, déjà la valeur par
   défaut). Si le dépôt a un autre nom (ex. `portfolio`), le site sera servi
   sur `https://<votre-utilisateur>.github.io/portfolio/` : mettez alors
   `site.basePath` à `"/portfolio"` dans `content.json` puis relancez le
   build et repoussez.
4. Un nom de domaine personnalisé peut être ajouté ensuite dans
   **Settings → Pages → Custom domain**.

## Performance & SEO déjà en place

- Zéro framework JS, zéro build lourd : HTML/CSS/JS servis tels quels.
- `sitemap.xml` et `robots.txt` générés automatiquement.
- Meta title/description, Open Graph et Twitter Card générés pour chaque
  page (accueil + chaque étude de cas projet) à partir de `content.json`.
- Animations limitées à un léger fondu au scroll, désactivées automatiquement
  si l'utilisateur a activé "réduire les animations" dans son système.
