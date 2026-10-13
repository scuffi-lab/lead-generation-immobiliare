# Sistema annunci — studioboldrini.online

Genera e pubblica le pagine `/immobili/` del sito (vetrina, singole schede, sezione
in home, sitemap) a partire da file JSON. Non serve toccare HTML a mano.

## Struttura

```
data/listings/<slug>.json       ← un file per annuncio: tutti i dati e i testi
data/listings/<slug>/img/       ← le foto originali di quell'annuncio
templates/                      ← i "master" HTML con segnaposto {{COSI}}
scripts/build.py                ← rigenera output/ dai dati (locale, non pubblica)
scripts/deploy.py               ← pubblica output/ su studioboldrini.online via SFTP
scripts/manage.py               ← comando unico: list / add / remove / build / deploy
scripts/deploy_config.json      ← credenziali SFTP (copia deploy_config.example.json e compila; non va su GitHub)
output/                         ← sito generato, pronto per essere caricato
```

## Comandi

Da dentro `scripts/`, con Python 3.12
(`python`):

```
python manage.py list                      # elenca tutti gli annunci
python manage.py add annuncio.json          # aggiunge/aggiorna e pubblica
python manage.py remove <slug>              # elimina e pubblica
python manage.py remove <slug> --keep-data  # nasconde senza cancellare i dati
python manage.py build                      # solo rigenera output/, non pubblica
python manage.py deploy                     # pubblica l'ultima build
```

`add` accetta `--no-deploy` per generare senza pubblicare (utile per controllare
prima con un server locale: `python -m http.server 8766 --directory ../output`).

## Formato di un annuncio (data/listings/<slug>.json)

Campi obbligatori: `slug`, `status` (`"affitto"` o `"vendita"`), `seo_title`,
`title_line1`, `title_em`, `comune`, `zona`, `tipologia`, `prezzo`, `descrizione`
(lista di paragrafi), `foto` (lista di `{file, didascalia, alt}`).

Campi opzionali utili: `piano`, `mq`, `ape` (classe energetica — se mancante non
compare la riga, ma è obbligatoria per legge negli annunci reali, va aggiunta
appena disponibile), `impianti`, `parcheggio`, `requisiti_testo` (se assente non
compare il riquadro "Cosa chiediamo"), `facts` (2-3 frasi brevi per la card, con
**parole in grassetto** tra doppi asterischi), `amenities` (per i dati
strutturati), `wa_text` (messaggio WhatsApp precompilato: se assente viene
generato automaticamente), `available` (default `true`: se `false` l'annuncio
resta nei dati ma sparisce dal sito).

Ogni foto in `foto` può avere anche `"src": "<percorso locale della foto
originale>"`: in quel caso `manage.py add` la copia e la rinomina da sola dentro
`data/listings/<slug>/img/<file>`. Se `src` non c'è, la foto deve già trovarsi lì
(es. perché l'hai copiata a mano).

Vedi `data/listings/bilocale-affitto-santa-croce-sull-arno.json` come esempio
completo e già pubblicato.

**Nessun annuncio deve riferire alla via o all'indirizzo esatto dell'immobile**
(vale per `slug`, `zona`, titoli, descrizione, wa_text, meta description...):
il riferimento geografico è sempre e solo `comune`, eventualmente con una zona
generica non identificativa (es. "centro storico", nome di una frazione).

## Cosa fa `build.py` automaticamente

- Genera la scheda di ogni annuncio disponibile (`available: true`) in
  `output/immobili/<slug>.html`, con dati strutturati (schema.org
  `RealEstateListing`) corretti per affitto o vendita.
- Genera `output/immobili/index.html` con una sezione "In affitto" e una "In
  vendita" (solo se ci sono annunci di quel tipo); se non c'è nessun annuncio
  mostra un messaggio invece di una pagina vuota.
- Rigenera la sezione "Disponibili adesso" in home (`output/index.html`) con i 3
  annunci più recenti, a partire dal template `templates/home_base.html` (se
  cambi manualmente altre parti della home — hero, chi siamo, blog — modificale
  in quel file, non nell'output).
- Rigenera `output/sitemap.xml` (le voci non-immobili restano quelle in
  `templates/sitemap_static.xml`).
- Tiene traccia in `output/.manifest.json` di cosa ha generato, così se rimuovi
  un annuncio la build successiva cancella da sola i file HTML e le foto che non
  servono più (sia in locale sia, al prossimo `deploy`, sul server).

## Note

- Le credenziali SFTP sono in `deploy_config.json` (vedi `deploy_config.example.json`).
- Il deploy usa il comando `sftp` di sistema (Git Bash), non una libreria
  Python: se lo lanci da un terminale diverso, assicurati che `sftp` sia nel
  PATH.
- Le pagine `/blog/`, `/calcolatore-affitto.html` e il resto del sito non sono
  gestite da questo sistema: restano file statici pubblicati a parte.
