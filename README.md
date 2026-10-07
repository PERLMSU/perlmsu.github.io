# Physics Education Research Lab at MSU

This is the website for the Physics Education Research Lab (PERL) at Michigan State University, live at <https://perlmsu.github.io>. It is built with [Pelican](https://getpelican.com), a Python static site generator: pages are Markdown files, and Pelican turns them into HTML. The Python environment is managed with [uv](https://docs.astral.sh/uv/).

## 🚀 Getting started

Install `uv` if you don't have it (`brew install uv` on macOS, or see the [installation docs](https://docs.astral.sh/uv/getting-started/installation/) for other options):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Clone the repo and install dependencies:

```bash
git clone https://github.com/PERLMSU/perlmsu.github.io
cd perlmsu.github.io
uv sync
```

Start a local server that rebuilds the site whenever you save a file:

```bash
uv run pelican --listen --autoreload
```

Then open <http://localhost:8000>. To build once without a server (output goes to `output/`):

```bash
uv run pelican content -s pelicanconf.py
```

## 🗂️ Where things live

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
| Publications | `content/pages/pubs.md` (generated, see [Publications](#-publications)) |
| Getting Involved | `content/pages/getting-involved.md` |

Other folders:

- `content/assets/img/` holds images, in `people/`, `events/` and `news/` subfolders.
- `content/assets/bib/` holds the BibTeX files the publications page is built from.
- `bin/` holds the publication scripts; `templates/` holds the citation style they use.
- `themes/` is the site's look: HTML templates, CSS and JavaScript.
- The navigation menu is `MENUITEMS` in `pelicanconf.py`.

Text still to be written is marked `TODO`. To list it:

```bash
grep -rn TODO content/pages
```

## ✏️ Editing content

### Adding a person

Add an entry under the right section of `content/pages/people.md` (Faculty, Researchers, Research Associates, Graduate Students, Undergraduate Students, Affiliates and Collaborators, or Alumni):

```markdown
#### Firstname Lastname
<img src="/assets/img/people/firstname-lastname.jpg" style="float:left;margin:0 1.25rem 1rem 0" width="120" alt="Firstname Lastname">
Title, Department, MSU<br>
Office<br>
<email@msu.edu>
```

Put the headshot in `content/assets/img/people/`. Photos are cropped to 120×150 automatically. The `<img>` line is optional.

### Adding a news post

Create a Markdown file in `content/posts/` named `YYYY-MM-DD-short-slug.md`, starting with:

```
Title: Post Title Here
Date: 2026-01-15
Author: Firstname Lastname
Slug: short-url-slug
Summary: One or two sentences shown on the news index page.

Full post content starts here...
```

`Author` and `Summary` are optional, and every slug must be unique. The post appears at `/news/{year}/{slug}/`. The `/news/` page shows posts from the last 3 calendar years; older posts move to `/news/archive/` automatically on the next build (change `NEWS_RECENT_YEARS` in `pelicanconf.py` to adjust).

### Adding a seminar

Add the talk to the top of the current academic year in `content/pages/events.md`, following the existing entries. At the end of the academic year, move that year's section to the top of `content/pages/events-past.md` and add it to the year links at the top of that page.

## 📚 Publications

The publications page is built from BibTeX files in two steps:

1. `bin/dedupe_bib.py` merges every `.bib` file in `content/assets/bib/` into `group_publications.bib`, using Claude to find duplicates.
2. `bin/create_pubs.py` formats `group_publications.bib` in APA style and writes `content/pages/pubs.md`, grouped by year.

To add publications, put a new or updated `.bib` file (for example, an export from Google Scholar or Zotero) in `content/assets/bib/` and run both steps.

### Step 1: merge and remove duplicates

This step calls the Anthropic API, so it needs an API key with credits (a Claude.ai subscription doesn't cover API use). Create one at [console.anthropic.com](https://console.anthropic.com), then:

```bash
export ANTHROPIC_API_KEY=sk-ant-...      # fish: set -x ANTHROPIC_API_KEY sk-ant-...
uv run bin/dedupe_bib.py
```

Instead of a key, you can install the `ant` CLI (`brew install anthropics/tap/ant`) and run `ant auth login` once.

The script reads every `.bib` file in the folder except its own two outputs and writes:

- `group_publications.bib`: every unique entry, plus the most complete copy of each set of confirmed duplicates
- `possible_duplicates.bib`: entries Claude wasn't sure about, grouped, with the file each came from

Both files are rewritten on every run, so don't edit them by hand. To resolve a group in `possible_duplicates.bib`, edit the input files instead: delete the weaker copy if the entries are the same paper, or give one a new citation key if they are different papers that share a key. Then run the script again. Each run makes new API calls, and the script prints how many entry pairs it will check before it calls the API.

### Step 2: build the publications page

This step runs locally and costs nothing. Preview the result in a separate file first:

```bash
uv run python bin/create_pubs.py pubs_preview.md
```

When it looks right, overwrite the real page and delete the preview:

```bash
uv run python bin/create_pubs.py
rm pubs_preview.md
```

⚠️ `pubs.md` is replaced completely, so any publication that isn't in `group_publications.bib` disappears from the site, and hand formatting such as bold group-member names is lost. Before the first run, check that everything on the current page is in the bib files. To undo an overwrite you haven't committed yet:

```bash
git checkout content/pages/pubs.md
```

## 🚢 Publishing

Pushing to `main` publishes the site: a GitHub Actions workflow builds it with `publishconf.py` and pushes the result to the `gh-pages` branch, which GitHub Pages serves. It takes a few minutes. Pushes to other branches run the build as a check but don't publish. You can also start a deploy from the **Actions** tab with the "Run workflow" button.

The workflow installs exactly what `uv.lock` lists, so after adding a dependency with `uv add`, commit both `pyproject.toml` and `uv.lock` or the build will fail.

Don't edit the `gh-pages` branch by hand; it is overwritten on every deploy.

### One-time GitHub Pages setup

1. Go to **Settings → Pages**.
2. Under **Source**, choose **Deploy from a branch**, then `gh-pages` and `/ (root)`.
