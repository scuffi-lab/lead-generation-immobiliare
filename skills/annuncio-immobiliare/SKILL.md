---
name: annuncio-immobiliare
description: Crea e pubblica un annuncio immobiliare (affitto o vendita) sulla vetrina di studioboldrini.online, sul profilo Facebook studio_immobiliare_boldrini + gruppi immobiliari del Comprensorio del Cuoio, e su Facebook Marketplace, aprendo Chrome. Chiede le informazioni sull'immobile se non già fornite, genera la scheda sul sito e il testo nel formato standard dello Studio Boldrini, poi pubblica su sito + profilo + gruppi + Marketplace. Usare quando l'utente chiede di creare/pubblicare un annuncio immobiliare (sito e/o Facebook e/o Marketplace).
---

# Annuncio immobiliare Studio Boldrini — generatore e pubblicazione sito + Facebook + Marketplace

Crea un annuncio immobiliare e lo pubblica su tre canali: la vetrina di **studioboldrini.online**, **Facebook** (profilo `studio_immobiliare_boldrini` + gruppi del Comprensorio del Cuoio) e **Facebook Marketplace**, usando la skill `immobili-sito` per il sito e il browser Chrome (claude-in-chrome MCP) per Facebook/Marketplace.

Se l'utente chiede esplicitamente di pubblicare solo su uno o due dei tre canali (es. "pubblica solo su Facebook", "solo sul sito", "anche su Marketplace" riferito a un annuncio già pubblicato altrove, "non serve Marketplace"), esegui solo le sezioni richieste. Di default (nessuna precisazione) pubblica su **tutti e tre**, nell'ordine: sito, Facebook (profilo+gruppi), Marketplace — **ma per Marketplace, anche quando incluso di default, chiedi sempre conferma esplicita all'utente prima di pubblicare, dopo aver controllato che sia possibile farlo** (vedi punto 5, passi 2-4): non pubblicare mai lì in automatico.

## 1. Raccogli le informazioni

Se l'utente non ha già fornito tutto in chat, chiedi (in una volta sola, con AskUserQuestion o messaggio diretto):

- **Tipo di annuncio**: affitto (AFFITTASI) o vendita (VENDESI)
- **Tipologia**: bilocale, trilocale, monolocale, ecc.
- **Comune/città** dell'immobile (e, se utile, una zona generica non identificativa come "centro", "periferia" o il nome di una frazione/paese) — il comune serve anche per la scheda sul sito
- **Composizione**: elenco vani (soggiorno, camere, bagno, ecc.) e dotazioni extra (posto auto, giardino, cantina, ascensore...)
- **Prezzo**: canone mensile o prezzo di vendita, e cosa include (es. "comprensivo di spese condominiali")
- **Disponibilità**: da quando è libero
- **Requisiti**: es. referenze lavorative, garanzie
- **Foto**: cartella con le immagini dell'immobile (percorso completo)
- **mq** e **classe energetica (APE)**: obbligatori per legge sulla scheda del sito — se non forniti, procedi comunque ma segnalalo esplicitamente all'utente (sia durante la pubblicazione sul sito sia nel riepilogo finale)

Se manca il percorso delle foto o è fuori dalla working directory, usa `mcp__ccd_directory__request_directory` per ottenere l'accesso PRIMA di procedere.

**Se l'utente dice esplicitamente di non avere foto per quell'immobile** (es. "non ho foto", "niente foto per questa casa"), usa come unica foto l'immagine di riserva (logo Studio Boldrini) in `.claude/skills/annuncio-immobiliare/assets/foto-default.png` — stesso file per sito, Facebook e Marketplace — e segnalalo esplicitamente nel riepilogo finale ("nessuna foto reale disponibile, pubblicato con logo Studio Boldrini al posto delle foto").

**Non inventare mai dati** (prezzo, mq, ecc.) non forniti dall'utente.

