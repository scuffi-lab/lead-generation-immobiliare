# Lead generation immobiliare: dall'annuncio al database

Flusso completo, usato da uno studio immobiliare di provincia (affitti), che parte dalla **pubblicazione di un appartamento**, raccoglie i **contatti interessati su WhatsApp**, li **qualifica** e li archivia in un **database** (Google Sheets) con un punteggio per ogni inquilino.

```
 1. PUBBLICAZIONE                2. RACCOLTA LEAD                  3. DATABASE
 +-------------------+           +-----------------------+         +---------------------------+
 | scheda sul sito   |           | messaggio WhatsApp    |         | Google Sheet              |
 | post Facebook     |  ------>  | ("via messaggio")     | ------> |  - Tutti i contatti       |
 | gruppi Facebook   |           | messaggio di          |         |  - Idonei (+ sezioni)     |
 | Marketplace       |           | qualificazione        |         |  - Da ricontattare        |
 +-------------------+           +-----------------------+         +---------------------------+
   skills/annuncio-immobiliare     docs/messaggio-qualificazione     docs/database-contatti.md
   skills/immobili-sito + sito/    docs/flusso.md
```

## Contenuto

| Cartella | Cosa c'è |
|---|---|
| `skills/annuncio-immobiliare/` | Istruzioni per un agente Claude (skill) che compone il testo standard e pubblica su sito, Facebook (profilo + gruppi) e Marketplace guidando Chrome. |
| `skills/immobili-sito/` | Skill che aggiunge, aggiorna o rimuove un annuncio sulla vetrina del sito. |
| `sito/` | Generatore statico della vetrina: un JSON per annuncio, pagine HTML, home, sitemap e deploy via SFTP. Python 3, nessuna dipendenza esterna. |
| `docs/flusso.md` | Il flusso passo per passo, regole e trappole operative. |
| `docs/messaggio-qualificazione.txt` | Messaggio inviato al primo contatto per qualificare il lead. |
| `docs/database-contatti.md` | Struttura del foglio, criteri del rating e regole di compilazione. |

## Regole di fondo

- **Mai l'indirizzo esatto** in annunci, slug o Marketplace: solo il comune e al massimo una zona generica.
- **Mai inventare dati**: se un requisito non è dichiarato dal contatto resta "Non dichiarato".
- **Animali = veto** (l'agenzia non li ammette).
- Nessuna pubblicazione a pagamento (boost) e nessun invio a terzi senza conferma.

## Usare il sito

```
cd sito/scripts
cp deploy_config.example.json deploy_config.json   # compila le credenziali SFTP (file ignorato da git)
python manage.py list
python manage.py add ../data/listings/esempio-bilocale-affitto.json --no-deploy
python manage.py build
```

L'esempio in `sito/data/listings/` non include le foto: aggiungile in `data/listings/<slug>/img/` (cartella ignorata da git) oppure usa il campo `src` di ogni foto.

## Cosa NON è in questo repository

Credenziali SFTP, foto degli immobili, contatti e conversazioni reali, link del foglio Google. Il sito e i template sono quelli di uno studio reale (nome, telefono pubblico e dati strutturati): sostituiscili con i tuoi prima di riutilizzarlo.
