# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

Pelican static site for the MSU Physics Education Research Lab (PERL), hosted on GitHub Pages at `perlmsu.github.io`. The infrastructure (theme, plugin, workflow) is adapted from the CERL site (`msu-cerl.github.io`); content was migrated from the old `perl.natsci.msu.edu` site. The Python environment is managed with `uv`. Pushing to `main` triggers automatic GitHub Pages build and deploy.

## Local Development

```bash
uv sync                                  # install / sync dependencies
uv run pelican content -s pelicanconf.py # one-shot build → output/
uv run pelican --listen --autoreload     # build + live-reload dev server
```

For a production build (sets `SITEURL`, deletes `output/` first):

```bash
uv run pelican content -s publishconf.py
```

## Site Architecture

Static pages live under `content/pages/` and news posts under `content/posts/`, all as Markdown files with Pelican metadata headers (plain `Key: Value` lines, no YAML fences). The custom theme is in `themes/`.

**Content pages** (in nav order):

- `home.md` — homepage (uses `index.html` template with aside sidebar)
- `people.md` — group roster, sections: Faculty → Researchers → Research Associates → Graduate Students → Undergraduate Students → Affiliates and Collaborators → Alumni
- `events.md` — current seminar series; `events-past.md` — past seminars by academic year (served at `/events/past/`)
- `research-areas.md` (`/research/areas/`) and `research-projects.md` (`/research/projects/`) — shown under the Research dropdown; PERL software (GitHub `PERLMSU` org) is listed under the related project
- `curriculum.md` — curriculum development
- `partnerships.md` — community partnerships / outreach
- `pubs.md` — publications, hand-edited, grouped by year
- `getting-involved.md` — mailing list, research opportunities, and contact info (there is no separate contact page)

Pages whose URL is nested (e.g. `/research/areas/`) set `URL:` and `Save_as:` metadata explicitly.

**News posts:** `content/posts/` — one Markdown file per post; served at `/news/{year}/{slug}/`. Filenames are `YYYY-MM-DD-slug.md`.

**Theme (`themes/`):**

- `templates/base.html` — shared header/footer, nav (with dropdown support), canonical link
- `templates/index.html` — extends base; adds aside sidebar
- `templates/page.html` — standard content page
- `templates/news.html` — news index; `templates/article.html` — individual post
- `static/css/style.css` — layout/typography; no hardcoded colors
- `static/css/theme-msu.css` — color tokens (`COLOR_SCHEME = "msu"`)
- `static/js/nav.js` — mobile menu and dropdown toggles

**Navigation:** `MENUITEMS` in `pelicanconf.py`. An entry is `(label, url)` or `(label, url, [(label, url), ...])` for a dropdown. A top-level item is highlighted when the current path starts with its URL; a dropdown parent is highlighted when the current path is in its section (e.g. `/research/`). The hamburger menu kicks in below 1240px — adding nav items may require raising that breakpoint in `style.css`.

**Static files:** everything under `content/assets/` is copied to `output/assets/`. Images live in `content/assets/img/{people,events,news}/`.

## Adding or Updating People

Each entry in `content/pages/people.md` follows this pattern:

```markdown
#### Firstname Lastname
<img src="/assets/img/people/firstname-lastname.jpg" style="float:left;margin:0 1.25rem 1rem 0" width="120" alt="Firstname Lastname">
Title, Department, MSU<br>
Office<br>
<email@msu.edu>
```

Headshots with `width="120"` are cropped to a 120×150 box by CSS (`object-fit: cover`). The `<img>` tag is optional.

## Writing News Posts

```
Title: Post Title Here
Date: 2026-01-15
Author: Firstname Lastname
Slug: short-url-slug
Summary: One or two sentences shown on the news index page.

Full post content starts here...
```

`Author` and `Summary` are optional (Pelican auto-generates a summary). Slugs must be unique across all posts.

## Typogrify

`TYPOGRIFY = True` is set in `pelicanconf.py`. It will mangle double-quoted HTML attributes that contain quote-like characters, so avoid interpolating Pelican variables into double-quoted attributes such as `aria-label` in templates — use visually hidden text (`.sr-only`) instead, as the nav dropdown does.

## Placeholders

Unfinished content is marked with `TODO` in italics. Find it with `grep -rn TODO content/pages`.
