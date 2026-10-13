# Database dei contatti (Google Sheets)

Un foglio con più schede.

## Tutti i contatti

Una riga per lead. Il dedup si fa su **nome e numero**: se il contatto viene salvato in rubrica il nome cambia, e il solo nome creerebbe un doppione.

| Col. | Campo |
|---|---|
| A | Nome WhatsApp |
| B | Numero di telefono (`'+39 ...`, oppure "da rilevare") |
| C | Data primo contatto |
| D | Riepilogo conversazione |
| E | Contratto indeterminato o pensionato |
| F | Garante |
| G | Animali |
| H | Affitto lungo (> 1 anno) |
| I | Figli |
| J | Rating |
| K | Appuntamento |
| L | Data ultimo aggiornamento |
| M | Stato |

## Rating dell'inquilino

Cinque requisiti: contratto indeterminato o pensionato, garante, niente animali, affitto oltre l'anno, niente figli. Il rating è il numero di requisiti **confermati** (es. `3/5 - Alto`). I requisiti non dichiarati restano "Non dichiarato" e non contano. Gli **animali sono un veto**: "Da scartare - animale non ammesso".

## Idonei

Chi non ha animali e ha un contratto idoneo. Colonne: Nome, Numero, Contratto, Animali, Rating, Appuntamento. In fondo ci sono sezioni tematiche con intestazione in grassetto (per esempio insegnanti e pensionati), separate da una riga vuota. Le sezioni **duplicano** le righe della lista generale, non le spostano. Se cambia un appuntamento in "Tutti i contatti", va aggiornato anche qui.

## Da ricontattare

Follow-up manuale: Nome, Numero, Rating, Motivo/Stato, Ricontattare dal, riga di riferimento, data ultimo controllo. Si aggiorna rileggendo le chat dei nominativi elencati.

## Privacy

Il foglio contiene dati personali di persone reali: tienilo privato e non pubblicarne mai il contenuto o l'indirizzo. Questo repository non ne contiene.
