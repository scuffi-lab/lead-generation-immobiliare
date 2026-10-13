#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Carica output/ sul webspace IONOS via SFTP, e rimuove sul server i file
di annunci che non esistono più in locale (rimossi con manage.py remove).

Uso:
    python deploy.py
"""
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as c

CONFIG_PATH = Path(__file__).resolve().parent / "deploy_config.json"
DEPLOYED_MANIFEST_PATH = c.OUTPUT_DIR / ".deployed-manifest.json"

ALWAYS_FILES = ["index.html", "immobili/index.html", "sitemap.xml"]


def load_config():
    if not CONFIG_PATH.exists():
        print(f"ERRORE: manca {CONFIG_PATH} con le credenziali SFTP.", file=sys.stderr)
        sys.exit(1)
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def load_manifest():
    p = c.OUTPUT_DIR / ".manifest.json"
    if not p.exists():
        print("ERRORE: nessuna build trovata. Esegui prima 'python build.py'.", file=sys.stderr)
        sys.exit(1)
    return json.loads(p.read_text(encoding="utf-8"))


def load_deployed_manifest():
    if DEPLOYED_MANIFEST_PATH.exists():
        return json.loads(DEPLOYED_MANIFEST_PATH.read_text(encoding="utf-8"))
    return {"html": [], "img": []}


def save_deployed_manifest(manifest):
    DEPLOYED_MANIFEST_PATH.write_text(json.dumps(manifest, indent=2), encoding="utf-8")


def build_sftp_batch(config, manifest, old_manifest):
    webroot = config["remote_webroot"]
    lines = [
        f"-mkdir {webroot}/immobili",
        f"-mkdir {webroot}/immobili/img",
    ]
    for rel in ALWAYS_FILES:
        local = (c.OUTPUT_DIR / rel).as_posix()
        lines.append(f"put \"{local}\" {webroot}/{rel}")
    for rel in manifest["html"] + manifest["img"]:
        local = (c.OUTPUT_DIR / rel).as_posix()
        lines.append(f"put \"{local}\" {webroot}/{rel}")

    new_set = set(manifest["html"]) | set(manifest["img"])
    old_set = set(old_manifest.get("html", [])) | set(old_manifest.get("img", []))
    to_remove = old_set - new_set
    for rel in sorted(to_remove):
        lines.append(f"-rm {webroot}/{rel}")

    return "\n".join(lines) + "\n"


def run_sftp(config, batch_text):
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        batch_file = tmp / "batch.txt"
        batch_file.write_text(batch_text, encoding="utf-8")
        askpass = tmp / "askpass.sh"
        askpass.write_text(f'#!/bin/sh\necho "{config["password"]}"\n', encoding="utf-8")
        askpass.chmod(0o700)

        sftp_bin = shutil.which("sftp") or "/usr/bin/sftp"
        cmd = [
            sftp_bin,
            "-oBatchMode=no",
            "-oStrictHostKeyChecking=no",
            "-oUserKnownHostsFile=/dev/null",
            "-b", str(batch_file),
            f"{config['user']}@{config['host']}",
        ]
        import os
        env = dict(os.environ)
        env["SSH_ASKPASS"] = str(askpass)
        env["SSH_ASKPASS_REQUIRE"] = "force"
        env["DISPLAY"] = ":0"
        result = subprocess.run(cmd, capture_output=True, text=True, env=env)
        return result


def main():
    config = load_config()
    manifest = load_manifest()
    old_manifest = load_deployed_manifest()

    batch = build_sftp_batch(config, manifest, old_manifest)
    result = run_sftp(config, batch)

    noise = ("post-quantum", "store now", "openssh.com/pq", "Permanently added")
    out_lines = [l for l in (result.stdout or "").splitlines() if not any(n in l for n in noise)]
    err_lines = [l for l in (result.stderr or "").splitlines() if not any(n in l for n in noise)]

    print("\n".join(out_lines))
    if err_lines:
        print("\n".join(err_lines), file=sys.stderr)

    if result.returncode != 0:
        print(f"ERRORE: sftp ha restituito codice {result.returncode}", file=sys.stderr)
        sys.exit(1)

    save_deployed_manifest(manifest)
    print("\nDeploy completato su https://studioboldrini.online/")


if __name__ == "__main__":
    main()
