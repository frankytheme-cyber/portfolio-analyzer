from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re
import io
import textwrap

# ── Page config ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Portfolio Analyzer",
    page_icon="◈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={},
)

# ── Design system ────────────────────────────────────────────────────────────
# Aesthetic: "Obsidian Terminal" — deep dark surfaces, luminous cyan/emerald
# accents, frosted glass panels, monospace data with humanist labels.

st.html(
    textwrap.dedent("""
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,500;0,9..40,700&family=JetBrains+Mono:wght@400;600&display=swap" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200" rel="stylesheet">
    <style>

    .mat {
        font-family: 'Material Symbols Rounded';
        font-weight: 300;
        font-style: normal;
        font-size: 1.3rem;
        line-height: 1;
        letter-spacing: normal;
        text-transform: none;
        display: inline-block;
        white-space: nowrap;
        word-wrap: normal;
        -webkit-font-feature-settings: 'liga';
        font-feature-settings: 'liga';
        -webkit-font-smoothing: antialiased;
        font-variation-settings: 'FILL' 0, 'wght' 300, 'GRAD' 0, 'opsz' 24;
    }

    :root {
        --bg-deep:    #0A0C10;
        --bg-surface: #111318;
        --bg-card:    rgba(17, 19, 24, 0.85);
        --glass-border: rgba(255,255,255,0.05);
        --text-primary:   #E8ECF1;
        --text-secondary: #7A8599;
        --text-muted:     #4A5568;

        /* ── Chromatic Language: semantic class colors ── */
        --cl-bond:       #22D3EE;   /* BOND       — cerulean */
        --cl-bond-field: rgba(34,211,238,0.08);
        --cl-etf:        #34D399;   /* ETF        — emerald  */
        --cl-etf-field:  rgba(52,211,153,0.08);
        --cl-cert:       #A78BFA;   /* CERTIFICATE— violet   */
        --cl-cert-field: rgba(167,139,250,0.08);
        --cl-comm:       #FBBF24;   /* COMMODITY  — amber    */
        --cl-comm-field: rgba(251,191,36,0.08);
        --cl-azione:     #60A5FA;   /* AZIONE     — blue     */
        --cl-azione-field: rgba(96,165,250,0.08);
        --cl-altro:      #4A5568;   /* ALTRO      — steel    */
        --cl-altro-field: rgba(74,85,104,0.08);

        --accent-cyan:    #22D3EE;
        --accent-emerald: #34D399;
        --accent-amber:   #FBBF24;
        --accent-rose:    #FB7185;
        --accent-violet:  #A78BFA;
        --accent-blue:    #60A5FA;
        --glow-cyan:      rgba(34,211,238,0.12);
        --glow-emerald:   rgba(52,211,153,0.10);
    }

    /* ── Hide Streamlit chrome ───────────────────────────────────── */
    #MainMenu, header[data-testid="stHeader"], footer,
    .stDeployButton, [data-testid="stToolbar"],
    [data-testid="stDecoration"],
    [data-testid="collapsedControl"],
    button[data-testid="baseButton-headerNoPadding"] {
        display: none !important;
    }

    /* ── Sidebar always visible, no collapse button ──────────────── */
    section[data-testid="stSidebar"] {
        transform: none !important;
        min-width: 280px !important;
        max-width: 320px !important;
    }

    /* ── Global ──────────────────────────────────────────────────── */
    .stApp {
        background: var(--bg-deep) !important;
        color: var(--text-primary);
        font-family: 'DM Sans', sans-serif;
    }
    .stApp::before {
        content: '';
        position: fixed;
        inset: 0;
        background:
            radial-gradient(ellipse 80% 60% at 20% 10%, rgba(34,211,238,0.04), transparent),
            radial-gradient(ellipse 60% 50% at 80% 80%, rgba(52,211,153,0.03), transparent);
        pointer-events: none;
        z-index: 0;
    }

    /* ── Sidebar ─────────────────────────────────────────────────── */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0F1318 0%, #141820 100%) !important;
        border-right: 1px solid var(--glass-border) !important;
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown span,
    section[data-testid="stSidebar"] label {
        color: var(--text-secondary) !important;
    }
    section[data-testid="stSidebar"] .stFileUploader {
        border: 1px dashed rgba(34,211,238,0.25) !important;
        border-radius: 12px !important;
        background: rgba(34,211,238,0.03) !important;
        transition: border-color 0.3s, background 0.3s;
    }
    section[data-testid="stSidebar"] .stFileUploader:hover {
        border-color: rgba(34,211,238,0.5) !important;
        background: rgba(34,211,238,0.06) !important;
    }
    section[data-testid="stSidebar"] hr {
        border-color: var(--glass-border) !important;
    }

    /* ── Typography overrides ────────────────────────────────────── */
    h1, h2, h3, h4 { color: var(--text-primary) !important; font-family: 'DM Sans', sans-serif !important; }
    p, span, label, li { color: var(--text-secondary) !important; }

    /* ── Glass card ──────────────────────────────────────────────── */
    .glass-card {
        background: var(--bg-card);
        backdrop-filter: blur(16px) saturate(1.2);
        -webkit-backdrop-filter: blur(16px) saturate(1.2);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 1.5rem 1.8rem;
        position: relative;
        overflow: hidden;
        transition: transform 0.25s ease, border-color 0.25s ease;
    }
    .glass-card:hover {
        transform: translateY(-2px);
        border-color: rgba(255,255,255,0.10);
    }
    .glass-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.08), transparent);
    }

    /* ── KPI metric cards — Chromatic Language ──────────────────── */
    .kpi-card {
        text-align: left;
        position: relative;
        padding-left: 1.4rem !important;
    }
    .kpi-card::after {
        content: '';
        position: absolute;
        left: 0; top: 0; bottom: 0;
        width: 3px;
        border-radius: 0 2px 2px 0;
    }
    .kpi-card.kpi-bond { background: var(--cl-bond-field) !important; border-color: rgba(34,211,238,0.12) !important; }
    .kpi-card.kpi-bond::after { background: var(--cl-bond); }
    .kpi-card.kpi-etf  { background: var(--cl-etf-field) !important; border-color: rgba(52,211,153,0.12) !important; }
    .kpi-card.kpi-etf::after  { background: var(--cl-etf); }
    .kpi-card.kpi-cert { background: var(--cl-cert-field) !important; border-color: rgba(167,139,250,0.12) !important; }
    .kpi-card.kpi-cert::after { background: var(--cl-cert); }

    .kpi-card .kpi-icon {
        width: 32px; height: 32px;
        border-radius: 8px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    .kpi-card .kpi-label {
        font-size: 0.78rem;
        font-weight: 500;
        letter-spacing: 0.06em;
        text-transform: uppercase;
        color: var(--text-muted) !important;
        margin-bottom: 0.35rem;
    }
    .kpi-card .kpi-value {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.65rem;
        font-weight: 600;
        color: var(--text-primary) !important;
        line-height: 1.2;
    }
    .kpi-card .kpi-sub {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.05rem;
        font-weight: 600;
        margin-top: 0.2rem;
    }

    /* Icon backgrounds per KPI */
    .kpi-icon-value { background: var(--glow-cyan); color: var(--accent-cyan); }
    .kpi-icon-count { background: var(--glow-emerald); color: var(--accent-emerald); }
    .kpi-icon-top   { background: rgba(251,191,36,0.12); color: var(--accent-amber); }

    /* ── Tabs ────────────────────────────────────────────────────── */
    div[data-baseweb="tab-list"] {
        background: transparent !important;
        border-bottom: 1px solid var(--glass-border) !important;
        gap: 0 !important;
    }
    button[data-baseweb="tab"] {
        font-family: 'DM Sans', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.92rem !important;
        color: var(--text-muted) !important;
        border-bottom: 2px solid transparent !important;
        padding: 0.6rem 1.2rem !important;
        transition: color 0.2s, border-color 0.2s !important;
    }
    button[data-baseweb="tab"]:hover {
        color: var(--text-secondary) !important;
    }
    button[data-baseweb="tab"][aria-selected="true"] {
        color: var(--accent-cyan) !important;
        border-bottom-color: var(--accent-cyan) !important;
    }

    /* ── Dataframe ───────────────────────────────────────────────── */
    .stDataFrame {
        border: 1px solid var(--glass-border) !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }

    /* ── Download buttons ────────────────────────────────────────── */
    .stDownloadButton > button {
        background: var(--bg-card) !important;
        border: 1px solid var(--glass-border) !important;
        color: var(--text-primary) !important;
        border-radius: 10px !important;
        font-family: 'Material Symbols Rounded', 'DM Sans', sans-serif !important;
        font-weight: 600 !important;
        padding: 0.55rem 1.4rem !important;
        transition: all 0.25s ease !important;
        display: inline-flex !important;
        align-items: center !important;
        gap: 0.4rem !important;
    }
    .stDownloadButton > button:hover {
        border-color: var(--accent-cyan) !important;
        box-shadow: 0 0 20px var(--glow-cyan) !important;
        transform: translateY(-1px) !important;
    }

    /* ── Landing hero ────────────────────────────────────────────── */
    .hero-container {
        text-align: center;
        padding: 8rem 2rem 4rem;
        position: relative;
    }
    .hero-container::before {
        content: '';
        position: absolute;
        top: 50%; left: 50%;
        transform: translate(-50%, -50%);
        width: 400px; height: 400px;
        background: radial-gradient(circle, rgba(34,211,238,0.08), transparent 70%);
        border-radius: 50%;
        pointer-events: none;
    }
    .hero-logo {
        font-size: 3rem;
        margin-bottom: 1rem;
        display: inline-block;
        background: linear-gradient(135deg, var(--accent-cyan), var(--accent-emerald));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
    }
    .hero-title {
        font-family: 'DM Sans', sans-serif;
        font-size: 2.4rem;
        font-weight: 700;
        color: var(--text-primary) !important;
        margin-bottom: 0.6rem;
        letter-spacing: -0.02em;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: var(--text-muted) !important;
        max-width: 440px;
        margin: 0 auto;
        line-height: 1.6;
    }
    .hero-hint {
        margin-top: 2.5rem;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.8rem;
        color: var(--text-muted) !important;
        background: var(--bg-card);
        border: 1px solid var(--glass-border);
        border-radius: 8px;
        padding: 0.5rem 1rem;
    }
    .hero-hint .arrow { color: var(--accent-cyan); }

    /* ── Section divider ─────────────────────────────────────────── */
    .section-label {
        font-family: 'DM Sans', sans-serif;
        font-size: 0.72rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        color: var(--text-muted) !important;
        margin-bottom: 0.5rem;
        padding-left: 0.2rem;
    }

    /* ── Chromatic Language: class chip badges ───────────────────── */
    .cl-chip {
        display: inline-block;
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.65rem;
        font-weight: 600;
        letter-spacing: 0.06em;
        padding: 0.15rem 0.5rem;
        border-radius: 3px;
        border-left: 2px solid currentColor;
    }
    .cl-bond  { color: #22D3EE; background: rgba(34,211,238,0.08); }
    .cl-etf   { color: #34D399; background: rgba(52,211,153,0.08); }
    .cl-cert  { color: #A78BFA; background: rgba(167,139,250,0.08); }
    .cl-comm  { color: #FBBF24; background: rgba(251,191,36,0.08); }
    .cl-az    { color: #60A5FA; background: rgba(96,165,250,0.08); }
    .cl-altro { color: #4A5568; background: rgba(74,85,104,0.08); }

    /* ── Chromatic accent on active tab ─────────────────────────── */
    button[data-baseweb="tab"][aria-selected="true"] {
        color: var(--cl-bond) !important;
        border-bottom-color: var(--cl-bond) !important;
    }
    </style>
    """)
)


# ── Classification helpers ───────────────────────────────────────────────────

CERT_ISSUERS = [
    "vontobel", "leonteq", "marex", "bnp paribas", "bnp", "societe generale",
    "citigroup", "barclays", "mediobanca", "unicredit",
]
CERT_KEYWORDS = [
    "cash collect", "phoenix", "barrier", "memory", "step down",
    "bonus cap", "express", "reverse convertible", "outperformance",
    "autocallable",
]
ETF_KEYWORDS = [
    "ucits", "etf", "fnd", "ishares", "vanguard", "invesco",
    "lyxor", "amundi", "xtrackers", "wisdomtree", "spdr",
]
BOND_KEYWORDS = [
    "btp", "bund", "treasury", "t-note", "t-bill", "senior preferred",
    "subordinated", "zero coupon", "cct", "corp bond", "govt bond",
    "high yield corp bond", "euromts",
]