**Nessun annuncio deve mai riferire alla via o all'indirizzo esatto dell'immobile**, né nel testo Facebook né sulla scheda del sito né nello slug **né nel campo posizione di Marketplace**: il riferimento geografico è sempre e solo il comune/città (eventualmente con una zona generica non identificativa, es. "centro storico", "zona stazione", il nome di una frazione/paese). Questo vale anche se l'utente fornisce spontaneamente la via o il numero civico: raccoglila pure per uso interno se serve altrove, ma non riportarla in nessun testo pubblicato né digitarla nel campo indirizzo di Marketplace (vedi punto 5).

## 2. Componi il testo

Segui **esattamente** questo formato (adatta i contenuti tra parentesi, mantieni struttura, ordine e stile dei bullet con `*`):

```
AFFITTASI|VENDESI <TIPOLOGIA> - <COMUNE/CITTÀ o FRAZIONE> 🏠
<Comune/città o frazione>, <zona generica non identificativa, es. centro storico>.
<Descrizione tipo ingresso/piano>, composto da:
* <vano/dotazione 1>
* <vano/dotazione 2>
* ...
€ <prezzo>/mese|(prezzo vendita) <condizioni incluse>.
Libero a <mese/data>.
Si richiedono referenze lavorative.
Per info contattare VIA MESSAGGIO lo Studio Immobiliare Boldrini http://studioboldrini.online/
```

Il numero e il testo dei bullet cambiano in base all'immobile; il resto della struttura (riga titolo con 🏠, riga prezzo, riga disponibilità, riga referenze, riga contatti) resta fissa salvo diversa indicazione esplicita dell'utente.

## 3. Pubblica sul sito studioboldrini.online

Usa la skill `immobili-sito` (Skill tool, `skill: "immobili-sito"`) passandole in `args` tutti i dati raccolti al punto 1 (tipo annuncio, tipologia, comune/zona, composizione, prezzo, disponibilità, requisiti, descrizione, percorso completo delle foto) più mq e APE se disponibili. Quella skill si occupa da sola di scrivere il JSON in `data/listings/`, copiare le foto ed eseguire `manage.py add` (pubblicazione immediata su studioboldrini.online).

Annota l'URL della scheda pubblicata che la skill restituisce (`https://studioboldrini.online/immobili/<slug>.html`): serve per il riepilogo finale. Se `immobili-sito` segnala dati obbligatori mancanti (APE, mq), riportalo così com'è nel riepilogo finale invece di reinventare l'avviso.

Se l'utente ha chiesto di pubblicare solo su Facebook e/o Marketplace (escludendo il sito), salta questo passo.

## 4. Pubblica su Facebook (profilo + gruppi) via Chrome

Se l'utente ha chiesto di pubblicare solo sul sito e/o solo su Marketplace (escludendo profilo/gruppi Facebook), salta questa sezione.

Usa le tool `mcp__claude-in-chrome__*` (caricale con ToolSearch se deferite: `select:mcp__claude-in-chrome__tabs_context_mcp,mcp__claude-in-chrome__navigate,mcp__claude-in-chrome__computer,mcp__claude-in-chrome__read_page,mcp__claude-in-chrome__find,mcp__claude-in-chrome__file_upload`).

1. Apri/naviga su `https://www.facebook.com` in una tab pulita (crea una nuova tab con `tabs_create_mcp` per evitare stati sporchi da tab precedenti). Verifica di essere loggato come `studio_immobiliare_boldrini` da uno screenshot.
2. Trova il composer con `find` (query tipo "A cosa stai pensando post composer") e cliccalo. **Non tentare mai di aprire "Metti in evidenza"/boost a pagamento** — se capita per errore, esci senza pubblicare l'inserzione a pagamento.
3. Scrivi il testo del post con `computer` action `type` nel campo di testo.
4. Clicca il pulsante "Foto/video" (`find` per il ref esatto). Si apre la finestra nativa di Windows "Open":
   - **Claude non può cliccare né digitare in questa finestra nativa** (blocco di sicurezza del sistema, non aggirabile — non tentare con computer-use). Chiedi esplicitamente all'utente di selezionare i file nella cartella (già posizionata correttamente se la cartella è stata usata di recente) e premere "Open". Aspetta la sua conferma prima di continuare.
   - Dopo la conferma dell'utente, verifica con uno screenshot che le foto siano state caricate (indicatore "+N" o miniature visibili).
