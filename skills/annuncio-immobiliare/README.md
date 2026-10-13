# Agente "annuncio-immobiliare"

Agente per creare e pubblicare annunci immobiliari su sito, Facebook e Facebook Marketplace per lo Studio Immobiliare Boldrini.

## Come si usa

Scrivi in chat:

```
/annuncio-immobiliare
```

oppure chiedi direttamente, ad esempio:

> "Crea un annuncio per un trilocale a Santa Croce, zona centro, 3 camere, cucina abitabile, bagno, balcone, euro 700 al mese spese escluse, libero da ottobre, referenze lavorative richieste. Foto nella cartella X."

Se non fornisci subito tutte le informazioni, l'agente te le chiede prima di procedere.

## Cosa fa, passo per passo

1. **Raccoglie le info sull'immobile**: tipo di annuncio (affitto/vendita), tipologia, zona, composizione dei vani, prezzo, disponibilità, requisiti, cartella con le foto.
2. **Scrive il testo dell'annuncio** nel formato standard dello Studio Boldrini:
   ```
   AFFITTASI BILOCALE - SAN ROMANO 🏠
   Zona San Romano, vicino al Conad.
   Appartamento con ingresso indipendente al piano terra, composto da:
   * Soggiorno con angolo cottura
   * Disimpegno
   * Camera
   * Bagno
   * Posto auto esclusivo nella resede condominiale
   € 530/mese comprensivo di spese condominiali.
   Libero a settembre.
   Si richiedono referenze lavorative.
   Per info contattare VIA MESSAGGIO lo Studio Immobiliare Boldrini http://studioboldrini.online/
   ```
3. **Apre Chrome** e pubblica il post sul profilo Facebook `studio_immobiliare_boldrini`, con le foto allegate.
4. **Condivide il post nei gruppi Facebook** (di default questi 6, salvo diversa indicazione):
   - Bacheca degli Annunci Immobiliari del Comprensorio del Cuoio
   - PUNTO AFFITTI COMPRENSORIO DEL CUOIO
   - Bacheca Immobiliare Affitti Comprensorio del Cuoio e Limitrofe
   - Scambio immobiliare zona cuoio
   - CASE IN VENDITA EMPOLI E DINTORNI - COMPRENSORIO DEL CUOIO
   - IMMOBILIARE BOLDRINI
5. **Pubblica l'annuncio anche su Facebook Marketplace** (categoria affitti/immobili), con foto, prezzo, camere/bagni e descrizione — usando il profilo personale profilo personale del titolare, perché la Pagina non può usare Marketplace.
6. **Controlla davvero** se il post è visibile in ciascun gruppo (o se è ancora "in attesa di approvazione da parte dell'amministratore") e se l'annuncio Marketplace è stato pubblicato o è ancora "in fase di analisi", e ti riporta lo stato reale per ciascun canale — non si ferma alle notifiche di Facebook, che confermano solo il tentativo di invio.

## Cose da sapere

- **Le foto vanno selezionate a mano solo per il post Facebook** (profilo/gruppi): quando Chrome apre la finestra di Windows per scegliere le foto, Claude non può cliccarci dentro per motivi di sicurezza. Ti verrà chiesto di selezionare i file e premere "Open" tu stesso — richiede pochi secondi. Su Marketplace invece Claude carica le foto da solo.
- **L'approvazione dei gruppi non dipende da Claude**: alcuni gruppi richiedono che un amministratore approvi l'iscrizione e/o il post prima che diventi visibile a tutti. È un passaggio manuale di Facebook, non un errore della pubblicazione. Anche Marketplace può mostrare l'annuncio come "in fase di analisi" per un po' prima di renderlo pubblico.
- Puoi indicare in chat un elenco di gruppi diverso dai 6 di default, se per un dato annuncio vuoi pubblicare solo in alcuni.
- Puoi chiedere di pubblicare solo su alcuni canali (es. "solo su Marketplace", "solo sul sito", "non serve il post su Facebook") — di default vengono usati tutti e tre.
- Prima di pubblicare su Marketplace, Claude controlla che non esista già un annuncio attivo per lo stesso immobile (stesso comune/zona e prezzo): se lo trova, te lo segnala invece di creare un duplicato.
- Claude non accetta mai una promozione a pagamento ("Metti in evidenza"/boost), né su Facebook né su Marketplace, a meno che tu non lo chieda esplicitamente.

## File

- `SKILL.md` — istruzioni tecniche che Claude segue per eseguire l'agente (non serve leggerlo per usarlo).
- `README.md` — questo file, guida rapida per l'utente.
