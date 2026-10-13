# -*- coding: utf-8 -*-
"""
Funzioni condivise per generare le pagine immobili di studioboldrini.online
a partire dai file JSON in data/listings/.
"""
import json
import re
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "listings"
TEMPLATES_DIR = ROOT / "templates"
OUTPUT_DIR = ROOT / "output"

SITE = "https://studioboldrini.online"
WA_NUMBER = "393703791000"

STATUS_LABELS = {"affitto": "Affitto", "vendita": "Vendita"}
CONTRACT_LABELS = {"affitto": "Affitto residenziale", "vendita": "Vendita"}
SECTION_TITLES = {"affitto": "In affitto", "vendita": "In vendita"}
SECTION_SUBTITLES = {
    "affitto": "Verifica urbanistica e catastale fatta prima di pubblicare. Le visite le facciamo noi, di persona.",
    "vendita": "Stessa verifica, stessa cura. Trattiamo poche vendite alla volta per seguirle fino al rogito.",
}


class ListingError(ValueError):
    pass


# ---------------------------------------------------------------- utilità

def html_escape(text):
    if text is None:
        return ""
    return (
        str(text)
        .replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace('"', "&quot;")
    )


def bold(text):
    """Converte **testo** in <b>testo</b>. Il resto del testo non viene escaped
    perché il contenuto è scritto da noi (non input di terzi)."""
    if text is None:
        return ""
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)


def read_template(name):
    return (TEMPLATES_DIR / name).read_text(encoding="utf-8")


def fill(template_text, tokens):
    out = template_text
    for key, value in tokens.items():
        out = out.replace("{{%s}}" % key, value)
    return out


# ---------------------------------------------------------------- listing

REQUIRED_FIELDS = [
    "slug", "status", "seo_title", "title_line1", "title_em",
    "comune", "zona", "tipologia", "prezzo", "descrizione", "foto",
]


