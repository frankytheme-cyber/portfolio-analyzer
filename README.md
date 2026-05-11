# Portfolio Analyzer

Analizzatore di portafoglio multi-broker (CSV/Excel + crypto manuali) con classificazione automatica, metriche di rischio, simulatore what-if e chat con Claude. Single-file Streamlit app, estetica editoriale **Almanac**.

## Quick start

```bash
# 1. installa dipendenze
pip3 install streamlit plotly pandas openpyxl anthropic

# 2. avvia
python3 -m streamlit run app.py
# → http://localhost:8501
```

Headless (no auto-open browser):

```bash
python3 -m streamlit run app.py --server.headless true
```

Porta custom:

```bash
python3 -m streamlit run app.py --server.port 8765
```

## Setup chat con Claude

La tab **Chat** richiede una API key Anthropic. Due opzioni:

**A. Variabile d'ambiente** (per-shell):

```bash
export ANTHROPIC_API_KEY="sk-ant-..."
python3 -m streamlit run app.py
```

**B. File secrets** (persistente, consigliato):

```bash
mkdir -p .streamlit
cat > .streamlit/secrets.toml <<EOF
ANTHROPIC_API_KEY = "sk-ant-..."
EOF
```

`.streamlit/` è già in `.gitignore`. La key si genera su [console.anthropic.com](https://console.anthropic.com/settings/keys).

## Utilizzo

1. **Carica file** dalla sidebar — CSV/XLSX/XLS, anche multipli (es. export Fineco diversi)
2. **Aggiungi crypto manuali** dal form sidebar (persistite in `crypto.json`)
3. **Modifica/rimuovi crypto** cliccando l'expander della posizione
4. **Esplora le tab**:
   - **Grafici** — donut allocazione, settore, geografia, sottotipo, holdings
   - **Tabella Dati** — vista dettagliata + export CSV/Excel formattato
   - **Analisi** — metriche di rischio (HHI, top-5, single-name) + simulatore what-if (vendita/aggiunta/stress test)
   - **Chat** — domande in linguaggio naturale al portafoglio (richiede API key)

## File di test

| File | Note |
|---|---|
| `test_portfolio.csv` | 10 righe miste (formati italiani, € symbol, N/A) |
| `portafoglio_sporco.csv` | 15 righe stile real-world per testing |

## Architettura

Tutto in `app.py` (~3200 righe). Layout:

1. **CSS injection** — design system "Almanac" (cream paper, Fraunces serif, Bricolage Grotesque body, JetBrains Mono per numerali tabulari)
2. **Classification helpers** — `classify_asset(name, isin)` con priorità: CASH → CERTIFICATE → ETF/FUND (commodity/bond/equity per sottostante) → BOND diretto → AZIONE (suffissi/ticker/ISIN) → ALTRO
3. **Data cleaning** — `clean_numeric` (locale italiano: `7.125,00 €` → `7125.0`), `normalize_columns` (mappa header alternativi via `HEADER_MAP`)
4. **Crypto storage** — sidebar form → `crypto.json` (stesso path di `app.py`)
5. **Persistenza sessione** — upload e chat history sopravvivono al reload: file salvati in `.cache/uploads/`, cronologia chat in `.cache/chat_history.json`
6. **Excel export** — `to_excel_styled` con openpyxl (testo blu su ISIN/Nome, bordi, separatori migliaia)
7. **Streamlit UI** — sidebar → landing guard → KPI row → tabs (Grafici/Tabella/Analisi/Chat) → report Financial-Analyst

Modello chat: `claude-sonnet-4-6` con prompt caching ephemeral sul portafoglio iniettato (taglia i costi sui follow-up).

## Skill di riferimento

L'analisi finanziaria è codice Python diretto in `app.py`, ispirato a tre skill Claude Code referenziate in `skills-lock.json`:

| Skill | Fonte | Utilizzo nell'app |
|---|---|---|
| `financial-analyst` | `alirezarezvani/claude-skills` | benchmark HHI, concentration ratio, diversification rating, risk analytics, report tab |
| `csv-data-summarizer` | `coffeefuelbump/csv-data-summarizer-claude-skill` | data quality report, correlazioni, statistiche distribuzione |
| `xlsx` | `anthropics/skills` | export Excel multi-sheet con formule, color coding (blu ISIN/Nome, nero numerici) |

Le skill hanno funzionato come **blueprint** durante lo sviluppo; la logica è poi stata cristallizzata in codice Python per non richiedere un loader di skill a runtime. La tab **Chat** usa direttamente l'API Anthropic senza skill intermedie.

## Stack

- Python 3.9+ (con `from __future__ import annotations` per supportare `X | Y`)
- Streamlit 1.50+
- Plotly (grafici)
- pandas (data wrangling)
- openpyxl (export Excel)
- anthropic (chat — opzionale)

## Troubleshooting

**Chat dice "API KEY MANCANTE"** → riavvia streamlit nella shell che ha la env var, o crea `.streamlit/secrets.toml`

**Sidebar non scrolla** → bug fixato; se ricompare svuota la cache browser e riavvia

**Asset finiscono in ALTRO** → la classificazione usa nome + ISIN. Se ne trovi qualcuno mal classificato apri una segnalazione con nome esatto + ISIN

**Errore importing anthropic** → `pip3 install anthropic` (richiesto solo per la tab Chat)

## Privacy

- **Dati portafoglio** restano locali — file `.xls/.xlsx/.csv` esclusi dal repo via `.gitignore`
- **API key** in `.streamlit/secrets.toml` (gitignored)
- **Crypto manuali** in `crypto.json` locale
- **Chat con Claude** invia il portafoglio strutturato come contesto a Anthropic — vedi loro [policy](https://www.anthropic.com/legal/privacy)