SECTOR_MAP = {
    # Technology
    "aapl": "Technology", "msft": "Technology", "nvda": "Technology",
    "goog": "Technology", "googl": "Technology", "meta": "Technology",
    "amzn": "Technology", "tsm": "Technology", "asml": "Technology",
    "stm": "Technology", "sap": "Technology", "intc": "Technology",
    "amd": "Technology", "crm": "Technology", "adbe": "Technology",
    "orcl": "Technology", "csco": "Technology", "ibm": "Technology",
    # Energy
    "eni": "Energy", "xom": "Energy", "bp": "Energy",
    "shel": "Energy", "tot": "Energy", "cvx": "Energy",
    "cop": "Energy", "eog": "Energy", "slb": "Energy",
    "tenaris": "Energy", "saipem": "Energy",
    # Finance
    "jpm": "Finance", "isp": "Finance", "ucg": "Finance",
    "intesa": "Finance", "unicredit": "Finance", "mediobanca": "Finance",
    "generali": "Finance", "bpm": "Finance", "bper": "Finance",
    "gs": "Finance", "ms": "Finance", "bnp": "Finance",
    "ing": "Finance", "hsbc": "Finance", "ubs": "Finance",
    "dbk": "Finance", "san": "Finance",
    # Healthcare
    "pfe": "Healthcare", "jnj": "Healthcare", "unh": "Healthcare",
    "mrk": "Healthcare", "abbv": "Healthcare", "lly": "Healthcare",
    "novo": "Healthcare", "azn": "Healthcare", "gsk": "Healthcare",
    "roche": "Healthcare", "sanofi": "Healthcare", "bayer": "Healthcare",
    "recordati": "Healthcare", "diasorin": "Healthcare",
    # Utilities
    "enel": "Utilities", "a2a": "Utilities", "terna": "Utilities",
    "hera": "Utilities", "snam": "Utilities", "italgas": "Utilities",
    "erg": "Utilities", "nee": "Utilities", "duke": "Utilities",
    # Consumer / Retail
    "ko": "Consumer", "pep": "Consumer", "pg": "Consumer",
    "nesn": "Consumer", "ul": "Consumer", "lvmh": "Consumer",
    "mc": "Consumer", "or": "Consumer", "campari": "Consumer",
    # Industrials
    "leonardo": "Industrials", "prysmian": "Industrials",
    "cnh": "Industrials", "stellantis": "Industrials",
    "ferrari": "Industrials", "pirelli": "Industrials",
    "hon": "Industrials", "cat": "Industrials", "ba": "Industrials",
    "siemens": "Industrials", "airbus": "Industrials",
    # Telecom
    "tim": "Telecom", "t": "Telecom", "vz": "Telecom",
    "dte": "Telecom", "orange": "Telecom",
    # Real Estate
    "spg": "Real Estate", "o": "Real Estate", "amt": "Real Estate",
}

# ── Sector keywords (per ETF tematici / settoriali) ─────────────────────────
SECTOR_KEYWORD_MAP = {
    "Technology": [
        "technology", "tech", "information tech", "digital", "semiconductor",
        "artificial intelligence", " ai ", "robotics", "automation", "cyber",
        "cloud", "software", "nasdaq", "blockchain",
    ],
    "Healthcare": [
        "healthcare", "health care", "pharma", "biotech", "medical",
        "genomic", "aging population",
    ],
    "Energy": [
        "energy", "oil", "gas", "petroleum", "clean energy", "solar",
        "wind", "renewable", "nuclear",
    ],
    "Finance": [
        "financial", "financials", "banking", "banks", "insurance",
    ],
    "Utilities": [
        "utilities", "utility", "infrastructure",
    ],
    "Real Estate": [
        "real estate", "reit", "property", "immobiliare",
    ],
    "Consumer": [
        "consumer", "retail", "staples", "discretionary", "luxury",
        "food", "beverage",
    ],
    "Industrials": [
        "industrial", "aerospace", "defense", "defence", "materials",
        "construction", "machinery",
    ],
    "Telecom": [
        "telecom", "communication", "media",
    ],
    "ESG / SRI": [
        "esg", "sri", "sustainable", "sustainability", "climate",
        "paris aligned", "social responsibility", "green",
    ],
}

# ── Geography keywords (per ETF / fondi) ────────────────────────────────────
GEOGRAPHY_KEYWORD_MAP = {
    "World": [
        "world", "all-world", "global", "msci world", "acwi",
        "all country", "ftse all",
    ],
    "USA": [
        "s&p 500", "s&p500", "usa", "us ", "u.s.", "america",
        "nasdaq", "dow jones", "russell", "msci usa",
    ],
    "Europa": [
        "europe", "euro stoxx", "europa", "msci europe", "stoxx 600",
        "eurozone", "ftse developed europe", "euro area",
    ],
    "Italia": [
        "italy", "italia", "ftse mib", "btp", "piazza affari",
    ],
    "Emergenti": [
        "emerging", "em imi", "em ", "msci em", "ftse emerging",
    ],
    "Cina": [
        "china", "cina", "msci china", "csi 300", "hang seng",
        "shanghai",
    ],
    "Giappone": [
        "japan", "giappone", "topix", "nikkei", "msci japan",
    ],
    "Asia Pacifico": [
        "asia", "pacific", "apac", "asia-pacific", "asean",
        "asia ex japan", "asia ex-japan",
    ],
    "UK": [
        "uk ", "united kingdom", "ftse 100", "ftse 250", "britain",
        "british",
    ],
    "Germania": [
        "germany", "germania", "dax",
    ],
    "America Latina": [
        "latin america", "latam", "brazil", "brasil", "mexico",
        "messico",
    ],
    "Africa / Frontiera": [
        "africa", "frontier", "frontiera",
    ],
}

# ── ISIN country prefix → geography (per azioni dirette / bond sovrani) ─────
ISIN_COUNTRY_MAP = {
    "IT": "Italia", "US": "USA", "DE": "Germania", "FR": "Europa",
    "GB": "UK", "NL": "Europa", "ES": "Europa", "CH": "Europa",
    "JP": "Giappone", "CN": "Cina", "HK": "Cina",
    "AU": "Asia Pacifico", "KR": "Asia Pacifico", "TW": "Asia Pacifico",
    "BR": "America Latina", "MX": "America Latina",
    "IE": None, "LU": None,  # domicilio fondo, non esposizione geografica
}


BOND_UNDERLYING_KEYWORDS = [
    "bond", "obbligazion", "govt", "government", "treasury", "t-bill",
    "t-note", "aggregate", "corporate", "high yield", "investment grade",
    "fixed income", "inflation linked", "euromts", "barclays",
]

MONETARY_KEYWORDS = [
    "money market", "monetario", "short maturity", "overnight",
    "cash", "liquidity", "eonia", "ester", "€str", "floating rate",
    "ultra short", "enhanced cash",
]

COMMODITY_KEYWORDS = [
    "gold", "oro", "silver", "argento", "platinum", "platino", "palladium",
    "palladio", "commodity", "commodities", "physical", "oil", "petrolio",
    "natural gas", "agriculture", "metals", "copper", "rame",
    "etc ", "etn ",
]


def classify_asset(name: str) -> str:
    low = name.lower()
    has_issuer = any(k in low for k in CERT_ISSUERS)
    has_cert_kw = any(k in low for k in CERT_KEYWORDS)
    # 1) Certificates
    if has_issuer and has_cert_kw:
        return "CERTIFICATE"
    if has_issuer and not any(k in low for k in ETF_KEYWORDS + BOND_KEYWORDS):
        return "CERTIFICATE"
    # 2) ETF/ETC/ETN — smista per sottostante
    is_etf = any(k in low for k in ETF_KEYWORDS)
    if is_etf:
        # Commodity / Oro / Materie prime → COMMODITY
        is_commodity = any(k in low for k in COMMODITY_KEYWORDS)
        if is_commodity:
            return "COMMODITY"
        # Monetari → BOND
        is_monetary = any(k in low for k in MONETARY_KEYWORDS)
        if is_monetary:
            return "BOND"
        # Obbligazionario sottostante → BOND
        is_bond_underlying = any(k in low for k in BOND_UNDERLYING_KEYWORDS + BOND_KEYWORDS)
        if is_bond_underlying:
            return "BOND"
        return "ETF"
    # 3) Bonds diretti
    if any(k in low for k in BOND_KEYWORDS):
        return "BOND"
    if re.search(r"\b20\d{2}\b", low) and "%" in low:
        return "BOND"
    # 4) Azione
    if "azione" in low:
        return "AZIONE"
    return "ALTRO"


def classify_subtype(name: str, classe: str) -> str:
    """Sub-classification per analisi diversificazione (financial-analyst skill)."""
    low = name.lower()

    if classe == "BOND":
        # Monetary / ultra-short — ETF monetari assimilati a obbligazionario breve
        if any(k in low for k in ("money market", "monetario", "short maturity", "overnight",
                                   "liquidity", "eonia", "ester", "€str", "enhanced cash",
                                   "ultra short", "floating rate")):
            return "Monetario / Breve Termine"
        # Government
        if any(k in low for k in ("gov", "btp", "bund", "treasury", "t-bill", "t-note", "cct", "stato")):
            if any(k in low for k in ("short", "1-3", "breve", "maturity")):
                return "Gov. Breve Termine"
            if any(k in low for k in ("25+", "long", "lungo", "2037", "2040", "2050")):
                return "Gov. Lungo Termine"
            return "Gov. Medio Termine"
        # Corporate
        if any(k in low for k in ("corporate", "corp bond", "credit")):
            if "high yield" in low:
                return "Corporate High Yield"
            return "Corporate Inv. Grade"
        if "high yield" in low:
            return "Corporate High Yield"
        # Inflation
        if any(k in low for k in ("inflation", "indicizzat")):
            return "Inflation Linked"
        # Aggregate / Global
        if any(k in low for k in ("aggregate", "global", "broad")):
            return "Obbligazionario Globale"
        if "euromts" in low or "eurozone" in low or "euro" in low:
            return "Gov. Euro"
        return "Obbligazionario Altro"

    if classe in ("ETF", "AZIONE"):
        # Geographic
        if any(k in low for k in ("emerging", "em imi", "em ")):
            return "Azionario Emergenti"
        if any(k in low for k in ("china", "cina")):
            return "Azionario Cina"
        if any(k in low for k in ("europe", "euro stoxx", "europa", "msci europe")):
            return "Azionario Europa"
        if any(k in low for k in ("s&p 500", "usa", "us ", "america")):
            return "Azionario USA"
        if any(k in low for k in ("world", "all-world", "global", "msci world", "acwi")):
            if "small" in low:
                return "Azionario World Small Cap"
            if "value" in low:
                return "Azionario World Value"
            if "divid" in low or "div." in low or "div " in low:
                return "Azionario World Dividendo"
            return "Azionario World"
        if any(k in low for k in ("japan", "giappone", "topix", "nikkei")):
            return "Azionario Giappone"
        if "divid" in low or "div." in low:
            return "Azionario Dividendo"
        if "azione" in low:
            return "Azione Singola"
        return "Azionario Altro"

    if classe == "CERTIFICATE":
        return "Certificate"

    if classe == "COMMODITY":
        if any(k in low for k in ("gold", "oro")):
            return "Oro"
        if any(k in low for k in ("silver", "argento")):
            return "Argento"
        if any(k in low for k in ("oil", "petrolio", "crude")):
            return "Petrolio"
        if any(k in low for k in ("natural gas", "gas naturale")):
            return "Gas Naturale"
        return "Commodity Altro"

    return "Altro"


def infer_sector(name: str, current: str, classe: str = "") -> str:
    """Infer sector from name using: existing value → keyword map → ticker map."""
    if pd.notna(current) and current.strip() not in ("", "N/A", "n/a", "n/d", "N/D"):
        return current.strip()
    low = name.lower()
    # Bond e Commodity: settore non applicabile nel senso equity
    if classe in ("BOND", "COMMODITY"):
        return "—"
    # 1) Keyword-based sector detection (ETF names are descriptive)
    for sector, keywords in SECTOR_KEYWORD_MAP.items():
        if any(k in low for k in keywords):
            return sector
    # 2) Ticker-based fallback — word boundary match to avoid "ms" inside "MSCI"
    for ticker, sector in SECTOR_MAP.items():
        if re.search(r"\b" + re.escape(ticker) + r"\b", low):
            return sector
    # 3) Broad/world ETF → multi-settore
    is_etf = any(k in low for k in ETF_KEYWORDS)
    if is_etf and any(k in low for k in ("world", "all-world", "global", "acwi", "ftse all", "stoxx")):
        return "Multi-settore"
    return "Non classificato"


def infer_geography(name: str, isin: str | None, classe: str) -> str:
    """Infer geographic exposure from name and ISIN."""
    low = name.lower()
    # 1) Keyword-based geography from fund/ETF name
    for geo, keywords in GEOGRAPHY_KEYWORD_MAP.items():
        if any(k in low for k in keywords):
            return geo
    # 2) ISIN prefix for direct equities and government bonds
    if pd.notna(isin) and isinstance(isin, str) and len(isin) >= 2:
        prefix = isin[:2].upper()
        # IE/LU = fund domicile, not geographic exposure — skip
        geo = ISIN_COUNTRY_MAP.get(prefix)
        if geo is not None:
            return geo
    # 3) Heuristics for bond issuers
    if classe == "BOND":
        if any(k in low for k in ("btp", "cct", "italia")):
            return "Italia"
        if "bund" in low:
            return "Germania"
        if "treasury" in low or "t-note" in low or "t-bill" in low:
            return "USA"
        if "euromts" in low or "eurozone" in low:
            return "Europa"
    # 4) Commodity = global
    if classe == "COMMODITY":
        return "Globale"
    return "Non classificato"


