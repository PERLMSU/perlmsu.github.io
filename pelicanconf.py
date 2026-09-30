from datetime import date

AUTHOR = "PERL"
SITENAME = "PERL@MSU"
SITEURL = ""
SITELOGO = ""

SITE_DESCRIPTION = """
We study how students learn physics and engage in physics practice, from pre-college to post-graduate.
<br><br>
Want to hear about our seminars, or interested in joining us?<br>
See <a href="/getting-involved/">Getting Involved</a> or<br>
email us at <a href="mailto:perl@msu.edu">perl@msu.edu</a>.
"""

# Theme choice: "msu" or "cerl"
COLOR_SCHEME = "msu"

PATH = "content"
PAGE_PATHS = ["pages"]
ARTICLE_PATHS = ["posts"]
ARTICLE_URL = "news/{date:%Y}/{slug}/"
ARTICLE_SAVE_AS = "news/{date:%Y}/{slug}/index.html"

DIRECT_TEMPLATES = ["news", "news_archive"]
NEWS_SAVE_AS = "news/index.html"
NEWS_ARCHIVE_SAVE_AS = "news/archive/index.html"

# /news/ lists posts from the last NEWS_RECENT_YEARS calendar years (including
# this one); older posts are listed at /news/archive/. Rolls over automatically.
NEWS_RECENT_YEARS = 3
NEWS_ARCHIVE_BEFORE = date.today().year - NEWS_RECENT_YEARS + 1

STATIC_PATHS = ["assets"]

TIMEZONE = "America/Detroit"
DEFAULT_LANG = "en"

THEME = "themes"

# Each item is (label, url) or (label, url, [(label, url), ...]) for a dropdown
MENUITEMS = [
    ("Home", "/"),
    ("People", "/people/"),
    ("Events", "/events/"),
    ("News", "/news/"),
    ("Research", "/research/areas/", [
        ("Research Areas", "/research/areas/"),
        ("Research Projects", "/research/projects/"),
    ]),
    ("Curriculum Development", "/curriculum/"),
    ("Community Partnerships", "/partnerships/"),
    ("Publications", "/pubs/"),
    ("Getting Involved", "/getting-involved/"),
]

PAGE_URL = "{slug}/"
PAGE_SAVE_AS = "{slug}/index.html"

# Disable blog/feed features
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None
AUTHOR_FEED_ATOM = None
AUTHOR_FEED_RSS = None
DEFAULT_PAGINATION = False

# Suppress unused output
ARCHIVES_SAVE_AS = ""
AUTHORS_SAVE_AS = ""
AUTHOR_SAVE_AS = ""
CATEGORIES_SAVE_AS = ""
CATEGORY_SAVE_AS = ""
TAGS_SAVE_AS = ""
TAG_SAVE_AS = ""
INDEX_SAVE_AS = ""

PLUGIN_PATHS = ["plugins"]
PLUGINS = ["pelican.plugins.sitemap", "accessible_tables"]

SITEMAP = {
    "format": "xml",
    "priorities": {"articles": 0.6, "indexes": 0.6, "pages": 0.8},
    "changefreqs": {"articles": "monthly", "indexes": "weekly", "pages": "monthly"},
}

TYPOGRIFY = True

MARKDOWN = {
    "extensions": [
        "markdown.extensions.toc",
        "markdown.extensions.tables",
        "markdown.extensions.fenced_code",
        "markdown.extensions.footnotes",
        "markdown.extensions.abbr",
    ],
    "extension_configs": {
        "markdown.extensions.toc": {
            "anchorlink": False,
        },
    },
    "output_format": "html5",
}
