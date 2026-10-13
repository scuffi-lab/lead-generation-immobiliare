#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Rigenera output/ (home, /immobili/, le singole schede, sitemap.xml) a partire
dai file in data/listings/*.json. Non tocca il server: solo file locali.

Uso:
    python build.py
"""
import datetime
import json
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as c

MANIFEST_PATH = c.OUTPUT_DIR / ".manifest.json"


def load_manifest():
    if MANIFEST_PATH.exists():
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    return {"html": [], "img": []}


def save_manifest(manifest):
    MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def clean_stale(old_manifest, keep_html, keep_img):
    """Rimuove i file generati in una build precedente che oggi non servono più
    (annuncio rimosso o rinominato)."""
    removed = []
    for rel in old_manifest.get("html", []):
        if rel not in keep_html:
            p = c.OUTPUT_DIR / rel
            if p.exists():
                p.unlink()
                removed.append(rel)
    for rel in old_manifest.get("img", []):
        if rel not in keep_img:
            p = c.OUTPUT_DIR / rel
            if p.exists():
                p.unlink()
                removed.append(rel)
    return removed


def build_detail_page(listing):
    template = c.read_template("detail.html")
    tokens = {
        "SEO_TITLE": listing["seo_title"],
        "META_DESCRIPTION": c.html_escape(listing.get("meta_description", listing["descrizione"][0])),
        "CANONICAL_URL": c.canonical_url(listing),
        "OG_DESCRIPTION": c.html_escape(listing.get("og_description", listing["descrizione"][0])),
        "OG_IMAGE": f"{c.SITE}/immobili/img/{listing['foto'][0]['file']}",
        "JSONLD": c.jsonld_detail(listing),
        "WA_LINK": c.wa_link(listing),
        "BREADCRUMB_LABEL": c.html_escape(c.breadcrumb_label(listing)),
        "TAG_LABEL": c.tag_label(listing),
        "COMUNE": c.html_escape(listing["comune"]),
        "TITLE_LINE1": c.html_escape(listing["title_line1"]),
        "TITLE_EM": c.html_escape(listing["title_em"]),
        "PRICE_HTML": c.price_html(listing),
        "STATUS_LABEL": c.html_escape(c.status_line(listing)),
        "GALLERY_HTML": c.gallery_html(listing),
        "DESCRIPTION_HTML": c.description_html(listing),
        "SPEC_ROWS_HTML": c.spec_rows_html(listing),
        "REQUISITI_HTML": c.requisiti_html(listing),
    }
    return c.fill(template, tokens)


def build_status_section(status, listings):
    cards = []
    for i, l in enumerate(listings):
        loading = "eager" if i == 0 else "lazy"
        cards.append(c.card_html(l, loading=loading))
    return (
        '  <section class="section">\n'
        '    <div class="wrap">\n'
        '      <div class="section-head">\n'
        f'        <h2>{c.SECTION_TITLES[status]}</h2>\n'
        f'        <p>{c.SECTION_SUBTITLES[status]}</p>\n'
        '      </div>\n'
        '      <div class="listing-grid">\n'
        + "\n".join(cards) +
        '\n      </div>\n'
        '    </div>\n'
        '  </section>'
    )


def build_immobili_index(listings):
    template = c.read_template("immobili_index.html")
    if listings:
        sections = []
        for status in ("affitto", "vendita"):
            group = [l for l in listings if l["status"] == status]
            if group:
                sections.append(build_status_section(status, group))
        sections_html = "\n\n".join(sections)
        og_image = f"{c.SITE}/immobili/img/{listings[0]['foto'][0]['file']}"
    else:
        empty = c.read_template("empty_state.html")
        sections_html = (
            '  <section class="section">\n'
            '    <div class="wrap">\n' + empty + '    </div>\n  </section>'
        )
        og_image = f"{c.SITE}/og-image.png"

    tokens = {
        "STATUS_SECTIONS_HTML": sections_html,
        "JSONLD": c.jsonld_index(listings),
        "OG_IMAGE": og_image,
    }
    return c.fill(template, tokens)


def build_home_fragment(top_listings):
    if top_listings:
        cards = "\n".join(c.card_html(l, loading="lazy") for l in top_listings)
    else:
        cards = c.read_template("empty_state.html")
    template = c.read_template("home_base.html")
    return c.fill(template, {"HOME_CARDS_HTML": cards})


def build_sitemap(listings):
    template = c.read_template("sitemap_static.xml")
    today = datetime.date.today().isoformat()
    blocks = [
        "  <url>\n"
        f"    <loc>{c.SITE}/immobili/</loc>\n"
        f"    <lastmod>{today}</lastmod>\n"
        "    <changefreq>weekly</changefreq>\n"
        "    <priority>0.9</priority>\n"
        "  </url>"
    ]
    for l in listings:
        blocks.append(
            "  <url>\n"
            f"    <loc>{c.canonical_url(l)}</loc>\n"
            f"    <lastmod>{l.get('date_posted', today)}</lastmod>\n"
            "    <changefreq>weekly</changefreq>\n"
            "    <priority>0.8</priority>\n"
            "  </url>"
        )
    return c.fill(template, {"IMMOBILI_URLS": "\n".join(blocks)})


def main():
    listings = c.load_all_listings(available_only=True)
    old_manifest = load_manifest()

    (c.OUTPUT_DIR / "immobili" / "img").mkdir(parents=True, exist_ok=True)

    keep_html = set()
    keep_img = set()

    # schede singole + foto
    for l in listings:
        html = build_detail_page(l)
        rel_html = f"immobili/{l['slug']}.html"
        (c.OUTPUT_DIR / rel_html).write_text(html, encoding="utf-8")
        keep_html.add(rel_html)

        src_dir = c.DATA_DIR / l["slug"] / "img"
        for foto in l["foto"]:
            src = src_dir / foto["file"]
            if not src.exists():
                raise c.ListingError(f"Foto mancante per {l['slug']}: {src}")
            rel_img = f"immobili/img/{foto['file']}"
            dst = c.OUTPUT_DIR / rel_img
            shutil.copyfile(src, dst)
            keep_img.add(rel_img)

    # /immobili/
    (c.OUTPUT_DIR / "immobili" / "index.html").write_text(
        build_immobili_index(listings), encoding="utf-8"
    )

    # home (rigenera index.html per intero, dal master templates/home_base.html)
    top = listings[:3]
    (c.OUTPUT_DIR / "index.html").write_text(build_home_fragment(top), encoding="utf-8")

    # sitemap
    (c.OUTPUT_DIR / "sitemap.xml").write_text(build_sitemap(listings), encoding="utf-8")

    removed = clean_stale(old_manifest, keep_html, keep_img)

    manifest = {"html": sorted(keep_html), "img": sorted(keep_img)}
    save_manifest(manifest)

    print(f"Build completata: {len(listings)} annunci pubblicati.")
    for l in listings:
        print(f"  - [{l['status']}] {l['slug']}  ({'disponibile' if l.get('available', True) else 'NASCOSTO'})")
    if removed:
        print("File rimossi (non più referenziati):")
        for r in removed:
            print(f"  - {r}")


if __name__ == "__main__":
    try:
        main()
    except c.ListingError as e:
        print(f"ERRORE: {e}", file=sys.stderr)
        sys.exit(1)