# ── Data cleaning ────────────────────────────────────────────────────────────

HEADER_MAP = {
    "descrizione titolo": "Nome",
    "description": "Nome",
    "nome": "Nome",
    "security name": "Nome",
    "isin": "ISIN",
    "codice isin": "ISIN",
    "isin code": "ISIN",
    "security id": "ISIN",
    "quantita": "Quantità",
    "quantità": "Quantità",
    "quantity": "Quantità",
    "qty": "Quantità",
    "prezzo acquisto": "Prezzo Acquisto",
    "prezzo_acquisto": "Prezzo Acquisto",
    "purchase price": "Prezzo Acquisto",
    "valore di mercato (eur)": "Controvalore",
    "valore di mercato": "Controvalore",
    "market value": "Controvalore",
    "controvalore": "Controvalore",
    "settore_presunto": "Settore",
    "settore": "Settore",
    "sector": "Settore",
    "data_acquisto": "Data Acquisto",
    "data acquisto": "Data Acquisto",
    "purchase date": "Data Acquisto",
    "note": "Note",
    "notes": "Note",
    # Export bancari italiani
    "descrizione": "Nome",
    "titolo": "Nome",
    "denominazione": "Nome",
    "codice isin": "ISIN",
    "cod. isin": "ISIN",
    # Controvalore — varie diciture incluse quelle con "€"
    "valore di mercato totale": "Controvalore",
    "controvalore di mercato": "Controvalore",
    "valore attuale": "Controvalore",
    "valore portafoglio": "Controvalore",
    "ctv attuale": "Controvalore",
    "ctv di mercato": "Controvalore",
    "valore di mercato €": "Controvalore",
    "valore di mercato eur": "Controvalore",
    "cambio di mercato": "Cambio Mercato",
    # Prezzi
    "p.zo di mercato": "Prezzo Mercato",
    "prezzo di mercato": "Prezzo Mercato",
    "p.zo medio di carico": "Prezzo Acquisto",
    "prezzo medio di carico": "Prezzo Acquisto",
    "prezzo medio": "Prezzo Acquisto",
    "valore di carico": "Valore Carico",
    # Quantità
    "quantità": "Quantità",
    "q.tà": "Quantità",
    "n. titoli": "Quantità",
    # Metadati
    "simbolo": "Ticker",
    "mercato": "Mercato",
    "valuta": "Valuta",
    "strumento": "Tipo Strumento",
    "cambio di carico": "Cambio Carico",
    "plus/minus": "Plus/Minus",
    "plus/minusvalenza": "Plus/Minus",
    "var%": "Var %",
    "rendimento": "Rendimento %",
    "peso": "Peso %",
    "peso %": "Peso %",
    "peso sul portafoglio": "Peso %",
    "asset class": "Classe",
    "categoria": "Settore",
    "tipo strumento": "Classe",
}


def clean_numeric(val) -> float | None:
    if pd.isna(val):
        return None
    s = str(val).strip()
    s = re.sub(r"[€$£USDEUR\s]", "", s)
    if s in ("", "N/A", "n/a", "n/d", "N/D", "-"):
        return None
    if re.match(r"^-?\d{1,3}(\.\d{3})*(,\d+)?$", s):
        s = s.replace(".", "").replace(",", ".")
    elif "," in s and "." not in s:
        s = s.replace(",", ".")
    try:
        return float(s)
    except ValueError:
        return None


def _norm_key(col: str) -> str:
    s = str(col).strip().lower()
    s = re.sub(r"\s+", " ", s)
    return s


def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    # Sort columns so "valore di mercato" variants come before less specific ones
    # This ensures Controvalore maps to the real market value, not a cambio
    def _priority(col: str) -> int:
        k = _norm_key(col)
        if "valore di mercato" in k:
            return 0
        if "controvalore" in k or "market value" in k:
            return 1
        return 2

    sorted_cols = sorted(df.columns, key=_priority)

    rename = {}
    seen: set[str] = set()
    for col in sorted_cols:
        key = _norm_key(col)
        target = HEADER_MAP.get(key)
        # Fuzzy: strip trailing currency symbols
        if target is None:
            key2 = re.sub(r"[€$£]+$", "", key).strip()
            target = HEADER_MAP.get(key2)
        if target and target not in seen:
            rename[col] = target
            seen.add(target)
    df = df.rename(columns=rename)
    # Drop any remaining duplicate columns (keep first)
    df = df.loc[:, ~df.columns.duplicated()]
    return df


def _strip_summary_rows(df: pd.DataFrame) -> pd.DataFrame:
    """Remove summary/total rows that appear at the bottom of bank exports."""
    name_col = None
    for c in df.columns:
        if _norm_key(c) in ("titolo", "nome", "descrizione titolo", "descrizione", "denominazione"):
            name_col = c
            break
    if name_col is None:
        # Try after rename candidates
        for c in df.columns:
            if c == "Nome":
                name_col = c
                break
    if name_col is not None:
        skip_labels = {"totale", "total", "eur", "usd", "gbp", "riepilogo", "summary", ""}
        mask = df[name_col].apply(
            lambda v: str(v).strip().lower() not in skip_labels if pd.notna(v) else False
        )
        df = df[mask].reset_index(drop=True)
    else:
        # Fallback: drop fully-empty rows
        df = df.dropna(how="all").reset_index(drop=True)
    return df


def process_portfolio(df: pd.DataFrame) -> pd.DataFrame:
    df = _strip_summary_rows(df)
    df = normalize_columns(df)
    for col in ("Nome", "ISIN", "Quantità", "Controvalore"):
        if col not in df.columns:
            df[col] = None
    df["Quantità"] = df["Quantità"].apply(clean_numeric)
    df["Controvalore"] = df["Controvalore"].apply(clean_numeric)
    if "Prezzo Acquisto" in df.columns:
        df["Prezzo Acquisto"] = df["Prezzo Acquisto"].apply(clean_numeric)
    # Fallback: se Controvalore è tutto nullo, prova a calcolarlo
    if df["Controvalore"].isna().all():
        if "Valore Carico" in df.columns:
            df["Controvalore"] = df["Valore Carico"].apply(clean_numeric)
        elif "Prezzo Mercato" in df.columns and not df["Quantità"].isna().all():
            pm = df["Prezzo Mercato"].apply(clean_numeric)
            df["Controvalore"] = pm * df["Quantità"]
    df["Classe"] = df["Nome"].fillna("").astype(str).apply(classify_asset)
    settore_col = "Settore" if "Settore" in df.columns else None
    df["Settore"] = df.apply(
        lambda r: infer_sector(
            str(r["Nome"] or ""),
            r.get("Settore") if settore_col else None,
            r["Classe"],
        ),
        axis=1,
    )
    # Sub-classification per diversificazione
    df["Sottotipo"] = df.apply(
        lambda r: classify_subtype(str(r["Nome"] or ""), r["Classe"]),
        axis=1,
    )
    # Geographic exposure
    df["Geografia"] = df.apply(
        lambda r: infer_geography(
            str(r["Nome"] or ""),
            r.get("ISIN"),
            r["Classe"],
        ),
        axis=1,
    )
    total = df["Controvalore"].sum()
    df["Peso %"] = (df["Controvalore"] / total * 100).round(2) if total > 0 else 0
    return df


# ── Excel export ─────────────────────────────────────────────────────────────

def to_excel_styled(df: pd.DataFrame, summary: dict | None = None) -> bytes:
    """Export professionale multi-sheet seguendo xlsx skill standards.

    Parameters
    ----------
    df : pd.DataFrame – portfolio data
    summary : dict | None – optional summary metrics for Riepilogo sheet
    """
    from openpyxl import Workbook
    from openpyxl.styles import Font, Border, Side, PatternFill, Alignment, numbers
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = "Portafoglio"

    # ── Style definitions (xlsx skill color coding) ──
    font_header = Font(name="Arial", bold=True, size=10, color="000000")
    font_blue = Font(name="Arial", size=10, color="0000FF")       # inputs
    font_black = Font(name="Arial", size=10, color="000000")      # formulas/computed
    font_green = Font(name="Arial", size=10, color="008000")      # cross-sheet refs
    fill_yellow = PatternFill("solid", fgColor="FFFF00")          # N/A attention
    fill_header = PatternFill("solid", fgColor="D9E2F3")
    thin = Side(style="thin")
    border_all = Border(top=thin, bottom=thin, left=thin, right=thin)
    border_header = Border(bottom=Side(style="medium"))
    align_right = Alignment(horizontal="right")
    align_center = Alignment(horizontal="center")

    blue_cols = {"ISIN", "Nome"}
    currency_cols = {"Controvalore", "Prezzo Acquisto", "Valore Carico", "Prezzo Mercato"}
    pct_cols = {"Peso %", "Var %", "Rendimento %"}

    # ── Headers ──
    for col_idx, col_name in enumerate(df.columns, 1):
        cell = ws.cell(row=1, column=col_idx, value=col_name)
        cell.font = font_header
        cell.fill = fill_header
        cell.border = border_header
        cell.alignment = align_center

    # ── Data rows ──
    n_rows = len(df)
    for row_idx, (_, row_data) in enumerate(df.iterrows(), 2):
        for col_idx, col_name in enumerate(df.columns, 1):
            val = row_data[col_name]
            cell = ws.cell(row=row_idx, column=col_idx)
            cell.border = border_all

            # Write value
            if pd.isna(val):
                cell.value = "N/D"
                cell.fill = fill_yellow
                cell.font = Font(name="Arial", size=10, color="B7791F")
                continue

            cell.value = val

            # Font color
            if col_name in blue_cols:
                cell.font = font_blue
            else:
                cell.font = font_black

            # Number formats
            if col_name in currency_cols and isinstance(val, (int, float)):
                cell.number_format = '€ #,##0.00;(€ #,##0.00);"-"'
                cell.alignment = align_right
            elif col_name in pct_cols and isinstance(val, (int, float)):
                cell.number_format = '0.0%' if val <= 1 else '0.00"%"'
                cell.alignment = align_right
            elif col_name == "Quantità" and isinstance(val, (int, float)):
                cell.number_format = '#,##0'
                cell.alignment = align_right

    # ── Peso % as Excel formulas (xlsx skill: formulas, not hardcodes) ──
    peso_col_idx = None
    ctv_col_idx = None
    for idx, col_name in enumerate(df.columns, 1):
        if col_name == "Peso %":
            peso_col_idx = idx
        elif col_name == "Controvalore":
            ctv_col_idx = idx

    if peso_col_idx and ctv_col_idx:
        ctv_letter = get_column_letter(ctv_col_idx)
        peso_letter = get_column_letter(peso_col_idx)
        for row_idx in range(2, n_rows + 2):
            cell = ws.cell(row=row_idx, column=peso_col_idx)
            cell.value = f"={ctv_letter}{row_idx}/SUM({ctv_letter}$2:{ctv_letter}${n_rows + 1})*100"
            cell.number_format = '0.00"%"'
            cell.font = font_black
            cell.alignment = align_right
            cell.border = border_all

    # ── Totale row ──
    total_row = n_rows + 2
    ws.cell(row=total_row, column=1, value="TOTALE").font = Font(
        name="Arial", bold=True, size=10, color="000000"
    )
    ws.cell(row=total_row, column=1).border = border_all
    if ctv_col_idx:
        ctv_letter = get_column_letter(ctv_col_idx)
        total_cell = ws.cell(row=total_row, column=ctv_col_idx)
        total_cell.value = f"=SUM({ctv_letter}2:{ctv_letter}{n_rows + 1})"
        total_cell.number_format = '€ #,##0.00'
        total_cell.font = Font(name="Arial", bold=True, size=10, color="000000")
        total_cell.border = border_all
        total_cell.alignment = align_right
    if peso_col_idx:
        pct_cell = ws.cell(row=total_row, column=peso_col_idx)
        pct_cell.value = "100.00%"
        pct_cell.font = Font(name="Arial", bold=True, size=10, color="000000")
        pct_cell.border = border_all
        pct_cell.alignment = align_right

    # ── Auto-width columns ──
    for col_idx, col_name in enumerate(df.columns, 1):
        max_len = len(str(col_name))
        for row in ws.iter_rows(min_row=2, max_row=n_rows + 2, min_col=col_idx, max_col=col_idx):
            for cell in row:
                if cell.value is not None:
                    max_len = max(max_len, len(str(cell.value)))
        ws.column_dimensions[get_column_letter(col_idx)].width = min(max_len + 3, 45)

    # ── Freeze header row ──
    ws.freeze_panes = "A2"

    # ── Sheet 2: Riepilogo ──
    if summary:
        ws2 = wb.create_sheet("Riepilogo")
        ws2.column_dimensions["A"].width = 30
        ws2.column_dimensions["B"].width = 20

        riepilogo_data = [
            ("Riepilogo Portafoglio", ""),
            ("", ""),
            ("Controvalore Totale", summary.get("total_value", 0)),
            ("Numero Titoli", summary.get("n_assets", 0)),
            ("Asset Più Pesante", summary.get("heaviest", "")),
            ("Peso Asset Più Pesante", summary.get("heaviest_pct", 0)),
            ("", ""),
            ("Allocazione Macro", ""),
            ("Obbligazionario %", summary.get("bond_pct", 0)),
            ("Azionario %", summary.get("eq_pct", 0)),
            ("Altro %", summary.get("other_pct", 0)),
        ]
        # Add risk metrics if available
        if "hhi" in summary:
            riepilogo_data += [
                ("", ""),
                ("Metriche di Rischio", ""),
                ("HHI (Concentrazione)", summary.get("hhi", 0)),
                ("Top-5 Concentrazione %", summary.get("top5_pct", 0)),
                ("Sottocategorie Attive", summary.get("n_subtypes", 0)),
                ("Score Diversificazione", summary.get("diversification_rating", "")),
            ]

        for row_idx, (label, value) in enumerate(riepilogo_data, 1):
            lc = ws2.cell(row=row_idx, column=1, value=label)
            vc = ws2.cell(row=row_idx, column=2, value=value)
            lc.border = border_all
            vc.border = border_all

            if row_idx in (1, 8, 13):
                lc.font = Font(name="Arial", bold=True, size=11, color="000000")
                lc.fill = fill_header
                vc.fill = fill_header
            else:
                lc.font = Font(name="Arial", size=10, color="000000")
                # Green font for cross-sheet references
                vc.font = font_green

            if isinstance(value, (int, float)):
                vc.alignment = align_right
                if "%" in label:
                    vc.number_format = '0.0"%"'
                elif "Totale" in label:
                    vc.number_format = '€ #,##0.00'
                elif "HHI" in label:
                    vc.number_format = '0.0000'

    buf = io.BytesIO()
    wb.save(buf)
    return buf.getvalue()


