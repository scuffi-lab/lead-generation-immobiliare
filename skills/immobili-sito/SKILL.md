---
name: immobili-sito
description: Aggiunge, aggiorna o rimuove un annuncio immobiliare sulla vetrina di studioboldrini.online (pagina /immobili/, scheda del singolo immobile, sezione in home, sitemap). Usa il sistema in sito/ (data/listings/*.json + scripts/manage.py), non modifica mai l'HTML a mano. Usare quando l'utente chiede di pubblicare, togliere, nascondere o aggiornare un immobile sul sito (non su Facebook: per Facebook c'è la skill annuncio-immobiliare).
---

# Gestione annunci sul sito studioboldrini.online

Il sito ha una vetrina immobili gestita da un piccolo generatore statico in
`sito/`. **Non scrivere mai HTML a mano
per un annuncio**: crea un JSON e lascia fare a `manage.py`. Leggi
`sito/README.md` per il formato completo
se serve un ripasso; qui c'è il flusso operativo.

Python da usare: `python` (3.12)
(non è sul PATH di default in ogni shell).

## Aggiungere un annuncio

1. Raccogli dai dati forniti (o chiedi se mancano): tipo (affitto/vendita),
   tipologia, comune/zona, prezzo, piano, impianti, parcheggio, mq, classe
   energetica (APE — obbligatoria per legge, se non la danno segnalalo),
   disponibilità, requisiti, descrizione, e le foto (percorso locale dei file).
   **Non inventare dati mancanti.** Nei campi `comune`/`zona` e in tutti i
   testi (title, descrizione, wa_text, meta description...) non riportare mai
   la via o l'indirizzo esatto, anche se l'utente lo fornisce: il riferimento
   geografico resta sempre comune/città, al massimo con una zona generica non
   identificativa.
2. Scegli uno `slug` (minuscolo, solo lettere/numeri/trattini, es.
   `trilocale-affitto-fucecchio-centro`). **Non usare mai il nome della via
   nello slug** (né altrove sulla scheda): compare nell'URL pubblico, quindi
   varrebbe come riferimento alla via. Il riferimento geografico è sempre e
   solo comune/città, eventualmente con una zona generica non identificativa
   (es. "centro", nome di una frazione).
3. Scrivi un file JSON (es. in una cartella temporanea) seguendo lo schema
   descritto nel README — copia la struttura da
   `data/listings/bilocale-affitto-santa-croce-sull-arno.json` come esempio.
   Per le foto, usa `"src": "<percorso completo del file originale>"` così le
   copia da solo; scegli didascalie/alt text descrittivi in italiano coerenti
   con lo stile già usato (concreto, niente aggettivi vuoti).
4. Esegui:
   ```
   cd "sito/scripts"
   "python" manage.py add <path-json>
   ```
   Questo copia le foto, rigenera home/vetrina/scheda/sitemap e pubblica subito
   su studioboldrini.online via SFTP.
5. Verifica con una richiesta HTTP (`curl -s -o /dev/null -w '%{http_code}'
   <url>`) che la nuova scheda risponda 200, e se possibile controlla
   visivamente la pagina (screenshot) prima di dire all'utente che è online.
6. Riporta all'utente l'URL della scheda pubblicata e, se manca l'APE o altri
   dati obbligatori, ricordaglielo esplicitamente.

## Rimuovere (o nascondere) un annuncio

- Elenca prima gli annunci esistenti se non conosci lo slug esatto:
  `python manage.py list`
- Eliminazione definitiva (cancella anche le foto):
  `python manage.py remove <slug>`
- Se l'utente vuole solo "metterlo in pausa" senza perdere i dati (es. immobile
  sotto trattativa che potrebbe tornare disponibile):
  `python manage.py remove <slug> --keep-data`
  In questo caso i dati restano in `data/listings/<slug>.json` con
  `"available": false"`, pronti per essere riattivati rimettendo `true` e
  rilanciando `python manage.py build && python manage.py deploy`.
- Anche qui, verifica con curl che la vecchia scheda dia 404 e che la vetrina
  non la mostri più prima di confermare all'utente.

## Cose a cui stare attenti

- Il comando `add`/`remove` pubblica **subito** in produzione (nessuna
  conferma intermedia): se l'utente sta ancora decidendo i dettagli, prepara
  il JSON e usa `--no-deploy` finché non è sicuro, poi lancia `deploy.py` a
  parte.
- I path locali passati a `sftp` nel batch devono usare `/` e non `\`
  (già gestito da `deploy.py`, ma se tocchi lo script tienilo a mente: `sftp`
  interpreta il backslash come escape e tronca il percorso).
- Non toccare `templates/home_base.html`, `templates/*.html` per un singolo
  annuncio: sono condivisi da tutti gli annunci. Le uniche modifiche
  per-annuncio vanno nel suo file JSON.
- Se serve cambiare lo stile grafico della vetrina/scheda per tutti gli
  annunci, quello sì si tocca nei template — ma è un'operazione rara e va
  verificata con uno screenshot prima di pubblicare.
