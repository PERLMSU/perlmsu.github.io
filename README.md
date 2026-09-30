# Physics Education Research Lab at MSU

This is the website for the Physics Education Research Lab (PERL) at Michigan State University. It is built with [Pelican](https://getpelican.com) (a Python static site generator) and hosted on GitHub Pages at <https://perlmsu.github.io>. The Python environment is managed with [uv](https://docs.astral.sh/uv/).

## Prerequisites

Install `uv` if you don’t have it:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Alternatively, `uv` can be installed via a package manager (e.g. `brew install uv` on macOS). See the [official installation docs](https://docs.astral.sh/uv/getting-started/installation/) for all options.

## Building the website locally

Clone the repo and install dependencies:

```bash
git clone https://github.com/PERLMSU/perlmsu.github.io
cd perlmsu.github.io
uv sync
```

Then start a live-reloading local server:

```bash
uv run pelican --listen --autoreload
```

The site will be available at `http://localhost:8000`. Changes to content files are picked up automatically.

To do a one-shot build without serving:

```bash
uv run pelican content -s pelicanconf.py
```

Pushing to `main` triggers an automatic GitHub Pages build and deploy (takes a few minutes).

## Where things live

| Page | File |
| --- | --- |
| Home | `content/pages/home.md` |
| People | `content/pages/people.md` |
| Events (current) | `content/pages/events.md` |
| Past events | `content/pages/events-past.md` |
| News | `content/posts/` (one file per post) |
| Research Areas | `content/pages/research-areas.md` |
| Research Projects | `content/pages/research-projects.md` |
| Curriculum Development | `content/pages/curriculum.md` |
| Community Partnerships | `content/pages/partnerships.md` |
| Publications | `content/pages/pubs.md` |
| Getting Involved | `content/pages/getting-involved.md` |

Images go in `content/assets/img/` (subfolders `people/`, `events/`, `news/`). The navigation menu is `MENUITEMS` in `pelicanconf.py`.

Placeholder text still to be filled in is marked with `TODO`:

```bash
grep -rn TODO content/pages
```

## Adding a news post

Create a new Markdown file in `content/posts/` with the following metadata at the top:

```
Title: Post Title Here
Date: 2026-01-15
Author: Firstname Lastname
Slug: short-url-slug
Summary: One or two sentences shown on the news index page.

Full post content starts here...
```

The post will appear automatically at `/news/` in reverse chronological order. The URL will be `/news/{year}/{slug}/`.

## Adding a seminar

Add the talk to the top of the current academic year in `content/pages/events.md`, following the existing entries. At the end of the academic year, move that year's section to the top of `content/pages/events-past.md` (and add it to the year links at the top of that page).

## Updating publications

Add new entries to `content/pages/pubs.md` under the right year heading (add a new `## YYYY` heading and a link in the year list at the top when a new year starts).

## GitHub Pages setup

On every push to `main`, a GitHub Actions workflow builds the Pelican site and publishes `output/` to the `gh-pages` branch. GitHub Pages serves that branch. One-time setup in the repository settings:

1. Go to **Settings → Pages**
2. Under **Source**, select **Deploy from a branch**, then choose `gh-pages` and `/ (root)`

Don't edit the `gh-pages` branch by hand; it is overwritten on every deploy. You can also trigger a deploy manually from the **Actions** tab using the "Run workflow" button.