# ── Financial-Analyst skill: portfolio report ────────────────────────────────

def generate_fa_report(df: pd.DataFrame, metrics: dict) -> dict:
    """
    Analisi completa del portafoglio ispirata alla financial-analyst skill.
    Restituisce sezioni strutturate: allocazione, concentrazione, diversificazione,
    geografia, raccomandazioni.
    """
    total = metrics.get("total_value", 0)
    n     = metrics.get("n_assets", 0)
    hhi   = metrics.get("hhi", 0)

    # ── 1. Allocazione macro ──────────────────────────────────────────────────
    class_split = df.groupby("Classe")["Controvalore"].sum().sort_values(ascending=False)
    alloc = {cls: round(v / total * 100, 1) for cls, v in class_split.items() if total > 0}

    bond_pct  = metrics.get("bond_pct", 0)
    eq_pct    = metrics.get("eq_pct", 0)
    other_pct = metrics.get("other_pct", 0)

    if bond_pct > 60:
        alloc_profile = ("Difensivo", "#22D3EE",
            f"Il portafoglio è prevalentemente obbligazionario ({bond_pct:.1f}%). "
            "Questo posizionamento riduce la volatilità ma limita il potenziale di rendimento a lungo termine.")
    elif eq_pct > 60:
        alloc_profile = ("Aggressivo", "#34D399",
            f"Il portafoglio è prevalentemente azionario/ETF ({eq_pct:.1f}%). "
            "Esposizione elevata alla volatilità di mercato; adatto a orizzonti temporali lunghi.")
    elif 35 <= bond_pct <= 65 and 35 <= eq_pct <= 65:
        alloc_profile = ("Bilanciato", "#A78BFA",
            f"Allocazione equilibrata tra obbligazionario ({bond_pct:.1f}%) e azionario ({eq_pct:.1f}%). "
            "Profilo coerente con obiettivi di crescita moderata e controllo del rischio.")
    else:
        alloc_profile = ("Misto", "#FBBF24",
            f"Composizione diversificata: obbligazionario {bond_pct:.1f}%, azionario {eq_pct:.1f}%, altro {other_pct:.1f}%.")

    # ── 2. Concentrazione (HHI benchmark dalla financial-analyst skill) ────────
    # HHI < 0.01 = molto diversificato, 0.01–0.15 = moderato, > 0.15 = concentrato
    if hhi < 0.06:
        hhi_label = ("Eccellente", "#34D399",
            f"HHI {hhi:.4f} — portafoglio ben distribuito. "
            "Il rischio è suddiviso su molte posizioni con peso equilibrato.")
    elif hhi < 0.10:
        hhi_label = ("Buono", "#34D399",
            f"HHI {hhi:.4f} — diversificazione soddisfacente. "
            "Qualche posizione di maggior peso, ma entro soglie accettabili.")
    elif hhi < 0.15:
        hhi_label = ("Accettabile", "#FBBF24",
            f"HHI {hhi:.4f} — concentrazione moderata. "
            "Alcune posizioni pesano significativamente: monitorare il rischio single-name.")
    else:
        hhi_label = ("Concentrato", "#FB7185",
            f"HHI {hhi:.4f} — portafoglio concentrato. "
            "Poche posizioni dominano il valore: alto rischio specifico.")

    # ── 3. Top holding analysis ───────────────────────────────────────────────
    df_sorted = df.dropna(subset=["Controvalore"]).sort_values("Controvalore", ascending=False)
    top5 = df_sorted.head(5)[["Nome", "Classe", "Controvalore", "Peso %"]].copy()
    top5_pct = metrics.get("top5_pct", 0)

    # ── 4. Diversificazione per sottotipo ─────────────────────────────────────
    subtype_w = df.groupby("Sottotipo")["Controvalore"].sum() / total * 100
    active_subtypes = subtype_w[subtype_w > 2].sort_values(ascending=False)
    n_sub = metrics.get("n_subtypes", 0)

    if n_sub >= 7:
        sub_comment = "Eccellente copertura per sottocategoria: il portafoglio tocca molti segmenti di mercato."
    elif n_sub >= 5:
        sub_comment = "Buona diversificazione per sottocategoria."
    elif n_sub >= 3:
        sub_comment = "Diversificazione parziale: ampliare la copertura su altri segmenti migliorerebbe il profilo di rischio."
    else:
        sub_comment = "Diversificazione per sottocategoria limitata: il portafoglio è concentrato su pochi segmenti."

    # ── 5. Analisi geografica ──────────────────────────────────────────────────
    geo_split = df.groupby("Geografia")["Controvalore"].sum().sort_values(ascending=False)
    geo_pct = {g: round(v / total * 100, 1) for g, v in geo_split.items() if total > 0}
    top_geo = list(geo_pct.items())[:3]

    non_classified_geo = geo_pct.get("Non classificato", 0)
    if non_classified_geo > 30:
        geo_note = f"Attenzione: il {non_classified_geo:.1f}% del portafoglio ha esposizione geografica non classificata."
    elif len(geo_pct) >= 4:
        geo_note = "Buona diversificazione geografica su più aree."
    else:
        geo_note = "Esposizione geografica concentrata su poche aree."

    # ── 6. Raccomandazioni operative ──────────────────────────────────────────
    recommendations = []
    if hhi >= 0.15:
        recommendations.append(("Alta priorità", "#FB7185",
            "Ridurre la concentrazione aumentando il numero di posizioni o ribilanciando le più pesanti."))
    if metrics.get("max_weight", 0) > 25:
        heaviest = df_sorted.iloc[0]["Nome"] if len(df_sorted) > 0 else "N/A"
        recommendations.append(("Alta priorità", "#FB7185",
            f'"{heaviest[:40]}" pesa il {metrics.get("max_weight",0):.1f}%: considerare un parziale alleggerimento.'))
    if bond_pct > 70:
        recommendations.append(("Moderata", "#FBBF24",
            "Allocazione obbligazionaria molto elevata: valutare l'aggiunta di componente azionaria per il lungo periodo."))
    if eq_pct > 80:
        recommendations.append(("Moderata", "#FBBF24",
            "Esposizione azionaria molto elevata: una quota obbligazionaria migliorerebbe la resilienza in fase di correzione."))
    if non_classified_geo > 30:
        recommendations.append(("Bassa priorità", "#4A5568",
            "Verificare e completare la classificazione geografica delle posizioni non classificate."))
    if n_sub <= 2:
        recommendations.append(("Moderata", "#FBBF24",
            "Ampliare la diversificazione per sottocategoria aggiungendo strumenti di classi diverse."))
    if not recommendations:
        recommendations.append(("Nessuna azione urgente", "#34D399",
            "Il portafoglio presenta un profilo di rischio equilibrato. Mantenere il monitoraggio periodico."))

    return {
        "alloc_profile": alloc_profile,
        "alloc": alloc,
        "hhi_label": hhi_label,
        "top5": top5,
        "top5_pct": top5_pct,
        "active_subtypes": active_subtypes,
        "sub_comment": sub_comment,
        "geo_pct": geo_pct,
        "top_geo": top_geo,
        "geo_note": geo_note,
        "recommendations": recommendations,
        "bond_pct": bond_pct,
        "eq_pct": eq_pct,
        "other_pct": other_pct,
        "total": total,
        "n": n,
    }


# ── Portfolio risk analytics (financial-analyst skill) ──────────────────────

def compute_risk_metrics(df: pd.DataFrame) -> dict:
    """Compute portfolio-level risk & concentration metrics."""
    weights = df["Controvalore"].dropna()
    total = weights.sum()
    if total <= 0:
        return {}
    w = weights / total
    # HHI (Herfindahl-Hirschman Index): sum of squared weights
    hhi = (w ** 2).sum()
    # Top-5 concentration
    top5_pct = w.nlargest(5).sum() * 100
    # Active subtypes (with >2% weight)
    subtype_weights = df.groupby("Sottotipo")["Controvalore"].sum() / total * 100
    n_subtypes = (subtype_weights > 2).sum()
    # Asset class split
    class_split = df.groupby("Classe")["Controvalore"].sum() / total * 100
    bond_pct = class_split.get("BOND", 0)
    eq_pct = class_split.get("ETF", 0) + class_split.get("AZIONE", 0)
    other_pct = 100 - bond_pct - eq_pct
    # Single-name risk
    max_weight = w.max() * 100
    # Diversification rating (based on financial-analyst benchmarks)
    if hhi < 0.06:
        div_rating = "Eccellente"
        div_color = "#34D399"
    elif hhi < 0.10:
        div_rating = "Buona"
        div_color = "#34D399"
    elif hhi < 0.15:
        div_rating = "Accettabile"
        div_color = "#FBBF24"
    else:
        div_rating = "Concentrato"
        div_color = "#FB7185"
    # Concentration rating
    if max_weight > 25:
        conc_rating = "Alto Rischio"
        conc_color = "#FB7185"
    elif max_weight > 15:
        conc_rating = "Moderato"
        conc_color = "#FBBF24"
    else:
        conc_rating = "Basso"
        conc_color = "#34D399"

    return {
        "hhi": round(hhi, 4),
        "top5_pct": round(top5_pct, 1),
        "n_subtypes": int(n_subtypes),
        "bond_pct": round(bond_pct, 1),
        "eq_pct": round(eq_pct, 1),
        "other_pct": round(other_pct, 1),
        "max_weight": round(max_weight, 1),
        "diversification_rating": div_rating,
        "diversification_color": div_color,
        "concentration_rating": conc_rating,
        "concentration_color": conc_color,
        "n_assets": len(df),
        "total_value": round(total, 2),
    }


def generate_insights(df: pd.DataFrame, metrics: dict) -> list[str]:
    """Generate natural-language portfolio insights in Italian."""
    insights = []
    n = metrics.get("n_assets", 0)
    total = metrics.get("total_value", 0)
    insights.append(
        f"Il portafoglio comprende {n} titoli per un controvalore totale di € {total:,.2f}."
    )
    # Allocation bias
    bond_pct = metrics.get("bond_pct", 0)
    eq_pct = metrics.get("eq_pct", 0)
    if bond_pct > 60:
        insights.append(
            f"L'allocazione è sbilanciata verso l'obbligazionario ({bond_pct:.1f}%), "
            "suggerendo un posizionamento difensivo."
        )
    elif eq_pct > 60:
        insights.append(
            f"L'allocazione è sbilanciata verso l'azionario ({eq_pct:.1f}%), "
            "con una maggiore esposizione alla volatilità di mercato."
        )
    elif 35 <= bond_pct <= 65 and 35 <= eq_pct <= 65:
        insights.append(
            f"L'allocazione è bilanciata tra obbligazionario ({bond_pct:.1f}%) "
            f"e azionario ({eq_pct:.1f}%)."
        )
    # Concentration
    hhi = metrics.get("hhi", 0)
    if hhi >= 0.15:
        insights.append(
            f"Attenzione: l'indice HHI ({hhi:.4f}) indica una concentrazione elevata. "
            "Si consiglia di valutare una maggiore diversificazione."
        )
    # Single-name risk
    max_w = metrics.get("max_weight", 0)
    if max_w > 20:
        heaviest = df.loc[df["Controvalore"].idxmax(), "Nome"] if not df["Controvalore"].isna().all() else "N/A"
        insights.append(
            f"Rischio single-name: \"{heaviest}\" pesa il {max_w:.1f}% del portafoglio."
        )
    # Top-5 concentration
    top5 = metrics.get("top5_pct", 0)
    if top5 > 70:
        insights.append(
            f"I primi 5 titoli rappresentano il {top5:.1f}% del valore totale."
        )
    # Diversification
    n_sub = metrics.get("n_subtypes", 0)
    if n_sub >= 6:
        insights.append(
            f"Buona diversificazione per sottocategoria: {n_sub} sottotipi con peso significativo."
        )
    elif n_sub <= 3:
        insights.append(
            f"Diversificazione limitata: solo {n_sub} sottocategorie con peso superiore al 2%."
        )
    return insights