def validate_listing(data, source_desc=""):
    missing = [f for f in REQUIRED_FIELDS if f not in data or data[f] in (None, "", [])]
    if missing:
        raise ListingError(f"{source_desc}: campi obbligatori mancanti: {', '.join(missing)}")
    if data["status"] not in ("affitto", "vendita"):
        raise ListingError(f"{source_desc}: status deve essere 'affitto' o 'vendita', trovato {data['status']!r}")
    if not re.match(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$", data["slug"]):
        raise ListingError(f"{source_desc}: slug non valido (usa solo minuscole, numeri e trattini): {data['slug']!r}")
    if not data["foto"]:
        raise ListingError(f"{source_desc}: serve almeno una foto")
    for f in data["foto"]:
        if "file" not in f or "didascalia" not in f or "alt" not in f:
            raise ListingError(f"{source_desc}: ogni foto richiede 'file', 'didascalia' e 'alt'")


def load_listing_file(path):
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if "slug" not in data:
        data["slug"] = Path(path).stem
    validate_listing(data, source_desc=str(path))
    return data


def load_all_listings(available_only=False):
    listings = []
    if not DATA_DIR.exists():
        return listings
    for p in sorted(DATA_DIR.glob("*.json")):
        data = load_listing_file(p)
        if available_only and not data.get("available", True):
            continue
        listings.append(data)
    listings.sort(key=lambda l: l.get("date_posted", ""), reverse=True)
    return listings


# ---------------------------------------------------------------- campi derivati

def tag_label(listing):
    return STATUS_LABELS[listing["status"]]


def contract_label(listing):
    return CONTRACT_LABELS[listing["status"]]


def price_html(listing):
    prezzo = f"{listing['prezzo']:,}".replace(",", ".")
    if listing["status"] == "affitto":
        unita = listing.get("prezzo_unita") or "mese"
        return f"{prezzo} € <small>/ {unita}</small>"
    return f"{prezzo} €"


def price_plain(listing):
    prezzo = f"{listing['prezzo']:,}".replace(",", ".")
    if listing["status"] == "affitto":
        unita = listing.get("prezzo_unita") or "mese"
        return f"{prezzo} € / {unita}"
    return f"{prezzo} €"


def price_compact(listing):
    """Come price_plain ma senza spazi attorno alla barra (per meta/wa-text)."""
    prezzo = f"{listing['prezzo']:,}".replace(",", ".")
    if listing["status"] == "affitto":
        unita = listing.get("prezzo_unita") or "mese"
        return f"{prezzo} €/{unita}"
    return f"{prezzo} €"


def canonical_url(listing):
    return f"{SITE}/immobili/{listing['slug']}.html"


def wa_link(listing):
    custom = listing.get("wa_text")
    if custom:
        msg = custom
    else:
        verbo = "in affitto" if listing["status"] == "affitto" else "in vendita"
        msg = (
            f"Ciao! Ho visto sul sito {listing['tipologia'].lower()} {verbo} a {listing['comune']} "
            f"({listing['zona'].lower()}, {price_compact(listing)}). Vorrei avere maggiori informazioni."
        )
    return f"https://wa.me/{WA_NUMBER}?text={urllib.parse.quote(msg)}"


def wa_link_generic():
    msg = ("Ciao! Vorrei mettermi in contatto con Studio Immobiliare Boldrini. "
           "Ecco una breve presentazione, cosa sto cercando e gli orari migliori per richiamarmi:")
    return f"https://wa.me/{WA_NUMBER}?text={urllib.parse.quote(msg)}"


def status_line(listing):
    disp = listing.get("disponibilita", "Disponibile")
    return f"Disponibile · {disp[0].lower()+disp[1:]}" if not disp.lower().startswith("dispon") else disp


def breadcrumb_label(listing):
    return listing.get("breadcrumb_label") or f"{listing['tipologia']} a {listing['comune']}"


# ---------------------------------------------------------------- blocchi HTML

def description_html(listing):
    paras = [f"        <p>{bold(html_escape_keep_bold(p))}</p>" for p in listing["descrizione"]]
    return "\n".join(paras)


def html_escape_keep_bold(text):
    """Escape HTML ma preserva i marcatori **...** che bold() convertirà dopo."""
    escaped = html_escape(text)
    # html_escape non tocca gli asterischi, quindi non serve altro
    return escaped


def spec_rows_html(listing):
    rows = [
        ("Tipologia", listing["tipologia"]),
        ("Contratto", contract_label(listing)),
        ("Canone" if listing["status"] == "affitto" else "Prezzo", price_plain(listing)),
        ("Zona", listing["zona"]),
    ]
    if listing.get("piano"):
        rows.append(("Piano", listing["piano"]))
    if listing.get("mq"):
        rows.append(("Superficie", f"{listing['mq']} m²"))
    if listing.get("stato_immobile"):
        rows.append(("Stato", listing["stato_immobile"]))
    if listing.get("impianti"):
        rows.append(("Impianti", listing["impianti"]))
    if listing.get("parcheggio"):
        rows.append(("Parcheggio", listing["parcheggio"]))
    if listing.get("ape"):
        rows.append(("Classe energetica", listing["ape"]))
    if listing.get("disponibilita"):
        rows.append(("Disponibilità", listing["disponibilita"]))
    return "\n".join(
        f'          <div class="spec-row"><dt>{html_escape(k)}</dt><dd>{html_escape(v)}</dd></div>'
        for k, v in rows
    )


def requisiti_html(listing):
    testo = listing.get("requisiti_testo")
    if not testo:
        return ""
    return (
        '\n        <div class="req">\n'
        '          <h3>Cosa chiediamo</h3>\n'
        f'          <p>{bold(html_escape_keep_bold(testo))}</p>\n'
        '        </div>\n'
    )


def gallery_html(listing):
    figs = []
    for i, foto in enumerate(listing["foto"]):
        loading = "eager" if i == 0 else "lazy"
        figs.append(
            '    <figure>\n'
            f'      <img src="/immobili/img/{foto["file"]}" width="1200" height="1600" '
            f'alt="{html_escape(foto["alt"])}" loading="{loading}">\n'
            f'      <figcaption>{html_escape(foto["didascalia"])}</figcaption>\n'
            '    </figure>'
        )
    return "\n".join(figs)


def facts_html(listing, indent="                "):
    facts = listing.get("facts") or []
    return "\n".join(f"{indent}<span>{bold(html_escape_keep_bold(f))}</span>" for f in facts)


def card_html(listing, loading="lazy"):
    template = read_template("card.html")
    first_photo = listing["foto"][0]
    thumb_alt = first_photo.get("card_alt") or first_photo["alt"]
    tokens = {
        "SLUG": listing["slug"],
        "THUMB_FILE": first_photo["file"],
        "THUMB_ALT": html_escape(thumb_alt),
        "LOADING": loading,
        "TAG_LABEL": tag_label(listing),
        "CARD_TITLE": html_escape(listing["title_line1"].rstrip(",")),
        "COMUNE": html_escape(listing["comune"]),
        "ZONA": html_escape(listing["zona"]),
        "FACTS_HTML": facts_html(listing),
        "PRICE_HTML": price_html(listing),
        "SHARE_URL": canonical_url(listing),
        "SHARE_TITLE": html_escape(listing["title_line1"].rstrip(",")),
    }
    return fill(template, tokens)


# ---------------------------------------------------------------- JSON-LD

def jsonld_detail(listing):
    image_urls = [f"{SITE}/immobili/img/{f['file']}" for f in listing["foto"]]
    amenity = [
        {"@type": "LocationFeatureSpecification", "name": a, "value": True}
        for a in listing.get("amenities", [])
    ]
    amenity.append({
        "@type": "LocationFeatureSpecification",
        "name": "Ascensore",
        "value": bool(listing.get("ascensore", False)),
    })

    about = {
        "@type": listing.get("schema_type", "Apartment"),
        "name": listing["title_line1"].rstrip(","),
        "petsAllowed": bool(listing.get("pets_allowed", False)),
        "address": {
            "@type": "PostalAddress",
            "addressLocality": listing["comune"],
            "addressRegion": listing.get("provincia", "PI"),
            "postalCode": listing.get("cap", ""),
            "addressCountry": "IT",
        },
        "amenityFeature": amenity,
    }
    if listing.get("vani"):
        about["numberOfRooms"] = listing["vani"]
    if listing.get("piano_numero"):
        about["floorLevel"] = str(listing["piano_numero"])
    if listing.get("mq"):
        about["floorSize"] = {"@type": "QuantitativeValue", "value": listing["mq"], "unitCode": "MTK"}

    offer = {
        "@type": "Offer",
        "price": str(listing["prezzo"]),
        "priceCurrency": "EUR",
        "availability": "https://schema.org/InStock",
        "businessFunction": (
            "https://purl.org/goodrelations/v1#LeaseOut"
            if listing["status"] == "affitto"
            else "https://purl.org/goodrelations/v1#Sell"
        ),
        "seller": {"@id": f"{SITE}/#agenzia"},
    }
    if listing["status"] == "affitto":
        offer["priceSpecification"] = {
            "@type": "UnitPriceSpecification",
            "price": str(listing["prezzo"]),
            "priceCurrency": "EUR",
            "unitCode": "MON",
            "billingIncrement": 1,
        }

    graph = [
        {
            "@type": "RealEstateListing",
            "@id": f"{canonical_url(listing)}#annuncio",
            "url": canonical_url(listing),
            "name": listing["seo_title"],
            "description": listing.get("jsonld_description", listing["descrizione"][0]),
            "datePosted": listing.get("date_posted", ""),
            "inLanguage": "it-IT",
            "image": image_urls,
            "provider": {"@id": f"{SITE}/#agenzia"},
            "about": about,
            "offers": offer,
        },
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
                {"@type": "ListItem", "position": 2, "name": "Immobili", "item": f"{SITE}/immobili/"},
                {"@type": "ListItem", "position": 3, "name": breadcrumb_label(listing)},
            ],
        },
    ]
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2)