5. Clicca "Avanti".
6. Nella schermata "Impostazioni del post", clicca "Condividi nei gruppi".
7. **Selezione gruppi — usa SEMPRE `read_page` con `filter: all` sul dialog per ottenere i `ref` esatti dei checkbox**, poi clicca ogni checkbox per `ref` (mai coordinate pixel + scroll: lo scroll dentro questa lista può attivare click accidentali su elementi che passano sotto il cursore). Dopo ogni click, ricontrolla lo stato leggendo la lista "Condividi su" in cima al dialog (i "chip" rimovibili) — quella è la fonte di verità su cosa è selezionato, non l'attributo `checked` del checkbox.
   - Gruppi da selezionare — sono **6**, la Pagina è membro di tutti (nomi esatti da cercare nella lista "Seleziona gruppi" del dialog):
     - Bacheca degli Annunci Immobiliari del Comprensorio del Cuoio — `facebook.com/groups/631353890399206/`
     - PUNTO AFFITTI COMPRENSORIO DEL CUOIO — `facebook.com/groups/puntoaffitti/`
     - Bacheca Immobiliare Affitti Comprensorio del Cuoio e Limitrofe — `facebook.com/groups/554672095429886/`
     - Scambio immobiliare zona cuoio — `facebook.com/groups/1541721503596954/`
     - CASE IN VENDITA EMPOLI E DINTORNI - COMPRENSORIO DEL CUOIO — `facebook.com/groups/1380277182429042/`
     - IMMOBILIARE BOLDRINI — `facebook.com/groups/287835378274044/` (gruppo dello Studio, 407 membri)
   - **La lista del dialog mostra solo ~5 gruppi alla volta: gli altri stanno sotto e vanno cercati scrollando.** Non dare per scontato che i gruppi visibili al primo `read_page`/`find` siano tutti quelli disponibili: se non hai trovato tutti e 6 i checkbox, scrolla la lista verso il basso (con cautela, ricontrollando i chip "Condividi su" dopo ogni scroll) e ripeti `find` finché non li hai tutti, oppure hai visto la fine della lista. Se un gruppo davvero non c'è, verifica su `facebook.com/groups/<id>/members/` se la Pagina ne è membro prima di riportarlo come "non disponibile".
   - Se in chat l'utente specifica un elenco diverso di gruppi per quella pubblicazione, usa quello al posto della lista di default sopra.
8. Clicca "Fine", verifica che il testo "N gruppi Facebook selezionati" combaci con il numero atteso (**6** con la lista di default: se ne leggi meno, torna indietro e cerca i mancanti scrollando la lista prima di pubblicare), poi clicca "Pubblica".
   - **Attenzione**: nella schermata "Impostazioni del post" il contenuto può scrollare tra uno screenshot e il click successivo, e sotto "Condividi nella storia" c'è il toggle **"Metti in evidenza il post"** (boost a pagamento). Clicca "Pubblica" **sempre per `ref`** (`find` "Pubblica button in post settings dialog"), mai per coordinate: un click a coordinate fisse può finire sul toggle e attivare l'inserzione a pagamento. Prima di pubblicare, verifica da screenshot che quel toggle sia spento; se si è acceso, spegnilo e ripeti la verifica.

## 5. Pubblica su Facebook Marketplace via Chrome

Se l'utente ha chiesto di pubblicare solo sul sito e/o solo su profilo/gruppi Facebook (escludendo Marketplace), salta questa sezione.

