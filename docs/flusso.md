# Il flusso, passo per passo

## 1. Pubblicazione dell'appartamento

1. Si raccolgono i dati: tipo (affitto o vendita), tipologia, comune, composizione, prezzo e cosa include, disponibilità, requisiti, foto, mq e classe energetica (APE, obbligatoria per legge).
2. Testo standard dell'annuncio: titolo con tipologia e comune, elenco dei vani con `*`, prezzo, disponibilità, referenze, riga contatti "via messaggio".
3. **Sito**: un JSON in `sito/data/listings/`. `manage.py add` genera scheda, vetrina, home e sitemap, poi pubblica via SFTP.
4. **Facebook**: post dal profilo dell'agenzia e condivisione nei gruppi immobiliari della zona. La scelta delle foto nella finestra nativa di Windows la fa l'utente; il resto lo guida Chrome.
5. **Marketplace**: solo dal profilo personale, perché le Pagine non possono usarlo. Prima si controlla il limite mensile e che non esista un duplicato, poi si chiede conferma.
6. **Verifica reale**: le notifiche di "cross-posting" non bastano, perché molti gruppi richiedono l'approvazione di un admin. Si controlla gruppo per gruppo se il post è visibile.

Dettagli operativi nelle skill in `skills/`.

## 2. Raccolta dei lead

I contatti arrivano su WhatsApp Business da sito, Facebook e Marketplace. Le fonti dei candidati sono due:

- la lista WhatsApp **"New customer"**;
- i **numeri sconosciuti non archiviati** (quelli archiviati sono rumore). Ogni numero sconosciuto va aggiunto subito alla lista "New customer", così i giri successivi lo trovano.

Al primo contatto si invia il messaggio di `messaggio-qualificazione.txt`: nome e cognome, zona e budget, professione e tipo di contratto, garante, occupanti e figli, durata, animali, fascia oraria.

Prima di trattare un contatto come lead si guarda la chat: nella lista finiscono anche account WhatsApp Business di aziende (pannello "Contact info": "This is a business account") e scambi personali. Questi si escludono dal foglio.

**Si lavora da WhatsApp Web in Chrome**, non dall'app Desktop: lì la lista chat non scorre e i drag causano azioni accidentali. Lo storico si carica scorrendo verso l'alto con pause di 2-3 secondi, e i risultati di ricerca si aprono per riferimento, non a coordinate fisse.

## 3. Database

Vedi `database-contatti.md`. Un'attività pianificata (due volte al giorno) rilegge le chat e schedula i nuovi contatti. Solo il giro del mattino produce anche il report degli appuntamenti del giorno, inviato come messaggio a se stessi.

## Trappole operative (Google Sheets via browser)

- **Un numero che inizia con `+` diventa una formula** e dà `#ERROR!`. Si scrive con un apice iniziale: `'+39 ...`. Vale anche quando il numero fa da nome. Dopo ogni scrittura si rilegge il foglio cercando `#ERROR!`.
- Si scrive cella per cella con la casella del nome (riferimento, Invio, valore) e `Tab` per spostarsi a destra. Mai Invio "a vuoto" su una cella piena: il testo successivo viene appeso.
- Le frecce ravvicinate vengono perse. Per leggere è più sicuro un `fetch` sull'export CSV (`/gviz/tq?tqx=out:csv&gid=<id>`).
- Aprire sempre l'URL con il `gid` della scheda e verificarlo con uno screenshot prima di digitare.
