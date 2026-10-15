"""One-shot migration of the legacy bronkhorsterkermis.nl site into this Astro project.

Reads the legacy copy (pages/*.html, DATABASE.sql, images, downloads) and writes:
  src/content/jaren/<jaar>.md      kermisjaren shown on the home page
  src/content/pages/<slug>.md      ordinary pages (markdown drafts, hand-edited afterwards)
  src/data/koningen.json           galerij der koningen
  src/data/documenten.json         programma's, uitnodigingen, notulen (activiteiten page)
  src/data/fotoarchief.json        historic photo archive
  src/assets/media/...             images (downscaled to MAX_EDGE)
  public/downloads/...             referenced downloads (same URLs as the old site)

It is a migration aid, not part of the build: after the first run the generated files are
hand-edited and committed, so re-running overwrites those edits. Run with --force to do so.

Usage: python build_content.py <legacy-site-dir> [--force]
"""

import json
import re
import shutil
import sys
import unicodedata
from pathlib import Path
from urllib.parse import unquote

import yaml
from bs4 import BeautifulSoup, Comment
from markdownify import markdownify
from PIL import Image, ImageFile, ImageOps

# A few legacy JPEGs are truncated by some bytes; browsers show them fine, so should we.
ImageFile.LOAD_TRUNCATED_IMAGES = True

sys.path.insert(0, str(Path(__file__).parent))
from parse_home import cell_record  # noqa: E402
from sqldump import read_tables  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
MEDIA = ROOT / "src" / "assets" / "media"
DOWNLOADS = ROOT / "public" / "downloads"
MAX_EDGE = 2000

LEGACY: Path


# ---------------------------------------------------------------- helpers

def slugify(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")


def find_legacy(rel: str) -> Path:
    """Resolve a legacy URL path case-insensitively (the old host was forgiving, Linux isn't)."""
    rel = unquote(rel).lstrip("/")
    p = LEGACY / rel
    if p.exists():
        return p
    folder = p.parent
    for cand in folder.iterdir():
        if cand.name.lower() == p.name.lower():
            return cand
    raise FileNotFoundError(rel)


def media(rel: str, folder: str, name: str | None = None) -> str:
    """Copy a legacy image into src/assets/media/<folder>/, downscaled; return its CMS path."""
    src = find_legacy(rel)
    stem = slugify(name or src.stem)
    ext = src.suffix.lower().replace(".jpeg", ".jpg")
    dest = MEDIA / folder / f"{stem}{ext}"
    dest.parent.mkdir(parents=True, exist_ok=True)
    if ext in (".jpg", ".png"):
        with Image.open(src) as im:
            im = ImageOps.exif_transpose(im)
            if max(im.size) > MAX_EDGE:
                im.thumbnail((MAX_EDGE, MAX_EDGE), Image.LANCZOS)
            if ext == ".jpg":
                im.convert("RGB").save(dest, quality=85, optimize=True, progressive=True)
            else:
                im.save(dest, optimize=True)
    else:
        shutil.copyfile(src, dest)
    return f"/media/{folder}/{dest.name}"


def download(rel: str) -> str:
    """Copy a legacy download to public/downloads/ under its original name (keeps old URLs)."""
    src = find_legacy(rel)
    DOWNLOADS.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, DOWNLOADS / src.name)
    return f"/downloads/{src.name}"


def tidy(text: str) -> str:
    text = text.replace(" ", " ")
    text = re.sub(r"(\d) (e|ste|de)\b", r"\1\2", text)  # "3 e ronde" from <sup>
    return re.sub(r"\s+", " ", text).strip()


def write_md(path: Path, front: dict, body: str = ""):
    path.parent.mkdir(parents=True, exist_ok=True)
    fm = yaml.safe_dump(front, allow_unicode=True, sort_keys=False, width=1000)
    path.write_text(f"---\n{fm}---\n{body.strip()}\n" if body.strip() else f"---\n{fm}---\n",
                    encoding="utf-8")