def jsonld_index(listings):
    items = [
        {
            "@type": "ListItem",
            "position": i + 1,
            "url": canonical_url(l),
            "name": l["seo_title"],
        }
        for i, l in enumerate(listings)
    ]
    graph = [
        {
            "@type": "CollectionPage",
            "@id": f"{SITE}/immobili/#vetrina",
            "url": f"{SITE}/immobili/",
            "name": "Immobili — Studio Immobiliare Boldrini",
            "description": "Gli immobili in affitto e in vendita seguiti da Studio Immobiliare Boldrini nel Comprensorio del Cuoio.",
            "inLanguage": "it-IT",
            "isPartOf": {"@id": f"{SITE}/#sito"},
            "about": {"@id": f"{SITE}/#agenzia"},
        },
        {
            "@type": "ItemList",
            "itemListOrder": "https://schema.org/ItemListOrderDescending",
            "numberOfItems": len(items),
            "itemListElement": items,
        },
        {
            "@type": "BreadcrumbList",
            "itemListElement": [
                {"@type": "ListItem", "position": 1, "name": "Home", "item": f"{SITE}/"},
                {"@type": "ListItem", "position": 2, "name": "Immobili"},
            ],
        },
    ]
    return json.dumps({"@context": "https://schema.org", "@graph": graph}, ensure_ascii=False, indent=2)
