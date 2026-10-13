#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Gestione annunci immobiliari di studioboldrini.online.

Comandi:
  python manage.py list
      Elenca tutti gli annunci (anche quelli nascosti con available:false).

  python manage.py add annuncio.json [--no-deploy]
      Aggiunge un nuovo annuncio (o aggiorna uno esistente con lo stesso slug),
      copia le foto, rigenera il sito e lo pubblica.
      Nel json, ogni foto può avere "src": "<percorso locale della foto originale>":
      verrà copiata e rinominata in "file" dentro data/listings/<slug>/img/.

  python manage.py remove <slug> [--keep-data] [--no-deploy]
      Rimuove un annuncio, rigenera il sito e lo pubblica.
      Con --keep-data non cancella i dati: imposta solo available:false
      (utile per un immobile "in pausa" che potrebbe tornare disponibile).

  python manage.py build
      Rigenera solo i file locali in output/, senza pubblicare.

  python manage.py deploy
      Pubblica su studioboldrini.online l'ultima build fatta con 'build'.
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as c

SCRIPTS_DIR = Path(__file__).resolve().parent


def run(script_name):
    result = subprocess.run([sys.executable, str(SCRIPTS_DIR / script_name)])
    if result.returncode != 0:
        sys.exit(result.returncode)


def cmd_list(args):
    listings = []
    for p in sorted(c.DATA_DIR.glob("*.json")):
        listings.append(c.load_listing_file(p))
    if not listings:
        print("Nessun annuncio in data/listings/.")
        return
    listings.sort(key=lambda l: l.get("date_posted", ""), reverse=True)
    print(f"{'SLUG':45} {'STATO':9} {'DISPONIBILE':12} {'PREZZO':12} DATA")
    for l in listings:
        prezzo = c.price_plain(l)
        vis = "sì" if l.get("available", True) else "NASCOSTO"
        print(f"{l['slug']:45} {l['status']:9} {vis:12} {prezzo:12} {l.get('date_posted','')}")


def cmd_add(args):
    src_json = Path(args.json_file)
    if not src_json.exists():
        print(f"ERRORE: file non trovato: {src_json}", file=sys.stderr)
        sys.exit(1)

    data = json.loads(src_json.read_text(encoding="utf-8"))
    if "slug" not in data or not data["slug"]:
        print("ERRORE: il json deve avere un campo 'slug'.", file=sys.stderr)
        sys.exit(1)
    slug = data["slug"]

    try:
        c.validate_listing(data, source_desc=str(src_json))
    except c.ListingError as e:
        print(f"ERRORE: {e}", file=sys.stderr)
        sys.exit(1)

    img_dir = c.DATA_DIR / slug / "img"
    img_dir.mkdir(parents=True, exist_ok=True)

    for foto in data["foto"]:
        dest = img_dir / foto["file"]
        src = foto.pop("src", None)
        if src:
            src_path = Path(src)
            if not src_path.exists():
                print(f"ERRORE: foto sorgente non trovata: {src_path}", file=sys.stderr)
                sys.exit(1)
            shutil.copyfile(src_path, dest)
            print(f"  foto copiata: {src_path.name} -> data/listings/{slug}/img/{foto['file']}")
        elif not dest.exists():
            print(f"ERRORE: {dest} non esiste e la foto non ha un campo 'src'.", file=sys.stderr)
            sys.exit(1)

    dest_json = c.DATA_DIR / f"{slug}.json"
    is_update = dest_json.exists()
    dest_json.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{'Aggiornato' if is_update else 'Aggiunto'} annuncio: {slug}")

    run("build.py")
    if not args.no_deploy:
        run("deploy.py")
        print(f"\nOnline su: {c.canonical_url(data)}")


def cmd_remove(args):
    slug = args.slug
    dest_json = c.DATA_DIR / f"{slug}.json"
    if not dest_json.exists():
        print(f"ERRORE: nessun annuncio con slug '{slug}'. Usa 'python manage.py list' per vederli.", file=sys.stderr)
        sys.exit(1)

    if args.keep_data:
        data = json.loads(dest_json.read_text(encoding="utf-8"))
        data["available"] = False
        dest_json.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"Annuncio '{slug}' nascosto dal sito (dati e foto conservati in data/listings/).")
    else:
        dest_json.unlink()
        img_dir = c.DATA_DIR / slug
        if img_dir.exists():
            shutil.rmtree(img_dir)
        print(f"Annuncio '{slug}' eliminato (dati e foto rimossi).")

    run("build.py")
    if not args.no_deploy:
        run("deploy.py")


def cmd_build(args):
    run("build.py")


def cmd_deploy(args):
    run("deploy.py")


def main():
    parser = argparse.ArgumentParser(description="Gestione annunci studioboldrini.online")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="Elenca gli annunci")
    p_list.set_defaults(func=cmd_list)

    p_add = sub.add_parser("add", help="Aggiunge o aggiorna un annuncio")
    p_add.add_argument("json_file", help="File JSON dell'annuncio")
    p_add.add_argument("--no-deploy", action="store_true", help="Non pubblicare, solo rigenerare in locale")
    p_add.set_defaults(func=cmd_add)

    p_remove = sub.add_parser("remove", help="Rimuove un annuncio")
    p_remove.add_argument("slug", help="Slug dell'annuncio (nome del file json senza .json)")
    p_remove.add_argument("--keep-data", action="store_true", help="Non cancellare i dati: nascondi soltanto")
    p_remove.add_argument("--no-deploy", action="store_true", help="Non pubblicare, solo rigenerare in locale")
    p_remove.set_defaults(func=cmd_remove)

    p_build = sub.add_parser("build", help="Rigenera solo i file locali")
    p_build.set_defaults(func=cmd_build)

    p_deploy = sub.add_parser("deploy", help="Pubblica l'ultima build")
    p_deploy.set_defaults(func=cmd_deploy)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