**Non pubblicare mai su Marketplace senza prima controllare che sia possibile e senza aver chiesto conferma esplicita all'utente per questa pubblicazione specifica** — anche se Marketplace era incluso nel default "tutti e tre i canali". I passi 1-4 sono obbligatori e vanno fatti in quest'ordine, prima di toccare qualsiasi campo del form.

1. **Passa al profilo personale**: Marketplace non è utilizzabile dalla Pagina (`studio_immobiliare_boldrini`) — se sei loggato come Pagina, qualunque URL di Marketplace reindirizza a `facebook.com/marketplace/ineligible/` con l'errore "Pages can't use Marketplace". Clicca l'avatar in alto a destra, poi il **profilo personale del titolare** nel menu a tendina. Dopo un'interruzione di connessione la sessione può tornare da sola sulla Pagina: se un URL di Marketplace mostra di nuovo l'errore, ripeti lo switch di profilo prima di continuare.
2. **Controlla se è possibile pubblicare**: naviga su `https://www.facebook.com/marketplace/create/rental` (per un affitto) o `https://www.facebook.com/marketplace/create/` (per una vendita, scegliendo la categoria immobiliare più simile) e leggi la pagina/fai uno screenshot **prima di compilare qualsiasi campo**. Se compare un avviso tipo "Hai raggiunto il tuo limite mensile di N annunci immobiliari", o il pulsante "Avanti" resta disattivato per un motivo analogo, la pubblicazione **non è possibile ora**: non forzarla, non compilare il form. Prendi nota del motivo esatto riportato da Facebook (es. limite mensile raggiunto e quando si sblocca, tipicamente il 1° del mese successivo) per riportarlo all'utente al punto 4, e salta i passi 5-10.
3. **Controlla che non esista già un annuncio duplicato**: naviga su `https://www.facebook.com/marketplace/you/selling` e scorri l'elenco "I tuoi annunci" cercando un annuncio attivo con stesso comune/zona e prezzo simile. Annota se lo trovi (prezzo, data di pubblicazione, eventuali clic/messaggi ricevuti), da riportare al punto 4.
4. **Chiedi sempre conferma esplicita all'utente prima di pubblicare**, per questa pubblicazione specifica, indipendentemente da cosa deciso all'inizio sui canali. Usa AskUserQuestion (o un messaggio diretto se il contesto non si presta a una domanda strutturata) riportando:
   - se la pubblicazione è possibile (punto 2) o bloccata (e perché, es. limite mensile) — se bloccata, fermati qui: non c'è nulla da confermare, salta i passi 5-10 e riporta lo stato nel riepilogo finale;
   - eventuali duplicati trovati (punto 3).
   Procedi ai passi 5-10 **solo** con una risposta affermativa esplicita dell'utente. Se risponde di no, salta il resto della sezione e riportalo nel riepilogo finale.
