"""Draft extraction of the legacy home page (pages/home.html) into per-cell records.

Prints JSON: a list of rows, each a list of cells {images: [...], text, links: [...]}.
The output is reviewed by hand and turned into src/content/jaren/*.md by build_content.py.
"""

import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup, Comment

IMG_EXT = re.compile(r"\.(jpe?g|png|gif)$", re.I)


def cell_record(td):
    images = []
    for img in td.find_all("img"):
        a = img.find_parent("a")
        href = a.get("href") if a else None
        full = href if href and IMG_EXT.search(href) else img.get("src")
        images.append({"thumb": img.get("src"), "full": full})
    links = [
        {"href": a.get("href"), "text": a.get_text(" ", strip=True)}
        for a in td.find_all("a")
        if a.get("href") and not IMG_EXT.search(a.get("href")) and not a.find("img")
    ]
    text = re.sub(r"\s+", " ", td.get_text(" ", strip=True)).strip()
    return {"images": images, "text": text, "links": links}


def main(path: Path):
    soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
    for c in soup.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()
    rows = []
    for tr in soup.find_all("tr"):
        if tr.find("tr"):  # only innermost rows carry content
            continue
        cells = [cell_record(td) for td in tr.find_all("td", recursive=False)]
        cells = [c for c in cells if c["images"] or c["text"] or c["links"]]
        if cells:
            rows.append(cells)
    sys.stdout.reconfigure(encoding="utf-8")
    json.dump(rows, sys.stdout, ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main(Path(sys.argv[1]))
