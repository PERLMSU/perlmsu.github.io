"""
Pelican plugin: accessible_tables

Post-processes rendered HTML at build time to improve accessibility without
requiring authors to write raw HTML in Markdown content files.

Table fixes:
  - Adds scope="col" to every <th> in <thead>
  - Promotes the first <td> in each <tbody> row to <th scope="row"> so that
    screen readers can associate each row's data cells with their row label

Jump-nav fix:
  - Any <p> whose first child is <strong>Jump to:</strong> is replaced with a
    <nav aria-label="Page sections"> containing the same content, giving
    landmark navigation to screen reader users

Footnote relocation:
  - The markdown footnotes extension renders all footnotes in a single <div
    class="footnote"> at the end of the document. This moves each footnote
    block to sit immediately after the table whose cells first reference it,
    so the note text appears in context rather than at the end of the page.
"""

from bs4 import BeautifulSoup
from pelican import signals


def make_tables_accessible(soup):
    modified = False

    for table in soup.find_all("table"):
        for th in table.select("thead th"):
            if not th.get("scope"):
                th["scope"] = "col"
                modified = True

        for row in table.select("tbody tr"):
            cells = row.find_all(["td", "th"])
            if cells and cells[0].name == "td":
                cells[0].name = "th"
                cells[0]["scope"] = "row"
                modified = True

        # Strip redundant <strong> wrappers from row header cells — <th> already
        # carries semantic weight and CSS sets font-weight: normal on these cells
        for th in table.select("tbody th[scope=row]"):
            for strong in th.find_all("strong"):
                strong.unwrap()
                modified = True

    return modified


def make_jump_navs_accessible(soup):
    modified = False

    for p in soup.find_all("p"):
        first = next((c for c in p.children if getattr(c, "name", None)), None)
        if first and first.name == "strong" and first.get_text(strip=True) == "Jump to:":
            nav = soup.new_tag("nav", attrs={"aria-label": "Page sections"})
            p.replace_with(nav)
            nav.append(p)
            modified = True

    return modified


def relocate_footnotes(soup):
    footnote_div = soup.find("div", class_="footnote")
    if not footnote_div:
        return False

    # Find the first table that contains a footnote reference link
    anchor_table = None
    for table in soup.find_all("table"):
        if table.find("a", class_="footnote-ref"):
            anchor_table = table
            break

    if not anchor_table:
        return False

    footnote_div.extract()
    anchor_table.insert_after(footnote_div)
    return True


def process_content(content_object):
    if not getattr(content_object, "_content", None):
        return

    soup = BeautifulSoup(content_object._content, "html.parser")

    changed = make_tables_accessible(soup)
    changed |= make_jump_navs_accessible(soup)
    if getattr(content_object, "relocate_footnotes", "").lower() == "true":
        changed |= relocate_footnotes(soup)

    if changed:
        content_object._content = str(soup)


def register():
    signals.content_object_init.connect(process_content)