5. Se non sei già sulla pagina di creazione annuncio (punto 2), naviga di nuovo su `https://www.facebook.com/marketplace/create/rental` (o l'equivalente per vendita).
6. **Foto**: usa `find` con una query tipo "file input button for adding photos" per trovare l'`input[type=file]` nascosto, poi `file_upload` con tutti i path delle foto. **Carica tutte le foto in un'unica chiamata `file_upload`**: chiamate separate sullo stesso o su un input diverso possono *sostituire* invece di aggiungere le foto già caricate (comportamento osservato e inaffidabile) — se serve aggiungerne altre dopo, verifica sempre il contatore "Foto · N/50" con uno screenshot prima di procedere.
7. Compila i campi (scorri il pannello di sinistra, i campi sono in quest'ordine): **Tipo di affitto/immobile** (dropdown: Appartamento/Condominio per un appartamento, Casa o Villetta a schiera per una casa indipendente, Solo stanza per una stanza singola), **Numero di camere da letto** e **Numero di bagni** (dal conteggio vani della composizione), **Prezzo al mese** (solo il numero), **Posizione** (digita **solo comune/zona generica, mai via o numero civico** — vedi regola privacy al punto 1 — e attendi ~1-2s i suggerimenti di autocomplete, poi clicca un suggerimento; verifica che la mappa nell'anteprima si aggiorni sulla zona corretta), **Descrizione** (incolla lo stesso testo standard composto al punto 2).
8. Clicca **Avanti**: si apre "Pubblica in altri luoghi" con "Pubblica annuncio per tutti" (Marketplace) già selezionato — lascialo così. "Pubblica l'annuncio nei tuoi gruppi" (fino a 20 gruppi Marketplace, diversi dai gruppi Facebook del punto 4 della sezione precedente) resta deselezionato di default: selezionalo solo se l'utente lo chiede esplicitamente per quella pubblicazione.
9. Clicca **Pubblica** e attendi (qualche secondo, mostra uno spinner). Se compare il popup "Metti in evidenza il tuo annuncio" (boost a pagamento), **chiudilo con la X senza mai accettare la promozione a pagamento**.
10. Verifica su `https://www.facebook.com/marketplace/you/selling` che il nuovo annuncio compaia con prezzo e data odierna corretti (può mostrare "Questo annuncio è in fase di analisi": è normale, la moderazione richiede tempo, riportalo come stato nel riepilogo finale).

**Attenzione dopo un'interruzione di connessione**: se una chiamata fallisce con un errore di connessione ("computer running that browser appears to be offline") e poi torna a funzionare, o se uno screenshot risulta di dimensioni anomale/minuscole (es. poche decine di pixel), non fidarti dello stato assunto in precedenza — ricarica la pagina e verifica con un nuovo screenshot prima di cliccare di nuovo: le coordinate calcolate prima dell'interruzione possono finire su elementi sbagliati (es. aprire per errore la modifica di un post esistente non correlato). Se capita, chiudi qualunque dialog non intenzionale **senza salvare**.

## 6. Verifica reale (non fidarti delle notifiche "cross-posting")

Le notifiche Facebook "Hai eseguito il cross-posting del tuo post su X" confermano solo il **tentativo di invio**, non la pubblicazione effettiva: molti di questi gruppi richiedono **approvazione admin** sia per l'iscrizione che per i post. Dopo aver pubblicato:

1. Per ciascun gruppo target, naviga alla sua pagina (`facebook.com/groups/<id>/`) e leggi il testo pagina (`get_page_text`).
2. Se compare "Iscrizione effettuata — In attesa di approvazione da parte dell'amministratore", il post **non è ancora visibile pubblicamente** — è in coda per approvazione.
3. Se il post con il testo dell'annuncio compare nel feed del gruppo, è pubblicato.
4. Riporta all'utente lo stato **reale e verificato** per il profilo e per ciascun gruppo separatamente (pubblicato / in attesa di approvazione / eventuali gruppi non trovati), non un riepilogo ottimistico basato solo sulle notifiche. Se pubblicato anche su Marketplace, includi lo stato trovato al punto 5.7 (pubblicato / in fase di analisi); se pubblicato anche sul sito, includi l'URL della scheda (punto 3) ed eventuali dati obbligatori mancanti (APE, mq).

## Note

- Se durante la selezione gruppi finisci per selezionare gruppi non richiesti (es. per un misclick), deselezionali PRIMA di cliccare "Pubblica" — una volta pubblicato non è possibile ritirare l'invio a un gruppo dal post stesso in modo affidabile.
- Se serve interagire con una finestra nativa di Windows aperta da Chrome (file picker, stampa, ecc.), ricordati che è bloccata per policy di sicurezza: va sempre chiesto all'utente di completarla lui.
- Non accettare mai una promozione/boost a pagamento (né sul post Facebook né sull'annuncio Marketplace) a meno che l'utente non lo chieda esplicitamente per quella pubblicazione specifica.