# ── Plotly theme ─────────────────────────────────────────────────────────────

# Chromatic Language: palette semantica per classe asset
CHART_PALETTE = [
    "#22D3EE",  # BOND       — cerulean
    "#34D399",  # ETF        — emerald
    "#A78BFA",  # CERTIFICATE— violet
    "#FBBF24",  # COMMODITY  — amber
    "#60A5FA",  # AZIONE     — blue
    "#FB7185",  # rose
    "#F472B6",  # pink
    "#2DD4BF",  # teal
]

PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#7A8599", size=12),
    margin=dict(t=48, b=24, l=24, r=24),
    title_font=dict(size=14, color="#E8ECF1"),
    legend=dict(
        font=dict(size=11, color="#7A8599"),
        bgcolor="rgba(0,0,0,0)",
        borderwidth=0,
    ),
)


# ── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        """
        <div style="padding: 0.5rem 0 1rem; display:flex; align-items:center; gap:0.5rem;">
            <span class="mat" style="font-size:1.6rem; background: linear-gradient(135deg, #22D3EE, #34D399);
                -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                font-variation-settings:'FILL' 1,'wght' 400,'GRAD' 0,'opsz' 24;">
                monitoring
            </span>
            <span style="font-family: 'DM Sans', sans-serif; font-weight: 700; font-size: 1.1rem;
                color: #E8ECF1; letter-spacing: -0.01em;">Portfolio Analyzer</span>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        '<p style="font-size:0.82rem; color:#4A5568 !important; margin-bottom:1rem;">Carica uno o più file CSV o Excel per analizzare il portafoglio in modo unificato.</p>',
        unsafe_allow_html=True,
    )
    uploaded_files = st.file_uploader(
        "Trascina qui i file",
        type=["csv", "xlsx", "xls"],
        accept_multiple_files=True,
        help="CSV, Excel (.xlsx/.xls) — puoi caricare più file contemporaneamente",
    )
    if uploaded_files:
        for uf in uploaded_files:
            st.markdown(
                f'<p style="font-family:JetBrains Mono,monospace; font-size:0.72rem; color:#34D399 !important; margin:0.15rem 0;">'
                f'✓ {uf.name}</p>',
                unsafe_allow_html=True,
            )
    st.markdown("---")
    st.markdown(
        '<p style="font-family: JetBrains Mono, monospace; font-size:0.7rem; color:#4A5568 !important;">v2.0 · Streamlit + Plotly</p>',
        unsafe_allow_html=True,
    )

# ── Landing state ────────────────────────────────────────────────────────────

