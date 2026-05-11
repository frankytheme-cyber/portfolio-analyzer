# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Running the app

```bash
python3 -m streamlit run app.py
# opens at http://localhost:8501
```

Headless (no auto-open browser):
```bash
python3 -m streamlit run app.py --server.headless true
```

## Dependencies

```bash
pip3 install streamlit plotly pandas openpyxl anthropic
```

No `requirements.txt` — install manually as above. Python 3.9 is in use; use `from __future__ import annotations` for `X | Y` type hints.

`anthropic` è richiesto solo per la tab Chat. Imposta `ANTHROPIC_API_KEY` come variabile d'ambiente o in `.streamlit/secrets.toml`.

## Architecture

Everything lives in a single file: `app.py`.

**Data flow (top to bottom):**
1. **CSS injection** — full dark-theme design system (`"Obsidian Terminal"`) injected via `st.markdown` at module level. Uses CSS variables and targets Streamlit internals (`[data-testid="stHeader"]`, `div[data-baseweb="tab-list"]`, etc.). Material Symbols Rounded loaded via Google Fonts; icons rendered as `<span class="mat">icon_name</span>`.
2. **Classification helpers** — pure functions (`classify_asset`, `infer_sector`) with priority order: CERTIFICATE → ETF → BOND → AZIONE → ALTRO.
3. **Data cleaning** — `clean_numeric` handles Italian locale numbers (`7.125,00 €` → `7125.0`); `normalize_columns` maps variant header names to canonical ones via `HEADER_MAP`; `process_portfolio` orchestrates both plus classification and weight calculation.
4. **Crypto manuali** — form in sidebar; persistite in `crypto.json` accanto a `app.py` via `load_crypto`/`save_crypto`. `crypto_rows_to_df` le converte in righe con `Classe="CRYPTO"` e vengono concatenate al df principale dopo `process_portfolio`, con ricalcolo dei pesi.
5. **Excel export** (`to_excel_styled`) — openpyxl: blue text for ISIN/Nome, black for numerics, thin borders, thousands separator.
6. **Streamlit UI** — sidebar (uploader + form crypto) → landing guard (`st.stop()`) → KPI row (3 glass cards) → tabs: Grafici / Tabella Dati / Analisi / Chat.
7. **Chat tab** — usa `anthropic.Anthropic` con modello `claude-sonnet-4-6` in streaming. Il portafoglio è iniettato nella prima user message con `cache_control: ephemeral` (prompt caching). La cronologia vive in `st.session_state.chat_history`. Senza API key la tab mostra istruzioni invece di errore.

**Key conventions:**
- `PLOTLY_LAYOUT` dict is reused across all figures (transparent bg, DM Sans font, dark grid lines).
- Missing/N/A values in the table are highlighted amber (`rgba(251,191,36,0.12)`), not blocked.
- Streamlit's default toolbar/header/footer hidden via `display: none` CSS.

## Test data

- `test_portfolio.csv` — 10 rows, mixed formats (Italian commas, `€` symbols, N/A values) for drag-and-drop testing.
- `portafoglio_sporco.csv` — 15-row "dirty" real-world-style file used during initial development.

---

## Product spec (original)

### Financial classification logic (priority order)

**A. Certificates** — Emittenti: Vontobel, Leonteq, Marex, BNP Paribas, Societe Generale, Citigroup, Barclays, Mediobanca. Keywords: "Cash Collect", "Phoenix", "Barrier", "Memory Step Down", "Bonus Cap", "Express", "Reverse Convertible", "Outperformance". Rule: issuer + keyword → CERTIFICATE.

**B. ETF** — Keywords: "UCITS", "ETF", "Ishares", "Vanguard", "Invesco", "Lyxor", "Amundi", "Xtrackers", "WisdomTree". Rule: contains "UCITS" or "ETF" → ETF.

**C. Bonds** — Keywords: "BTP", "Bund", "Treasury", "T-Note", "Senior Preferred", "Subordinated", "Zero Coupon". Pattern: year YYYY + % in name → BOND.

### Data cleaning rules

- Strip currency symbols (€, $, USD); convert Italian comma-decimals to dots.
- Mark N/A/empty values visually but don't halt analysis.
- Sector inference from ticker: AAPL/MSFT/NVDA → Technology; ENI/XOM/BP → Energy; JPM/ISP/UCG → Finance; PFE/JNJ → Healthcare.

### Excel export standards (Skill 4 / xlsx)

- Blue text `(0,0,255)`: ISIN, Nome.
- Black text `(0,0,0)`: numeric columns.
- Bold headers, thin borders, thousands separator on numeric cells.