def write_json(path: Path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def html_to_md(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for c in soup.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()
    for t in soup.find_all(["style", "script", "head", "title", "meta", "iframe"]):
        t.decompose()
    for t in soup.find_all(["table", "tbody", "tr", "td", "span", "font", "div", "html", "body"]):
        t.unwrap()
    md = markdownify(str(soup), heading_style="ATX", strip=["u"])
    md = md.replace(" ", " ")
    md = re.sub(r"[ \t]+\n", "\n", md)
    md = re.sub(r"\n{3,}", "\n\n", md)
    return md.strip()


# ---------------------------------------------------------------- kermisjaren (home page)

# (row, cell) references into the parsed home page, newest year first.
# items: cells whose image+caption become one item; captions: separate caption cell when the
# old layout put captions in the next table row; album: cell holding the Google Drive link.
JAREN = {
    2025: dict(items=[(0, 0), (0, 2)], album=(0, 1)),
    2024: dict(items=[(1, 0), (1, 2)], album=(1, 1)),
    2023: dict(items=[(2, 0), (2, 2)], album=(2, 1)),
    2022: dict(items=[(3, 0)], album=(3, 1), body=(3, 2)),
    2019: dict(items=[(4, 0), (4, 2)], album=(4, 1)),
    2018: dict(items=[(5, 0), (5, 2)], album=(5, 1)),
    2017: dict(items=[(6, 0), (6, 2)], album=(6, 1)),
    2016: dict(items=[(7, 0), (7, 2)], album=(7, 1)),
    2015: dict(items=[(8, 0), (8, 2)], album=(8, 1)),
    2014: dict(items=[(9, 0), (9, 2)], album=(9, 1)),
    2013: dict(items=[(11, 0), (10, 1), (11, 1)]),
    2012: dict(items=[(12, 1), (12, 0)]),
    2011: dict(items=[(13, 0), (13, 1)], captions=[(14, 0), (14, 1)]),
    2010: dict(items=[(15, 0), (15, 1), (15, 2)], captions=[(16, 0), (16, 1), (16, 2)]),
    2009: dict(items=[(17, 0), (17, 1), (17, 2)]),
    2008: dict(items=[(18, 0)]),
    2007: dict(items=[(20, 0), (21, 0), (19, 0), (19, 1), (21, 1)]),
}

# Image overrides where the old page linked a thumbnail to something other than the full image.
FULL_IMAGE = {
    "images/M4110022_klein.JPG": "images/M4110022.JPG",
    "images/margoengelaar2007_klein.jpg": "images/margoengelaar2007.jpg",
}

JAAR_BODY_EXTRA = {
    2013: "Omroep Gelderland: [Schutterskoning Bronkhorst zonder ketting]"
          "(http://www.omroepgelderland.nl/web/nieuws-1/2035589/schutterskoning-bronkhorst-zonder-ketting.htm)",
}


def build_jaren(home_html: Path):
    soup = BeautifulSoup(home_html.read_text(encoding="utf-8"), "html.parser")
    for c in soup.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()
    rows = []
    for tr in soup.find_all("tr"):
        if tr.find("tr"):
            continue
        tds = tr.find_all("td", recursive=False)
        cells = [(td, cell_record(td)) for td in tds]
        cells = [c for c in cells if c[1]["images"] or c[1]["text"] or c[1]["links"]]
        if cells:
            rows.append(cells)

    for year, spec in JAREN.items():
        items = []
        captions = spec.get("captions")
        for n, (r, c) in enumerate(spec["items"]):
            rec = rows[r][c][1]
            caption = tidy(rows[captions[n][0]][captions[n][1]][1]["text"]) if captions else tidy(rec["text"])
            caption = caption.replace("Zie galerij der Koningen.", "").strip()
            for k, img in enumerate(rec["images"]):
                full = FULL_IMAGE.get(unquote(img["full"]), img["full"])
                items.append({
                    "foto": media(full, f"jaren/{year}", f"{year}-{Path(unquote(full)).stem}"),
                    "bijschrift": caption if k == 0 else "",
                })
            if not rec["images"] and caption:
                items.append({"bijschrift": caption})
        front = {"jaar": year}
        if "album" in spec:
            album = rows[spec["album"][0]][spec["album"][1]][1]
            front["fotoalbum"] = album["links"][0]["href"]
        front["items"] = items
        body = ""
        if "body" in spec:
            body = html_to_md(str(rows[spec["body"][0]][spec["body"][1]][0].decode_contents()))
        if year in JAAR_BODY_EXTRA:
            body = (body + "\n\n" + JAAR_BODY_EXTRA[year]).strip()
        write_md(ROOT / "src/content/jaren" / f"{year}.md", front, body)
    print(f"jaren: {len(JAREN)}")


# ---------------------------------------------------------------- koningen

# Hard-coded in the old index.php below the gallery (years without a photo).
KONINGEN_EXTRA = [
    (1962, "M. van Mourik"), (1957, "H. Nijenhuis"), (1956, "G. Harmsen"),
    (1955, "Anton Harmsen en … Harmsen-Vriezekolk"), (1951, "W. Hulshof"), (1948, "G. Harmsen"),
    (1947, "?"), (1946, "A. Wiggerink"), (1945, "?"),
    (1938, "Gerrit de Wit en Nolda Wentink"), (1937, "Hein Knaake en Johanna van Veldhuizen"),
    (1936, "Willem Hulshof en Jantje Flamma"), (1935, "B. Wolff"),
    (1934, "Anton van Viegen en Marie Hissink"), (1933, "Hendrik Ovink en Riek Boogman"),
    (1932, "Bart Wolff en Jantje Wolf-Keurhorst"), (1931, "J.E. Wolff"),
    (1930, "Willem Hulshof en Jantje Flamma"), (1929, "J. Hulshof"),
    (1928, "E.J.Wolf en Jans Ovink"), (1927, "Arend en Mies Wiggerink"),
    (1926, "Gerrit Wolff en Aaltje Mennink"), (1925, "A. Mennink en Hanna van Veldhuizen"),
    (1924, "Gerrit Wolf en Jeanette Aussen"), (1923, "Alexander Saalmink en Dina Meenink"),
    (1922, "Ad Vrendenberg en Christien Wiemer"), (1921, "Jacob Saalmink en J.Harmsen"),
    (1920, "J.Wolf en J.Meutstege"), (1919, "Adriaan Meutstege en Jans Ovink"),
    (1913, "Hendrik van Veldhuizen en Geertje Meutstege"),
    (1912, "Derk Gerritsen en Grada Meutstege"),
    (1911, "Hendrik van Veldhuizen (Onderstraat 6)"), (1910, "Johan Wolf"),
    (1893, "E. Hendriksen"),
]
KONINGEN_NOTES = {
    1927: "Eerste jaar dat gehuwde mannen mogen schieten.",
}
GEEN_KERMIS = [
    dict(jaar=2020, tot=2021, opmerking="Geen kermis i.v.m. de coronapandemie."),
    dict(jaar=1939, tot=1944, opmerking="Geen kermis i.v.m. de Tweede Wereldoorlog."),
    dict(jaar=1914, tot=1918, opmerking="Geen kermis i.v.m. de Eerste Wereldoorlog."),
]


def build_koningen(tables):
    by_year = {}
    for r in tables["galerij"]:
        if not r["name"]:
            continue  # the 2020 placeholder row
        e = {"jaar": r["year"], "koning": r["name"]}
        if r["file"]:
            e["foto"] = media(f"galerij/{r['file']}", "koningen", f"{r['year']}-{r['name']}")
        by_year[r["year"]] = e
    for year, names in KONINGEN_EXTRA:
        e = by_year.setdefault(year, {"jaar": year, "koning": names})
        if len(names) > len(e["koning"]):
            e["koning"] = names
    for year, note in KONINGEN_NOTES.items():
        by_year[year]["opmerking"] = note
    by_year[1955]["video"] = download("downloads/ezgif-3-4923bc5ef9.mp4")
    by_year[1955]["opmerking"] = "Fragment uit het Polygoon-journaal van 1955."
    entries = list(by_year.values()) + GEEN_KERMIS
    entries.sort(key=lambda e: e["jaar"], reverse=True)
    write_json(ROOT / "src/data/koningen.json", entries)
    print(f"koningen: {len(entries)}")


# ---------------------------------------------------------------- documenten (activiteiten)

DOC_TYPES = ["Programma kermis", "Uitnodiging rekening & verantwoording",
             "Notulen rekening & verantwoording", "Winterkostmaaltijd / overig"]


def build_documenten(html_path: Path):
    soup = BeautifulSoup(html_path.read_text(encoding="utf-8"), "html.parser")
    for c in soup.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()
    docs = []
    for tr in soup.find_all("tr"):
        tds = tr.find_all("td", recursive=False)
        for col, td in enumerate(tds):
            for a in td.find_all("a"):
                href = a.get("href", "")
                if not href.startswith("downloads/"):
                    continue
                label = tidy(a.get_text(" ", strip=True))
                year = int(re.search(r"(19|20)\d\d", label + " " + href).group(0))
                kind = DOC_TYPES[3] if len(tds) == 1 else DOC_TYPES[min(col, 3)]
                try:
                    url = download(href)
                except FileNotFoundError:
                    print(f"  missing download: {href}")
                    continue
                d = {"jaar": year, "soort": kind, "bestand": url}
                if not re.fullmatch(r"\d{4}", label):
                    d["titel"] = label
                docs.append(d)
    write_json(ROOT / "src/data/documenten.json", docs)
    print(f"documenten: {len(docs)}")


# ---------------------------------------------------------------- pages

# legacy id -> (slug, title, order, source). source: "db" or a file in legacy pages/.
PAGES = {
    1: ("home", "Home", 0, "home.html"),
    4: ("activiteiten", "Activiteiten", 1, "activiteiten.html"),
    5: ("sponsoren-golfbaan", "Sponsoren Golfbaan", 2, "db"),
    6: ("oorsprong-schutterij", "Oorsprong Schutterij", 3, "db"),
    7: ("schuttersfeest", "Schuttersfeest", 4, "db"),
    8: ("foto-archief", "Foto Archief", 5, "db"),
    9: ("galerij-der-koningen", "Galerij der Koningen", 6, "db"),
    12: ("bielemans", "Bielemans", 7, "bielemans.html"),
    11: ("het-vaandel", "Het Vaandel", 8, "db"),
    13: ("kleine-schutterij", "Kleine Schutterij", 9, "db"),
    3: ("bestuur", "Bestuur", 10, "db"),
    15: ("links", "Links", 11, "db"),
}
# Pages whose body comes from structured data rendered by the template.
BIJLAGE = {1: "kermisjaren", 4: "documenten", 8: "fotoarchief", 9: "koningen"}


def rewrite_assets(html: str, slug: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for img in soup.find_all("img"):
        a = img.find_parent("a")
        src = img.get("src", "")
        href = a.get("href", "") if a else ""
        full = href if re.search(r"\.(jpe?g|png|gif)$", href, re.I) else src
        full = re.sub(r"^https?://www\.bronkhorsterkermis\.nl/", "", full)
        try:
            img["src"] = media(full, f"pages/{slug}")
        except FileNotFoundError:
            print(f"  missing image on {slug}: {full}")
            img.decompose()
            continue
        if a is not None and full == href:
            a.unwrap()
    for a in soup.find_all("a"):
        href = a.get("href", "")
        if href.startswith("downloads/"):
            try:
                a["href"] = download(href)
            except FileNotFoundError:
                print(f"  missing download on {slug}: {href}")
    return str(soup)


def build_pages(tables):
    db = {p["id"]: p for p in tables["pages"]}
    for pid, (slug, title, order, source) in PAGES.items():
        if pid in BIJLAGE and pid != 9:
            html = ""  # body replaced by structured data; intro text added by hand
        elif source == "db":
            html = db[pid]["content"]
        else:
            html = (LEGACY / "pages" / source).read_text(encoding="utf-8")
        body = html_to_md(rewrite_assets(html, slug)) if html else ""
        front = {"titel": title, "volgorde": order}
        if pid in BIJLAGE:
            front["bijlage"] = BIJLAGE[pid]
        front["legacyId"] = pid
        write_md(ROOT / "src/content/pages" / f"{slug}.md", front, body)
    print(f"pages: {len(PAGES)}")


# ---------------------------------------------------------------- foto archief

def build_fotoarchief(html: str):
    """Old layout: a row of two photos followed by a row of two captions."""
    soup = BeautifulSoup(html, "html.parser")
    for c in soup.find_all(string=lambda s: isinstance(s, Comment)):
        c.extract()
    photos, pending = [], []
    for tr in soup.find_all("tr"):
        if tr.find("tr"):
            continue
        cells = [cell_record(td) for td in tr.find_all("td", recursive=False)]
        imgs = [c for c in cells if c["images"]]
        if imgs:
            pending = [img for c in imgs for img in c["images"]]
            continue
        texts = [tidy(c["text"]) for c in cells if tidy(c["text"])]
        if pending and texts:
            for n, img in enumerate(pending):
                photos.append({
                    "foto": media(img["full"].replace("http://www.bronkhorsterkermis.nl/", ""),
                                  "fotoarchief"),
                    "bijschrift": texts[n] if n < len(texts) else "",
                })
            pending = []
        elif texts:
            photos.append({"bijschrift": " ".join(texts)})
    for img in pending:
        photos.append({"foto": media(img["full"], "fotoarchief"), "bijschrift": ""})
    write_json(ROOT / "src/data/fotoarchief.json", photos)
    print(f"fotoarchief: {len(photos)}")


# ---------------------------------------------------------------- main

def main():
    global LEGACY
    LEGACY = Path(sys.argv[1]).resolve()
    if (ROOT / "src/content/pages").exists() and "--force" not in sys.argv:
        sys.exit("Content already migrated (and possibly hand-edited). Use --force to overwrite.")
    sys.stdout.reconfigure(encoding="utf-8")
    tables = read_tables(LEGACY / "DATABASE.sql")
    build_jaren(LEGACY / "pages" / "home.html")
    build_koningen(tables)
    build_documenten(LEGACY / "pages" / "activiteiten.html")
    build_fotoarchief(next(p["content"] for p in tables["pages"] if p["id"] == 8))
    build_pages(tables)


if __name__ == "__main__":
    main()