if not uploaded_files:
    st.markdown(
        """
        <div class="hero-container">
            <div class="hero-logo">
                <span class="mat" style="font-size:3rem; background: linear-gradient(135deg, #22D3EE, #34D399);
                    -webkit-background-clip:text; -webkit-text-fill-color:transparent;
                    font-variation-settings:'FILL' 1,'wght' 300,'GRAD' 0,'opsz' 48;">
                    monitoring
                </span>
            </div>
            <div class="hero-title">Portfolio Analyzer</div>
            <div class="hero-subtitle">
                Trascina uno o più file CSV o Excel nella sidebar per visualizzare
                allocazione, composizione e metriche del tuo portafoglio unificato.
            </div>
            <div class="hero-hint">
                <span class="mat arrow" style="font-size:1rem;">arrow_back</span>
                Carica uno o più file per iniziare
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.stop()

# ── Load & process (csv-data-summarizer + xlsx skill) ───────────────────────

def read_file(uploaded) -> pd.DataFrame:
    """
    Robust file reader per CSV e Excel.
    CSV: prova separatori comuni e encodings multipli.
    Excel: legge il primo foglio, mostra un selettore se ci sono più fogli.
    """
    name = uploaded.name.lower()

    if name.endswith(".csv") or name.endswith(".tsv"):
        separators = [",", ";", "\t", "|"]
        encodings = ["utf-8", "utf-8-sig", "latin-1", "cp1252"]
        known = set(HEADER_MAP.keys())
        best: tuple | None = None   # (df, score)
        last_err = None
        for enc in encodings:
            for sep in separators:
                # Try with auto-header and also skipping up to 10 rows
                for skip in [0] + list(range(1, 11)):
                    try:
                        uploaded.seek(0)
                        df = pd.read_csv(
                            uploaded, sep=sep, encoding=enc,
                            engine="python", skiprows=skip,
                        )
                        if df.shape[1] < 2:
                            continue
                        score = sum(
                            1 for c in df.columns
                            if _norm_key(c) in known
                        )
                        if best is None or score > best[1]:
                            best = (df, score)
                        if score >= 2:      # good enough — stop searching
                            return df, None
                    except Exception as e:
                        last_err = e
        if best is not None:
            return best[0], None
        return None, f"Impossibile leggere il CSV: {last_err}"

    else:  # .xlsx / .xls
        try:
            uploaded.seek(0)
            xl = pd.ExcelFile(uploaded)
            sheets = xl.sheet_names
            if len(sheets) > 1:
                sheet = st.sidebar.selectbox(
                    "Foglio Excel",
                    sheets,
                    help="Il file contiene più fogli — scegli quello da analizzare.",
                )
            else:
                sheet = sheets[0]

            # Auto-detect header row: scan first 15 rows for the one that best
            # matches our known column names from HEADER_MAP
            known = set(HEADER_MAP.keys())

            def _col_score(columns) -> int:
                score = 0
                for c in columns:
                    k = _norm_key(c)
                    if k in known:
                        score += 1
                    elif re.sub(r"[€$£]+$", "", k).strip() in known:
                        score += 1
                return score

            best_row = 0
            best_score = 0
            for skip in range(15):
                uploaded.seek(0)
                try:
                    probe = xl.parse(sheet, header=skip, nrows=3)
                    score = _col_score(probe.columns)
                    if score > best_score:
                        best_score = score
                        best_row = skip
                except Exception:
                    break

            uploaded.seek(0)
            df = xl.parse(sheet, header=best_row)
            # Drop fully-empty rows/cols that often appear above real data
            df = df.dropna(how="all").dropna(axis=1, how="all")
            return df, None
        except Exception as e:
            return None, f"Impossibile leggere l'Excel: {e}"


def data_quality_report(raw: pd.DataFrame) -> dict:
    """Genera le statistiche di qualità dati (ispirato a csv-data-summarizer)."""
    total_cells = raw.shape[0] * raw.shape[1]
    missing_cells = raw.isnull().sum().sum()
    missing_pct = (missing_cells / total_cells * 100) if total_cells else 0
    by_col = {
        col: {"count": int(raw[col].isnull().sum()),
              "pct": round(raw[col].isnull().sum() / len(raw) * 100, 1)}
        for col in raw.columns
        if raw[col].isnull().sum() > 0
    }
    return {
        "rows": raw.shape[0],
        "cols": raw.shape[1],
        "missing_cells": int(missing_cells),
        "missing_pct": round(missing_pct, 1),
        "by_col": by_col,
    }


all_raws = []
for uf in uploaded_files:
    raw_i, read_error = read_file(uf)
    if read_error:
        st.error(f"{uf.name}: {read_error}")
        st.stop()
    raw_i["_fonte"] = uf.name
    all_raws.append(raw_i)

raw = pd.concat(all_raws, ignore_index=True) if len(all_raws) > 1 else all_raws[0]

qr = data_quality_report(raw)
raw_copy = raw.copy()
df = process_portfolio(raw_copy)
# _fonte sopravvive a process_portfolio perché non viene toccata
if "_fonte" in df.columns:
    df["Fonte"] = df["_fonte"]
    df = df.drop(columns=["_fonte"])

# ── KPI row ──────────────────────────────────────────────────────────────────

total_value = df["Controvalore"].sum()
n_assets = len(df)
has_values = not df["Controvalore"].isna().all()
heaviest = df.loc[df["Controvalore"].idxmax(), "Nome"] if has_values else "N/A"
heaviest_pct = df["Peso %"].max() if has_values else 0

# Truncate long names for display
heaviest_short = (heaviest[:30] + "...") if len(heaviest) > 30 else heaviest

st.markdown(
    '<div class="section-label"><span class="mat" style="font-size:0.9rem; vertical-align:-2px;">dashboard</span>&nbsp; Panoramica</div>',
    unsafe_allow_html=True,
)
k1, k2, k3 = st.columns(3)
with k1:
    st.markdown(
        f"""<div class="glass-card kpi-card kpi-bond">
            <div class="kpi-icon kpi-icon-value" style="background:rgba(34,211,238,0.1);">
                <span class="mat" style="color:#22D3EE;font-variation-settings:'FILL' 1,'wght' 300,'GRAD' 0,'opsz' 24;">account_balance_wallet</span>
            </div>
            <div class="kpi-label" style="color:#22D3EE !important;">Controvalore Totale</div>
            <div class="kpi-value" style="color:#22D3EE !important;">€ {total_value:,.2f}</div>
        </div>""",
        unsafe_allow_html=True,
    )
with k2:
    st.markdown(
        f"""<div class="glass-card kpi-card kpi-etf">
            <div class="kpi-icon kpi-icon-count" style="background:rgba(52,211,153,0.1);">
                <span class="mat" style="color:#34D399;font-variation-settings:'FILL' 1,'wght' 300,'GRAD' 0,'opsz' 24;">dataset</span>
            </div>
            <div class="kpi-label" style="color:#34D399 !important;">Numero Titoli</div>
            <div class="kpi-value" style="color:#34D399 !important;">{n_assets}</div>
        </div>""",
        unsafe_allow_html=True,
    )
with k3:
    st.markdown(
        f"""<div class="glass-card kpi-card kpi-cert">
            <div class="kpi-icon kpi-icon-top" style="background:rgba(167,139,250,0.1);">
                <span class="mat" style="color:#A78BFA;font-variation-settings:'FILL' 1,'wght' 300,'GRAD' 0,'opsz' 24;">trophy</span>
            </div>
            <div class="kpi-label" style="color:#A78BFA !important;">Asset Più Pesante</div>
            <div class="kpi-value" style="font-size:0.95rem; line-height:1.4; color:#A78BFA !important;">{heaviest_short}</div>
            <div class="kpi-sub" style="color:#A78BFA;">{heaviest_pct:.1f}%</div>
        </div>""",
        unsafe_allow_html=True,
    )

# ── Chromatic allocation bar ─────────────────────────────────────────────────

CLASS_COLORS = {
    "BOND":        ("#22D3EE", "rgba(34,211,238,0.18)"),
    "ETF":         ("#34D399", "rgba(52,211,153,0.18)"),
    "CERTIFICATE": ("#A78BFA", "rgba(167,139,250,0.18)"),
    "COMMODITY":   ("#FBBF24", "rgba(251,191,36,0.18)"),
    "AZIONE":      ("#60A5FA", "rgba(96,165,250,0.18)"),
    "ALTRO":       ("#4A5568", "rgba(74,85,104,0.18)"),
}

if has_values:
    class_totals = df.groupby("Classe")["Controvalore"].sum()
    total_ctv = class_totals.sum()
    segments = []
    for cls, val in class_totals.items():
        pct = val / total_ctv * 100
        col_l, col_f = CLASS_COLORS.get(cls, ("#4A5568", "rgba(74,85,104,0.18)"))
        segments.append((cls, pct, col_l, col_f))
    segments.sort(key=lambda x: -x[1])

    bar_html = '<div style="display:flex; width:100%; height:6px; border-radius:3px; overflow:hidden; margin:1rem 0 0.4rem;">'
    for cls, pct, col_l, _ in segments:
        bar_html += f'<div style="width:{pct:.2f}%; background:{col_l}; opacity:0.7;"></div>'
    bar_html += '</div>'

    labels_html = '<div style="display:flex; gap:1.2rem; flex-wrap:wrap; margin-bottom:1.5rem;">'
    for cls, pct, col_l, _ in segments:
        labels_html += (
            f'<span style="display:inline-flex; align-items:center; gap:0.35rem; '
            f'font-family:JetBrains Mono,monospace; font-size:0.7rem; color:{col_l};">'
            f'<span style="display:inline-block; width:8px; height:8px; border-radius:1px; '
            f'background:{col_l};"></span>{cls}&nbsp;<span style="opacity:0.5;">{pct:.1f}%</span></span>'
        )
    labels_html += '</div>'

    st.markdown(bar_html + labels_html, unsafe_allow_html=True)

# ── Risk metrics & insights ─────────────────────────────────────────────────

risk_metrics = compute_risk_metrics(df)
portfolio_insights = generate_insights(df, risk_metrics) if risk_metrics else []

if portfolio_insights:
    insight_html = "".join(f"<li>{i}</li>" for i in portfolio_insights)
    st.markdown(
        f"""<div class="glass-card" style="padding:1rem 1.4rem; margin-bottom:1rem;">
            <div style="display:flex; align-items:center; gap:0.4rem; margin-bottom:0.6rem;">
                <span class="mat" style="font-size:1.1rem; color:#A78BFA;
                    font-variation-settings:'FILL' 1,'wght' 300,'GRAD' 0,'opsz' 24;">psychology</span>
                <span style="font-size:0.78rem; font-weight:600; letter-spacing:0.05em;
                    text-transform:uppercase; color:#A78BFA;">Insight</span>
            </div>
            <ul style="margin:0; padding-left:1.2rem; font-size:0.88rem; color:#E8ECF1;
                line-height:1.7; list-style-type:'›  ';">{insight_html}</ul>
        </div>""",
        unsafe_allow_html=True,
    )

st.markdown("<div style='height:1.8rem'></div>", unsafe_allow_html=True)

# ── Tabs ─────────────────────────────────────────────────────────────────────

tab_charts, tab_table, tab_analysis = st.tabs(["Grafici", "Tabella Dati", "Analisi"])

with tab_charts:
    c1, c2, c3 = st.columns(3)

    # Donut — asset class
    with c1:
        class_agg = df.groupby("Classe", as_index=False)["Controvalore"].sum()
        fig_class = px.pie(
            class_agg,
            names="Classe",
            values="Controvalore",
            color_discrete_sequence=CHART_PALETTE,
            hole=0.55,
        )
        fig_class.update_traces(
            textinfo="label+percent",
            textposition="auto",
            textfont=dict(size=11, family="DM Sans"),
            insidetextorientation="horizontal",
            hovertemplate="<b>%{label}</b><br>€ %{value:,.2f}<br>%{percent}<extra></extra>",
            marker=dict(line=dict(color="#0B0E11", width=2)),
        )
        fig_class.update_layout(
            **PLOTLY_LAYOUT,
            title_text="Allocazione per Classe",
            annotations=[dict(
                text="Classe",
                x=0.5, y=0.5,
                font=dict(size=13, color="#4A5568", family="DM Sans"),
                showarrow=False,
            )],
        )
        st.plotly_chart(fig_class, use_container_width=True)

    # Donut — sector
    with c2:
        sector_agg = df.groupby("Settore", as_index=False)["Controvalore"].sum()
        fig_sector = px.pie(
            sector_agg,
            names="Settore",
            values="Controvalore",
            color_discrete_sequence=CHART_PALETTE[2:] + CHART_PALETTE[:2],
            hole=0.55,
        )
        fig_sector.update_traces(
            textinfo="label+percent",
            textposition="auto",
            textfont=dict(size=11, family="DM Sans"),
            insidetextorientation="horizontal",
            hovertemplate="<b>%{label}</b><br>€ %{value:,.2f}<br>%{percent}<extra></extra>",
            marker=dict(line=dict(color="#0B0E11", width=2)),
        )
        fig_sector.update_layout(
            **PLOTLY_LAYOUT,
            title_text="Allocazione per Settore",
            annotations=[dict(
                text="Settore",
                x=0.5, y=0.5,
                font=dict(size=13, color="#4A5568", family="DM Sans"),
                showarrow=False,
            )],
        )
        st.plotly_chart(fig_sector, use_container_width=True)

    # Donut — geography
    with c3:
        geo_agg = df.groupby("Geografia", as_index=False)["Controvalore"].sum()
        fig_geo = px.pie(
            geo_agg,
            names="Geografia",
            values="Controvalore",
            color_discrete_sequence=CHART_PALETTE[4:] + CHART_PALETTE[:4],
            hole=0.55,
        )
        fig_geo.update_traces(
            textinfo="label+percent",
            textposition="auto",
            textfont=dict(size=11, family="DM Sans"),
            insidetextorientation="horizontal",
            hovertemplate="<b>%{label}</b><br>€ %{value:,.2f}<br>%{percent}<extra></extra>",
            marker=dict(line=dict(color="#0B0E11", width=2)),
        )
        fig_geo.update_layout(
            **PLOTLY_LAYOUT,
            title_text="Allocazione Geografica",
            annotations=[dict(
                text="Geo",
                x=0.5, y=0.5,
                font=dict(size=13, color="#4A5568", family="DM Sans"),
                showarrow=False,
            )],
        )
        st.plotly_chart(fig_geo, use_container_width=True)

    # ── Analisi diversificazione (financial-analyst) ────────────────────────
    df_bond = df[df["Classe"] == "BOND"].dropna(subset=["Controvalore"])
    df_equity = df[df["Classe"].isin(["ETF", "AZIONE"])].dropna(subset=["Controvalore"])
    df_other = df[~df["Classe"].isin(["BOND", "ETF", "AZIONE"])].dropna(subset=["Controvalore"])

    has_bond = len(df_bond) > 0
    has_equity = len(df_equity) > 0

    if has_bond or has_equity:
        st.markdown(
            '<div class="section-label" style="margin-top:1.5rem;">'
            '<span class="mat" style="font-size:0.9rem; vertical-align:-2px;">analytics</span>'
            '&nbsp; Analisi diversificazione</div>',
            unsafe_allow_html=True,
        )

        # ── KPI riepilogo macro-allocazione ──
        bond_total_val = df_bond["Controvalore"].sum() if has_bond else 0
        eq_total_val = df_equity["Controvalore"].sum() if has_equity else 0
        other_total_val = df_other["Controvalore"].sum() if len(df_other) > 0 else 0
        ptf_total = bond_total_val + eq_total_val + other_total_val
        bond_pct = (bond_total_val / ptf_total * 100) if ptf_total > 0 else 0
        eq_pct = (eq_total_val / ptf_total * 100) if ptf_total > 0 else 0
        other_pct = (other_total_val / ptf_total * 100) if ptf_total > 0 else 0

        alloc_cols = st.columns(3 if other_total_val > 0 else 2)
        with alloc_cols[0]:
            st.markdown(
                f"""<div class="glass-card" style="text-align:center; padding:1rem 1.2rem;">
                    <span class="mat" style="font-size:1.3rem; color:#22D3EE;
                        font-variation-settings:'FILL' 1,'wght' 300,'GRAD' 0,'opsz' 24;">savings</span>
                    <div style="font-size:0.72rem; font-weight:600; letter-spacing:0.06em;
                        text-transform:uppercase; color:#4A5568 !important; margin:0.3rem 0 0.2rem;">Obbligazionario</div>
                    <div style="font-family:'JetBrains Mono',monospace; font-size:1.8rem; font-weight:700;
                        color:#22D3EE !important;">{bond_pct:.1f}%</div>
                    <div style="font-family:'JetBrains Mono',monospace; font-size:0.8rem;
                        color:#7A8599 !important;">€ {bond_total_val:,.0f}</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with alloc_cols[1]:
            st.markdown(
                f"""<div class="glass-card" style="text-align:center; padding:1rem 1.2rem;">
                    <span class="mat" style="font-size:1.3rem; color:#34D399;
                        font-variation-settings:'FILL' 1,'wght' 300,'GRAD' 0,'opsz' 24;">trending_up</span>
                    <div style="font-size:0.72rem; font-weight:600; letter-spacing:0.06em;
                        text-transform:uppercase; color:#4A5568 !important; margin:0.3rem 0 0.2rem;">Azionario</div>
                    <div style="font-family:'JetBrains Mono',monospace; font-size:1.8rem; font-weight:700;
                        color:#34D399 !important;">{eq_pct:.1f}%</div>
                    <div style="font-family:'JetBrains Mono',monospace; font-size:0.8rem;
                        color:#7A8599 !important;">€ {eq_total_val:,.0f}</div>
                </div>""",
                unsafe_allow_html=True,
            )
        if other_total_val > 0:
            with alloc_cols[2]:
                st.markdown(
                    f"""<div class="glass-card" style="text-align:center; padding:1rem 1.2rem;">
                        <span class="mat" style="font-size:1.3rem; color:#FBBF24;
                            font-variation-settings:'FILL' 1,'wght' 300,'GRAD' 0,'opsz' 24;">category</span>
                        <div style="font-size:0.72rem; font-weight:600; letter-spacing:0.06em;
                            text-transform:uppercase; color:#4A5568 !important; margin:0.3rem 0 0.2rem;">Altro</div>
                        <div style="font-family:'JetBrains Mono',monospace; font-size:1.8rem; font-weight:700;
                            color:#FBBF24 !important;">{other_pct:.1f}%</div>
                        <div style="font-family:'JetBrains Mono',monospace; font-size:0.8rem;
                            color:#7A8599 !important;">€ {other_total_val:,.0f}</div>
                    </div>""",
                    unsafe_allow_html=True,
                )

        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)

        # ── Row 1: Sottotipo donut (per-sottocategoria) ──
        d1, d2 = st.columns(2)

        if has_bond:
            with d1:
                bond_total = df_bond["Controvalore"].sum()
                bond_sub = df_bond.groupby("Sottotipo", as_index=False)["Controvalore"].sum()
                bond_sub = bond_sub.sort_values("Controvalore", ascending=False)
                fig_bond_sub = px.pie(
                    bond_sub,
                    names="Sottotipo",
                    values="Controvalore",
                    color_discrete_sequence=CHART_PALETTE,
                    hole=0.55,
                )
                fig_bond_sub.update_traces(
                    textinfo="label+percent",
                    textposition="outside",
                    textfont=dict(size=10, family="DM Sans"),
                    insidetextorientation="horizontal",
                    hovertemplate="<b>%{label}</b><br>€ %{value:,.2f}<br>%{percent}<extra></extra>",
                    marker=dict(line=dict(color="#0B0E11", width=2)),
                )
                bond_sub_layout = {k: v for k, v in PLOTLY_LAYOUT.items() if k != "legend"}
                fig_bond_sub.update_layout(
                    **bond_sub_layout,
                    title_text=f"Obbligazionario — € {bond_total:,.0f}",
                    showlegend=True,
                    legend=dict(font=dict(size=10, color="#7A8599"), bgcolor="rgba(0,0,0,0)"),
                    annotations=[dict(
                        text="Bond", x=0.5, y=0.5,
                        font=dict(size=13, color="#4A5568", family="DM Sans"),
                        showarrow=False,
                    )],
                )
                st.plotly_chart(fig_bond_sub, use_container_width=True)

        if has_equity:
            with d2:
                eq_total = df_equity["Controvalore"].sum()
                eq_sub = df_equity.groupby("Sottotipo", as_index=False)["Controvalore"].sum()
                eq_sub = eq_sub.sort_values("Controvalore", ascending=False)
                fig_eq_sub = px.pie(
                    eq_sub,
                    names="Sottotipo",
                    values="Controvalore",
                    color_discrete_sequence=CHART_PALETTE[2:] + CHART_PALETTE[:2],
                    hole=0.55,
                )
                fig_eq_sub.update_traces(
                    textinfo="label+percent",
                    textposition="outside",
                    textfont=dict(size=10, family="DM Sans"),
                    insidetextorientation="horizontal",
                    hovertemplate="<b>%{label}</b><br>€ %{value:,.2f}<br>%{percent}<extra></extra>",
                    marker=dict(line=dict(color="#0B0E11", width=2)),
                )
                eq_sub_layout = {k: v for k, v in PLOTLY_LAYOUT.items() if k != "legend"}
                fig_eq_sub.update_layout(
                    **eq_sub_layout,
                    title_text=f"Azionario — € {eq_total:,.0f}",
                    showlegend=True,
                    legend=dict(font=dict(size=10, color="#7A8599"), bgcolor="rgba(0,0,0,0)"),
                    annotations=[dict(
                        text="Equity", x=0.5, y=0.5,
                        font=dict(size=13, color="#4A5568", family="DM Sans"),
                        showarrow=False,
                    )],
                )
                st.plotly_chart(fig_eq_sub, use_container_width=True)

        # ── Row 2: Dettaglio singoli titoli per classe ──
        st.markdown(
            '<div class="section-label" style="margin-top:1rem;">'
            '<span class="mat" style="font-size:0.9rem; vertical-align:-2px;">list_alt</span>'
            '&nbsp; Dettaglio titoli per classe</div>',
            unsafe_allow_html=True,
        )
        e1, e2 = st.columns(2)

        if has_bond:
            with e1:
                df_b = df_bond.sort_values("Controvalore", ascending=True).copy()
                fig_b_bar = px.bar(
                    df_b,
                    x="Controvalore",
                    y="Nome",
                    orientation="h",
                    color="Sottotipo",
                    color_discrete_sequence=CHART_PALETTE,
                    custom_data=["ISIN", "Peso %", "Sottotipo"],
                )
                fig_b_bar.update_traces(
                    hovertemplate=(
                        "<b>%{y}</b><br>ISIN: %{customdata[0]}<br>"
                        "€ %{x:,.2f} · %{customdata[1]:.1f}%<br>"
                        "%{customdata[2]}<extra></extra>"
                    ),
                    marker=dict(cornerradius=4),
                )
                b_layout = {k: v for k, v in PLOTLY_LAYOUT.items() if k != "legend"}
                fig_b_bar.update_layout(
                    **b_layout,
                    title_text="Titoli Obbligazionari",
                    height=max(300, len(df_b) * 32),
                    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", zeroline=False,
                               tickfont=dict(family="JetBrains Mono", size=9, color="#4A5568")),
                    yaxis=dict(gridcolor="rgba(0,0,0,0)",
                               tickfont=dict(family="DM Sans", size=10, color="#7A8599")),
                    showlegend=True,
                    legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center",
                                font=dict(size=10, color="#7A8599"), bgcolor="rgba(0,0,0,0)"),
                )
                st.plotly_chart(fig_b_bar, use_container_width=True)

        if has_equity:
            with e2:
                df_e = df_equity.sort_values("Controvalore", ascending=True).copy()
                fig_e_bar = px.bar(
                    df_e,
                    x="Controvalore",
                    y="Nome",
                    orientation="h",
                    color="Sottotipo",
                    color_discrete_sequence=CHART_PALETTE[2:] + CHART_PALETTE[:2],
                    custom_data=["ISIN", "Peso %", "Sottotipo"],
                )
                fig_e_bar.update_traces(
                    hovertemplate=(
                        "<b>%{y}</b><br>ISIN: %{customdata[0]}<br>"
                        "€ %{x:,.2f} · %{customdata[1]:.1f}%<br>"
                        "%{customdata[2]}<extra></extra>"
                    ),
                    marker=dict(cornerradius=4),
                )
                e_layout = {k: v for k, v in PLOTLY_LAYOUT.items() if k != "legend"}
                fig_e_bar.update_layout(
                    **e_layout,
                    title_text="Titoli Azionari",
                    height=max(300, len(df_e) * 32),
                    xaxis=dict(gridcolor="rgba(255,255,255,0.04)", zeroline=False,
                               tickfont=dict(family="JetBrains Mono", size=9, color="#4A5568")),
                    yaxis=dict(gridcolor="rgba(0,0,0,0)",
                               tickfont=dict(family="DM Sans", size=10, color="#7A8599")),
                    showlegend=True,
                    legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center",
                                font=dict(size=10, color="#7A8599"), bgcolor="rgba(0,0,0,0)"),
                )
                st.plotly_chart(fig_e_bar, use_container_width=True)

    # Horizontal bar — top holdings
    df_sorted = df.dropna(subset=["Controvalore"]).sort_values("Controvalore", ascending=True)

    # Color map per class for the bar chart
    class_color = {cls: CHART_PALETTE[i % len(CHART_PALETTE)] for i, cls in enumerate(df["Classe"].unique())}

    fig_bar = go.Figure()
    for cls in df_sorted["Classe"].unique():
        subset = df_sorted[df_sorted["Classe"] == cls]
        fig_bar.add_trace(go.Bar(
            x=subset["Controvalore"],
            y=subset["Nome"],
            orientation="h",
            name=cls,
            marker=dict(
                color=class_color.get(cls, CHART_PALETTE[0]),
                line=dict(width=0),
                cornerradius=4,
            ),
            customdata=list(zip(subset["ISIN"], subset["Peso %"], subset["Classe"])),
            hovertemplate=(
                "<b>%{y}</b><br>"
                "ISIN: %{customdata[0]}<br>"
                "Controvalore: € %{x:,.2f}<br>"
                "Peso: %{customdata[1]:.1f}%<br>"
                "Classe: %{customdata[2]}"
                "<extra></extra>"
            ),
        ))

    bar_height = max(400, len(df_sorted) * 36)
    bar_layout = {k: v for k, v in PLOTLY_LAYOUT.items() if k != "legend"}
    fig_bar.update_layout(
        **bar_layout,
        title_text="Holdings per Controvalore",
        height=bar_height,
        barmode="stack",
        xaxis=dict(
            gridcolor="rgba(255,255,255,0.04)",
            zeroline=False,
            tickfont=dict(family="JetBrains Mono", size=10, color="#4A5568"),
        ),
        yaxis=dict(
            gridcolor="rgba(0,0,0,0)",
            tickfont=dict(family="DM Sans", size=11, color="#7A8599"),
        ),
        showlegend=True,
        legend=dict(orientation="h", y=-0.12, x=0.5, xanchor="center",
                    font=dict(size=11, color="#7A8599"), bgcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with tab_table:
    display_cols = ["Nome", "ISIN", "Classe", "Settore", "Geografia", "Quantità", "Prezzo Acquisto", "Controvalore", "Peso %"]
    display_cols = [c for c in display_cols if c in df.columns]
    df_display = df[display_cols].copy()

    def highlight_missing(val):
        if pd.isna(val) or str(val).strip() in ("", "N/A", "n/a", "n/d"):
            return "background-color: rgba(251,191,36,0.12); color: #FBBF24;"
        return ""

    styled = df_display.style.applymap(highlight_missing).format(
        {
            "Controvalore": "€ {:,.2f}",
            "Prezzo Acquisto": "€ {:,.2f}",
            "Peso %": "{:.2f}%",
        },
        na_rep="— N/D",
    )
    st.dataframe(styled, use_container_width=True, height=480)

    st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
    col_dl1, col_dl2, _ = st.columns([1, 1, 3])
    with col_dl1:
        csv_bytes = df_display.to_csv(index=False).encode("utf-8")
        st.download_button("download  CSV", csv_bytes, "portafoglio_analizzato.csv", "text/csv")
    with col_dl2:
        excel_summary = {
            "total_value": total_value,
            "n_assets": n_assets,
            "heaviest": heaviest,
            "heaviest_pct": heaviest_pct,
            "bond_pct": risk_metrics.get("bond_pct", 0),
            "eq_pct": risk_metrics.get("eq_pct", 0),
            "other_pct": risk_metrics.get("other_pct", 0),
            **{k: v for k, v in risk_metrics.items() if k in (
                "hhi", "top5_pct", "n_subtypes", "diversification_rating"
            )},
        }
        xlsx_bytes = to_excel_styled(df_display, summary=excel_summary)
        st.download_button(
            "download  Excel",
            xlsx_bytes,
            "portafoglio_analizzato.xlsx",
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

with tab_analysis:
    if not risk_metrics:
        st.info("Dati insufficienti per l'analisi di rischio.")
    else:
        # ── Risk KPI cards ──
        st.markdown(
            '<div class="section-label"><span class="mat" style="font-size:0.9rem; vertical-align:-2px;">'
            'security</span>&nbsp; Metriche di Rischio</div>',
            unsafe_allow_html=True,
        )
        r1, r2, r3, r4 = st.columns(4)
        with r1:
            st.markdown(
                f"""<div class="glass-card kpi-card">
                    <div class="kpi-label">Indice HHI</div>
                    <div class="kpi-value" style="font-size:1.6rem;">{risk_metrics['hhi']:.4f}</div>
                    <div class="kpi-sub" style="color:{risk_metrics['diversification_color']};">
                        {risk_metrics['diversification_rating']}</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with r2:
            st.markdown(
                f"""<div class="glass-card kpi-card">
                    <div class="kpi-label">Top-5 Concentrazione</div>
                    <div class="kpi-value" style="font-size:1.6rem;">{risk_metrics['top5_pct']:.1f}%</div>
                    <div class="kpi-sub" style="color:{'#FB7185' if risk_metrics['top5_pct'] > 80 else '#FBBF24' if risk_metrics['top5_pct'] > 60 else '#34D399'};">
                        {'Alto' if risk_metrics['top5_pct'] > 80 else 'Moderato' if risk_metrics['top5_pct'] > 60 else 'Basso'}</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with r3:
            st.markdown(
                f"""<div class="glass-card kpi-card">
                    <div class="kpi-label">Rischio Single-Name</div>
                    <div class="kpi-value" style="font-size:1.6rem;">{risk_metrics['max_weight']:.1f}%</div>
                    <div class="kpi-sub" style="color:{risk_metrics['concentration_color']};">
                        {risk_metrics['concentration_rating']}</div>
                </div>""",
                unsafe_allow_html=True,
            )
        with r4:
            st.markdown(
                f"""<div class="glass-card kpi-card">
                    <div class="kpi-label">Sottocategorie Attive</div>
                    <div class="kpi-value" style="font-size:1.6rem;">{risk_metrics['n_subtypes']}</div>
                    <div class="kpi-sub" style="color:#7A8599;">peso &gt; 2%</div>
                </div>""",
                unsafe_allow_html=True,
            )

        st.markdown("<div style='height:1.5rem'></div>", unsafe_allow_html=True)

        # ── Weight distribution chart ──
        st.markdown(
            '<div class="section-label"><span class="mat" style="font-size:0.9rem; vertical-align:-2px;">'
            'bar_chart</span>&nbsp; Distribuzione Pesi per Sottocategoria</div>',
            unsafe_allow_html=True,
        )
        subtype_agg = df.groupby(["Sottotipo", "Classe"], as_index=False)["Controvalore"].sum()
        subtype_agg["Peso %"] = (subtype_agg["Controvalore"] / total_value * 100).round(2)
        subtype_agg = subtype_agg.sort_values("Peso %", ascending=True)

        class_color_map = {cls: CHART_PALETTE[i % len(CHART_PALETTE)] for i, cls in enumerate(df["Classe"].unique())}
        fig_sub = go.Figure()
        for cls in subtype_agg["Classe"].unique():
            sub = subtype_agg[subtype_agg["Classe"] == cls]
            fig_sub.add_trace(go.Bar(
                x=sub["Peso %"], y=sub["Sottotipo"], orientation="h", name=cls,
                marker=dict(color=class_color_map.get(cls, CHART_PALETTE[0]), cornerradius=4),
                hovertemplate="<b>%{y}</b><br>%{x:.1f}%<br>€ %{customdata:,.0f}<extra></extra>",
                customdata=sub["Controvalore"],
            ))
        sub_layout = {k: v for k, v in PLOTLY_LAYOUT.items() if k != "legend"}
        fig_sub.update_layout(
            **sub_layout,
            height=max(350, len(subtype_agg) * 32),
            barmode="stack",
            xaxis=dict(title="Peso %", gridcolor="rgba(255,255,255,0.04)", zeroline=False,
                       tickfont=dict(family="JetBrains Mono", size=10, color="#4A5568")),
            yaxis=dict(gridcolor="rgba(0,0,0,0)",
                       tickfont=dict(family="DM Sans", size=10, color="#7A8599")),
            showlegend=True,
            legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center",
                        font=dict(size=10, color="#7A8599"), bgcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig_sub, use_container_width=True)

        # ── Data quality: correlation & distribution (csv-data-summarizer) ──
        st.markdown(
            '<div class="section-label" style="margin-top:1.5rem;">'
            '<span class="mat" style="font-size:0.9rem; vertical-align:-2px;">query_stats</span>'
            '&nbsp; Analisi Distribuzione</div>',
            unsafe_allow_html=True,
        )
        dq1, dq2 = st.columns(2)

        with dq1:
            # Holding size distribution histogram
            df_valid = df.dropna(subset=["Controvalore"])
            fig_hist = px.histogram(
                df_valid, x="Controvalore", nbins=min(15, max(5, len(df_valid) // 2)),
                color_discrete_sequence=[CHART_PALETTE[0]],
            )
            fig_hist.update_layout(
                **PLOTLY_LAYOUT,
                title_text="Distribuzione Controvalore",
                xaxis=dict(title="Controvalore (€)", gridcolor="rgba(255,255,255,0.04)",
                           tickfont=dict(family="JetBrains Mono", size=10, color="#4A5568")),
                yaxis=dict(title="Frequenza", gridcolor="rgba(255,255,255,0.04)",
                           tickfont=dict(family="JetBrains Mono", size=10, color="#4A5568")),
                height=350,
            )
            fig_hist.update_traces(marker_line_width=0)
            st.plotly_chart(fig_hist, use_container_width=True)

        with dq2:
            # Categorical breakdown
            class_counts = df["Classe"].value_counts().reset_index()
            class_counts.columns = ["Classe", "Conteggio"]
            fig_cat = px.bar(
                class_counts, x="Classe", y="Conteggio",
                color="Classe", color_discrete_sequence=CHART_PALETTE,
            )
            fig_cat.update_layout(
                **PLOTLY_LAYOUT,
                title_text="Conteggio per Classe",
                xaxis=dict(gridcolor="rgba(0,0,0,0)",
                           tickfont=dict(family="DM Sans", size=10, color="#7A8599")),
                yaxis=dict(gridcolor="rgba(255,255,255,0.04)",
                           tickfont=dict(family="JetBrains Mono", size=10, color="#4A5568")),
                showlegend=False,
                height=350,
            )
            fig_cat.update_traces(marker=dict(cornerradius=4))
            st.plotly_chart(fig_cat, use_container_width=True)

        # ── Outlier detection ──
        if len(df_valid) > 3:
            mean_ctv = df_valid["Controvalore"].mean()
            std_ctv = df_valid["Controvalore"].std()
            outliers = df_valid[df_valid["Controvalore"] > mean_ctv + 2 * std_ctv]
            if len(outliers) > 0:
                st.markdown(
                    '<div class="section-label" style="margin-top:1rem;">'
                    '<span class="mat" style="font-size:0.9rem; vertical-align:-2px;">warning</span>'
                    '&nbsp; Posizioni Anomale (&gt;2σ dalla media)</div>',
                    unsafe_allow_html=True,
                )
                outlier_display = outliers[["Nome", "Classe", "Controvalore", "Peso %"]].copy()
                st.dataframe(
                    outlier_display.style.format({"Controvalore": "€ {:,.2f}", "Peso %": "{:.2f}%"}),
                    use_container_width=True, hide_index=True,
                )

        # ── What-If Scenario Simulator ──
        st.markdown(
            '<div class="section-label" style="margin-top:2rem;">'
            '<span class="mat" style="font-size:0.9rem; vertical-align:-2px;">science</span>'
            '&nbsp; Simulatore What-If</div>',
            unsafe_allow_html=True,
        )
        with st.expander("Apri simulatore scenari", expanded=False):
            scenario_type = st.radio(
                "Tipo di scenario",
                ["Vendita titolo", "Aggiunta importo", "Stress test"],
                horizontal=True,
            )

            if scenario_type == "Vendita titolo":
                sell_name = st.selectbox(
                    "Titolo da vendere",
                    df["Nome"].dropna().tolist(),
                    key="sell_name",
                )
                if st.button("Simula vendita", key="btn_sell"):
                    df_sim = df[df["Nome"] != sell_name].copy()
                    sim_total = df_sim["Controvalore"].sum()
                    df_sim["Peso %"] = (df_sim["Controvalore"] / sim_total * 100).round(2) if sim_total > 0 else 0
                    sim_metrics = compute_risk_metrics(df_sim)
                    sc1, sc2, sc3 = st.columns(3)
                    with sc1:
                        delta_val = sim_total - total_value
                        st.metric("Controvalore", f"€ {sim_total:,.2f}", f"€ {delta_val:,.2f}")
                    with sc2:
                        delta_hhi = sim_metrics.get("hhi", 0) - risk_metrics.get("hhi", 0)
                        st.metric("HHI", f"{sim_metrics.get('hhi', 0):.4f}", f"{delta_hhi:+.4f}")
                    with sc3:
                        st.metric("Titoli", f"{len(df_sim)}", f"{len(df_sim) - n_assets}")

            elif scenario_type == "Aggiunta importo":
                add_class = st.selectbox(
                    "Classe asset",
                    sorted(df["Classe"].unique().tolist()),
                    key="add_class",
                )
                add_amount = st.number_input(
                    "Importo da aggiungere (€)", min_value=0.0, value=10000.0, step=1000.0,
                    key="add_amount",
                )
                if st.button("Simula aggiunta", key="btn_add"):
                    new_total = total_value + add_amount
                    new_bond_pct = risk_metrics.get("bond_pct", 0)
                    new_eq_pct = risk_metrics.get("eq_pct", 0)
                    new_other_pct = risk_metrics.get("other_pct", 0)
                    add_pct = add_amount / new_total * 100
                    if add_class == "BOND":
                        new_bond_pct = (risk_metrics.get("bond_pct", 0) * total_value / 100 + add_amount) / new_total * 100
                        new_eq_pct = risk_metrics.get("eq_pct", 0) * total_value / new_total
                        new_other_pct = 100 - new_bond_pct - new_eq_pct
                    elif add_class in ("ETF", "AZIONE"):
                        new_eq_pct = (risk_metrics.get("eq_pct", 0) * total_value / 100 + add_amount) / new_total * 100
                        new_bond_pct = risk_metrics.get("bond_pct", 0) * total_value / new_total
                        new_other_pct = 100 - new_bond_pct - new_eq_pct
                    else:
                        new_other_pct = (risk_metrics.get("other_pct", 0) * total_value / 100 + add_amount) / new_total * 100
                        new_bond_pct = risk_metrics.get("bond_pct", 0) * total_value / new_total
                        new_eq_pct = 100 - new_bond_pct - new_other_pct

                    sc1, sc2 = st.columns(2)
                    with sc1:
                        st.markdown("**Prima**")
                        fig_before = px.pie(
                            names=["Bond", "Equity", "Altro"],
                            values=[risk_metrics.get("bond_pct", 0), risk_metrics.get("eq_pct", 0), risk_metrics.get("other_pct", 0)],
                            hole=0.5, color_discrete_sequence=CHART_PALETTE[:3],
                        )
                        fig_before.update_layout(**PLOTLY_LAYOUT, height=250, showlegend=True,
                                                 legend=dict(font=dict(size=10)))
                        fig_before.update_traces(textinfo="label+percent", textfont=dict(size=10))
                        st.plotly_chart(fig_before, use_container_width=True)
                    with sc2:
                        st.markdown("**Dopo**")
                        fig_after = px.pie(
                            names=["Bond", "Equity", "Altro"],
                            values=[new_bond_pct, new_eq_pct, new_other_pct],
                            hole=0.5, color_discrete_sequence=CHART_PALETTE[:3],
                        )
                        fig_after.update_layout(**PLOTLY_LAYOUT, height=250, showlegend=True,
                                                legend=dict(font=dict(size=10)))
                        fig_after.update_traces(textinfo="label+percent", textfont=dict(size=10))
                        st.plotly_chart(fig_after, use_container_width=True)

            else:  # Stress test
                stress_pct = st.slider(
                    "Variazione azionario (%)", min_value=-50, max_value=50, value=-20,
                    key="stress_pct",
                )
                if st.button("Simula stress test", key="btn_stress"):
                    eq_val = risk_metrics.get("eq_pct", 0) * total_value / 100
                    eq_delta = eq_val * stress_pct / 100
                    new_total_stress = total_value + eq_delta
                    sc1, sc2, sc3 = st.columns(3)
                    with sc1:
                        st.metric("Controvalore Attuale", f"€ {total_value:,.2f}")
                    with sc2:
                        st.metric("Impatto Azionario", f"€ {eq_delta:,.2f}",
                                  f"{stress_pct:+d}%")
                    with sc3:
                        st.metric("Controvalore Post-Stress", f"€ {new_total_stress:,.2f}",
                                  f"€ {eq_delta:,.2f}")

# ── Financial-Analyst Report ─────────────────────────────────────────────────

if risk_metrics:
    fa = generate_fa_report(df, risk_metrics)

    st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
    st.markdown(
        '<div class="section-label"><span class="mat" style="font-size:0.9rem; vertical-align:-2px;">'
        'person_search</span>&nbsp; Report Financial-Analyst</div>',
        unsafe_allow_html=True,
    )

    # ── Profilo allocazione ───────────────────────────────────────────────────
    prof_name, prof_color, prof_text = fa["alloc_profile"]
    st.markdown(
        f"""<div class="glass-card" style="padding:1.2rem 1.6rem; margin-bottom:0.8rem;
            border-left:3px solid {prof_color}; background:rgba(17,19,24,0.9);">
            <div style="display:flex; align-items:center; gap:0.6rem; margin-bottom:0.5rem;">
                <span style="font-family:'JetBrains Mono',monospace; font-size:0.68rem;
                    font-weight:700; letter-spacing:0.1em; text-transform:uppercase;
                    color:{prof_color}; background:rgba(0,0,0,0.3);
                    padding:0.15rem 0.5rem; border-radius:2px;">PROFILO · {prof_name}</span>
            </div>
            <p style="font-size:0.9rem; color:#E8ECF1; margin:0; line-height:1.7;">{prof_text}</p>
        </div>""",
        unsafe_allow_html=True,
    )

    # ── Due colonne: concentrazione + geografia ───────────────────────────────
    fa_c1, fa_c2 = st.columns(2)

    with fa_c1:
        hhi_name, hhi_color, hhi_text = fa["hhi_label"]
        st.markdown(
            f"""<div class="glass-card" style="padding:1.1rem 1.4rem; height:100%;
                border-left:3px solid {hhi_color};">
                <div style="font-size:0.68rem; font-weight:700; letter-spacing:0.1em;
                    text-transform:uppercase; color:{hhi_color}; margin-bottom:0.4rem;">
                    CONCENTRAZIONE · {hhi_name}
                </div>
                <p style="font-size:0.86rem; color:#E8ECF1; margin:0 0 0.8rem; line-height:1.6;">{hhi_text}</p>
                <div style="font-size:0.8rem; color:#7A8599; margin-bottom:0.3rem;">
                    Top-5 posizioni: <span style="color:{hhi_color}; font-family:'JetBrains Mono',monospace;">
                    {fa['top5_pct']:.1f}%</span> del portafoglio
                </div>
                <div style="font-size:0.8rem; color:#7A8599;">{fa['sub_comment']}</div>
            </div>""",
            unsafe_allow_html=True,
        )

    with fa_c2:
        st.markdown(
            f"""<div class="glass-card" style="padding:1.1rem 1.4rem; height:100%;
                border-left:3px solid #60A5FA;">
                <div style="font-size:0.68rem; font-weight:700; letter-spacing:0.1em;
                    text-transform:uppercase; color:#60A5FA; margin-bottom:0.4rem;">
                    ESPOSIZIONE GEOGRAFICA
                </div>
                <p style="font-size:0.86rem; color:#E8ECF1; margin:0 0 0.8rem; line-height:1.6;">{fa['geo_note']}</p>
                {''.join(
                    f'<div style="display:flex; justify-content:space-between; align-items:center; '
                    f'margin-bottom:0.3rem;">'
                    f'<span style="font-size:0.8rem; color:#7A8599;">{g}</span>'
                    f'<span style="font-family:JetBrains Mono,monospace; font-size:0.8rem; color:#60A5FA;">{p:.1f}%</span>'
                    f'</div>'
                    for g, p in fa['top_geo']
                )}
            </div>""",
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

    # ── Top 5 holdings table ──────────────────────────────────────────────────
    st.markdown(
        '<div style="font-size:0.68rem; font-weight:700; letter-spacing:0.1em; '
        'text-transform:uppercase; color:#4A5568; margin-bottom:0.4rem;">'
        'TOP 5 POSIZIONI PER CONTROVALORE</div>',
        unsafe_allow_html=True,
    )
    fa_top5 = fa["top5"].copy()
    fa_top5["Controvalore"] = fa_top5["Controvalore"].apply(lambda x: f"€ {x:,.2f}" if pd.notna(x) else "N/D")
    fa_top5["Peso %"] = fa_top5["Peso %"].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "N/D")
    st.dataframe(fa_top5, use_container_width=True, hide_index=True)

    st.markdown("<div style='height:0.8rem'></div>", unsafe_allow_html=True)

    # ── Raccomandazioni ───────────────────────────────────────────────────────
    st.markdown(
        '<div style="font-size:0.68rem; font-weight:700; letter-spacing:0.1em; '
        'text-transform:uppercase; color:#4A5568; margin-bottom:0.6rem;">'
        'RACCOMANDAZIONI OPERATIVE</div>',
        unsafe_allow_html=True,
    )
    for priority, rec_color, rec_text in fa["recommendations"]:
        st.markdown(
            f"""<div style="display:flex; gap:0.8rem; align-items:flex-start;
                margin-bottom:0.5rem; padding:0.7rem 1rem;
                background:rgba(17,19,24,0.8); border-radius:8px;
                border-left:2px solid {rec_color};">
                <span style="font-family:'JetBrains Mono',monospace; font-size:0.65rem;
                    font-weight:700; color:{rec_color}; white-space:nowrap;
                    padding-top:0.1rem;">{priority.upper()}</span>
                <span style="font-size:0.86rem; color:#E8ECF1; line-height:1.6;">{rec_text}</span>
            </div>""",
            unsafe_allow_html=True,
        )

# ── Data quality (in fondo alla pagina) ─────────────────────────────────────

st.markdown("<div style='height:2rem'></div>", unsafe_allow_html=True)
with st.expander(
    f"{'⚠️' if qr['missing_cells'] > 0 else '✅'}  Qualità dati — "
    f"{qr['rows']} righe · {qr['cols']} colonne · "
    f"{qr['missing_pct']}% valori mancanti",
    expanded=False,
):
    if qr["missing_cells"] == 0:
        st.markdown(
            '<p style="color:#34D399;">Nessun valore mancante — dataset completo.</p>',
            unsafe_allow_html=True,
        )
    else:
        miss_df = pd.DataFrame([
            {"Colonna": col, "Mancanti": v["count"], "%": v["pct"]}
            for col, v in qr["by_col"].items()
        ])
        st.dataframe(miss_df, use_container_width=True, hide_index=True)
    valid_ctv = df["Controvalore"].notna().sum() if "Controvalore" in df.columns else 0
    st.markdown(
        f'<p style="font-family:JetBrains Mono,monospace; font-size:0.75rem; color:#4A5568;">'
        f'File: {", ".join(uf.name for uf in uploaded_files)} &nbsp;·&nbsp; {qr["rows"]} righe lette &nbsp;·&nbsp; '
        f'{len(df)} righe processate &nbsp;·&nbsp; {valid_ctv} con controvalore</p>',
        unsafe_allow_html=True,
    )
