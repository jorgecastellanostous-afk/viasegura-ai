"""
app/styles.py — VíaSegura AI Design System v2
Design: Editorial Bold / Bento Grid / Archivo Black + DM Sans
"""

import streamlit as st

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Archivo:ital,wght@0,400;0,500;0,600;0,700;0,900;1,900&family=DM+Sans:wght@300;400;500&family=DM+Mono:wght@400;500&display=swap');

/* ── Variables ─────────────────────────────────────────────────────────── */
:root {
  --bg:       #080808;
  --surface:  #111111;
  --raised:   #181818;
  --border:   #222222;
  --border-h: #333333;
  --red:      #ff2233;
  --red-dim:  rgba(255,34,51,0.08);
  --red-mid:  rgba(255,34,51,0.25);
  --amber:    #f59e0b;
  --blue:     #3b82f6;
  --text:     #f5f5f5;
  --muted:    #888888;
  --faint:    #444444;
  --font-h:   'Archivo', sans-serif;
  --font-b:   'DM Sans', sans-serif;
  --font-m:   'DM Mono', monospace;
  --r:        12px;
  --r-sm:     8px;
  --t:        180ms;
  --ease-out: cubic-bezier(0, 0, 0.2, 1);   /* enter — decelerates */
  --ease-in:  cubic-bezier(0.4, 0, 1, 1);   /* exit  — accelerates */
  --ease:     cubic-bezier(0.4, 0, 0.2, 1); /* micro-interactions  */
}

html { scroll-behavior: smooth; }

/* ── App shell ─────────────────────────────────────────────────────────── */
.stApp {
  background: var(--bg) !important;
  font-family: var(--font-b) !important;
  color: var(--text) !important;
}
.main .block-container {
  padding-top: 2rem !important;
  padding-bottom: 4rem !important;
  max-width: 1300px;
}

/* ── Sidebar ───────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: #0c0c0c !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div:first-child {
  padding: 1.5rem 1rem !important;
}
[data-testid="stSidebarNavLink"] {
  border-radius: var(--r-sm) !important;
  font-family: var(--font-b) !important;
  font-size: 0.85rem !important;
  color: var(--muted) !important;
  margin: 1px 0 !important;
  transition: color var(--t) var(--ease), background var(--t) var(--ease) !important;
}
[data-testid="stSidebarNavLink"]:hover {
  background: rgba(255,255,255,0.04) !important;
  color: var(--text) !important;
}
[data-testid="stSidebarNavLink"][aria-current="page"] {
  background: var(--red-dim) !important;
  color: var(--red) !important;
  border-left: 2px solid var(--red) !important;
  font-weight: 500 !important;
}
/* ── Sidebar page links (dim, compact) ─────────────────────────────────── */
[data-testid="stSidebar"] [data-testid="stPageLink"] a {
  border-radius: var(--r-sm) !important;
  font-family: var(--font-b) !important;
  font-size: 0.85rem !important;
  color: var(--muted) !important;
  padding: 0.4rem 0.75rem !important;
  display: block !important;
  text-decoration: none !important;
  cursor: pointer !important;
  transition: color var(--t) var(--ease),
              background var(--t) var(--ease) !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a:hover {
  background: rgba(255,255,255,0.05) !important;
  color: var(--text) !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a:active {
  background: rgba(255,255,255,0.08) !important;
}
[data-testid="stSidebar"] [data-testid="stPageLink"] a:focus-visible {
  outline: 2px solid var(--red) !important;
  outline-offset: 2px !important;
}

/* ── Main-content page links — pill buttons ────────────────────────────── */
.main [data-testid="stPageLink"] a,
.block-container [data-testid="stPageLink"] a {
  display: flex !important;
  align-items: center !important;
  justify-content: center !important;
  text-align: center !important;
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 60px !important;
  padding: 13px 12px !important;
  min-height: 48px !important;      /* WCAG touch target */
  cursor: pointer !important;
  font-family: var(--font-b) !important;
  font-weight: 500 !important;
  font-size: 0.82rem !important;
  color: var(--text) !important;
  text-decoration: none !important;
  width: 100% !important;
  will-change: transform, border-color !important;
  transition: border-color var(--t) var(--ease-out),
              background  var(--t) var(--ease-out),
              transform   150ms   var(--ease-out),
              box-shadow  var(--t) var(--ease-out) !important;
}
.main [data-testid="stPageLink"] a:hover,
.block-container [data-testid="stPageLink"] a:hover {
  border-color: var(--border-h) !important;
  background: var(--raised) !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 4px 16px rgba(0,0,0,0.4) !important;
}
.main [data-testid="stPageLink"] a:active,
.block-container [data-testid="stPageLink"] a:active {
  transform: scale(0.97) translateY(0) !important;
  box-shadow: none !important;
  background: #1c1c1c !important;
}
.main [data-testid="stPageLink"] a:focus-visible,
.block-container [data-testid="stPageLink"] a:focus-visible {
  outline: 2px solid var(--red) !important;
  outline-offset: 3px !important;
  border-color: var(--red) !important;
}

/* ── Header ────────────────────────────────────────────────────────────── */
header[data-testid="stHeader"] {
  background: rgba(8,8,8,0.9) !important;
  border-bottom: 1px solid var(--border) !important;
  backdrop-filter: blur(12px) !important;
}

/* ── st.metric override ─────────────────────────────────────────────────── */
[data-testid="stMetric"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
  padding: 1.25rem !important;
}
[data-testid="stMetricLabel"] > div {
  font-family: var(--font-b) !important;
  font-size: 0.65rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.1em !important;
  text-transform: uppercase !important;
  color: var(--muted) !important;
}
[data-testid="stMetricValue"] > div {
  font-family: var(--font-m) !important;
  font-size: 1.6rem !important;
  font-weight: 500 !important;
  color: var(--text) !important;
  letter-spacing: -0.04em !important;
}
[data-testid="stMetricDelta"] > div { color: var(--muted) !important; font-size: 0.7rem !important; }

/* ── Tabs ──────────────────────────────────────────────────────────────── */
[data-testid="stTabs"] > div:first-child {
  border-bottom: 1px solid var(--border) !important;
  gap: 0 !important;
}
button[data-baseweb="tab"] {
  font-family: var(--font-b) !important;
  font-size: 0.85rem !important;
  font-weight: 400 !important;
  color: var(--muted) !important;
  padding: 10px 16px !important;
  transition: color var(--t) var(--ease) !important;
}
button[data-baseweb="tab"]:hover { color: var(--text) !important; }
button[data-baseweb="tab"][aria-selected="true"] {
  color: var(--text) !important;
  border-bottom: 2px solid var(--red) !important;
  font-weight: 600 !important;
}

/* ── DataFrames ────────────────────────────────────────────────────────── */
.stDataFrame {
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
  overflow: hidden !important;
}
.stDataFrame thead th {
  background: var(--raised) !important;
  color: var(--red) !important;
  font-family: var(--font-b) !important;
  font-size: 0.65rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.08em !important;
  text-transform: uppercase !important;
}
.stDataFrame td {
  font-family: var(--font-b) !important;
  font-size: 0.85rem !important;
  color: var(--text) !important;
}
.stDataFrame tbody tr:hover td { background: rgba(255,255,255,0.02) !important; }

/* ── Inputs ────────────────────────────────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-baseweb="select"] > div {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r-sm) !important;
  color: var(--text) !important;
  font-family: var(--font-b) !important;
}
[data-testid="stTextInput"] input:focus {
  border-color: var(--red) !important;
  box-shadow: 0 0 0 2px var(--red-dim) !important;
  outline: none !important;
}
span[data-baseweb="tag"] {
  background: var(--red-dim) !important;
  border: 1px solid var(--red-mid) !important;
  color: var(--red) !important;
  font-size: 0.72rem !important;
}

/* ── Buttons ───────────────────────────────────────────────────────────── */
.stDownloadButton > button,
.stButton > button {
  font-family: var(--font-b) !important;
  font-weight: 500 !important;
  border-radius: var(--r-sm) !important;
  transition: all var(--t) var(--ease) !important;
  cursor: pointer !important;
}
.stDownloadButton > button {
  background: var(--red) !important;
  border: none !important;
  color: #fff !important;
  min-height: 44px !important;
}
.stDownloadButton > button:hover {
  filter: brightness(1.12) !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 4px 16px rgba(255,34,51,0.35) !important;
}
.stDownloadButton > button:active {
  transform: scale(0.97) translateY(0) !important;
  filter: brightness(0.95) !important;
}
.stDownloadButton > button:focus-visible,
.stButton > button:focus-visible {
  outline: 2px solid var(--red) !important;
  outline-offset: 3px !important;
}
/* Tab focus */
button[data-baseweb="tab"]:focus-visible {
  outline: 2px solid var(--red) !important;
  outline-offset: -2px !important;
  border-radius: 4px !important;
}
button[data-baseweb="tab"] { cursor: pointer !important; }

/* ── Chat ──────────────────────────────────────────────────────────────── */
[data-testid="stChatMessage"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: var(--r) !important;
  font-family: var(--font-b) !important;
}
[data-testid="stChatInputContainer"] {
  background: var(--surface) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  transition: border-color var(--t) var(--ease) !important;
}
[data-testid="stChatInputContainer"]:focus-within {
  border-color: var(--red) !important;
  box-shadow: 0 0 0 2px var(--red-dim) !important;
}

/* ── Alerts ────────────────────────────────────────────────────────────── */
[data-testid="stAlert"] {
  border-radius: var(--r) !important;
  border: 1px solid var(--border) !important;
  font-family: var(--font-b) !important;
}
[data-testid="stCaptionContainer"], .stCaption, small {
  color: var(--muted) !important;
  font-family: var(--font-b) !important;
  font-size: 0.72rem !important;
}
hr {
  border: none !important;
  height: 1px !important;
  background: var(--border) !important;
  margin: 2rem 0 !important;
}

/* ── Animations ────────────────────────────────────────────────────────── */
@keyframes fadeUp {
  from { opacity: 0; transform: translateY(14px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes blink {
  0%, 100% { opacity: 1; }
  50%       { opacity: 0.25; }
}

/* Global focus ring — keyboard nav */
:focus-visible {
  outline: 2px solid var(--red) !important;
  outline-offset: 3px !important;
}

/* ════════════════════════════════════════════════════════
   COMPONENTS
   ════════════════════════════════════════════════════════ */

/* ── Sidebar brand ─────────────────────────────────────────────────────── */
.vs-sidebar-brand {
  padding: 0 4px 20px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 12px;
}
.vs-logo-text {
  font-family: var(--font-h);
  font-weight: 900;
  font-size: 1.05rem;
  color: var(--text);
  letter-spacing: -0.03em;
  display: flex;
  align-items: center;
  gap: 8px;
}
.vs-logo-dot {
  width: 8px;
  height: 8px;
  background: var(--red);
  border-radius: 50%;
  flex-shrink: 0;
  animation: blink 4s ease-in-out infinite;
}
.vs-logo-sub {
  font-family: var(--font-b);
  font-size: 0.7rem;
  color: var(--muted);
  margin-top: 4px;
  padding-left: 16px;
}

/* ── Hero ──────────────────────────────────────────────────────────────── */
.vs-hero {
  padding: 1rem 0 2.5rem;
  animation: fadeUp 0.45s var(--ease-out) both;
}
.vs-hero-eyebrow {
  font-family: var(--font-m);
  font-size: 0.7rem;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--red);
  margin-bottom: 14px;
  display: flex;
  align-items: center;
  gap: 8px;
}
.vs-hero-eyebrow::before {
  content: '';
  display: block;
  width: 24px;
  height: 2px;
  background: var(--red);
  flex-shrink: 0;
}
.vs-hero-title {
  font-family: var(--font-h);
  font-weight: 900;
  font-size: clamp(2.4rem, 5vw, 3.8rem);
  line-height: 1;
  letter-spacing: -0.04em;
  color: var(--text);
  margin-bottom: 18px;
  text-wrap: balance;
}
.vs-hero-title em {
  font-style: normal;
  color: var(--red);
}
.vs-hero-sub {
  font-family: var(--font-b);
  font-size: 1rem;
  color: var(--muted);
  max-width: 560px;
  line-height: 1.6;
}

/* ── Section label ─────────────────────────────────────────────────────── */
.vs-label {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-family: var(--font-m);
  font-size: 0.62rem;
  font-weight: 500;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--red);
  background: var(--red-dim);
  border: 1px solid var(--red-mid);
  border-radius: 4px;
  padding: 3px 8px;
  margin-bottom: 16px;
}

/* ── KPI strip ─────────────────────────────────────────────────────────── */
.vs-kpi-strip {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  border: 1px solid var(--border);
  border-radius: var(--r);
  overflow: hidden;
  margin: 8px 0 36px;
  animation: fadeUp 0.4s var(--ease-out) 0.08s both;
}
.vs-kpi {
  padding: 22px 24px;
  border-right: 1px solid var(--border);
  cursor: default;
  transition: background var(--t) var(--ease-out);
}
.vs-kpi:last-child { border-right: none; }
.vs-kpi:hover { background: rgba(255,255,255,0.018); }
.vs-kpi-value {
  font-family: var(--font-h);
  font-weight: 900;
  font-size: 2rem;
  letter-spacing: -0.05em;
  color: var(--text);
  line-height: 1;
  margin-bottom: 6px;
}
.vs-kpi-label {
  font-family: var(--font-b);
  font-size: 0.72rem;
  color: var(--muted);
  line-height: 1.3;
}

/* ── Bento grid de hallazgos ───────────────────────────────────────────── */
.vs-bento {
  display: grid;
  grid-template-columns: 1.6fr 1fr 1fr;
  grid-template-rows: 1fr 1fr;
  gap: 3px;
  margin: 8px 0 40px;
  border-radius: var(--r);
  overflow: hidden;
  animation: fadeUp 0.4s var(--ease-out) 0.12s both;
}
/* Stagger bento children */
.vs-bento > div:nth-child(1) { animation: fadeUp 0.4s var(--ease-out) 0.10s both; }
.vs-bento > div:nth-child(2) { animation: fadeUp 0.4s var(--ease-out) 0.18s both; }
.vs-bento > div:nth-child(3) { animation: fadeUp 0.4s var(--ease-out) 0.26s both; }

.vs-bento-main {
  grid-column: 1;
  grid-row: 1 / 3;
  background: var(--surface);
  padding: 36px 36px 32px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  min-height: 280px;
  cursor: default;
  transition: background var(--t) var(--ease-out);
  position: relative;
  overflow: hidden;
  will-change: background;
}
.vs-bento-main::before {
  content: '';
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 3px;
  background: var(--red);
}
.vs-bento-main:hover { background: var(--raised); }
.vs-bento-sm {
  background: var(--surface);
  padding: 28px 28px 24px;
  display: flex;
  flex-direction: column;
  justify-content: flex-end;
  cursor: default;
  transition: background var(--t) var(--ease-out);
  position: relative;
  overflow: hidden;
  will-change: background;
}
.vs-bento-sm::before {
  content: '';
  position: absolute;
  top: 0; left: 0;
  width: 100%; height: 3px;
  background: var(--border-h);
  transition: background var(--t) var(--ease-out);
}
.vs-bento-sm:hover { background: var(--raised); }
.vs-bento-sm:hover::before { background: var(--red); }

.vs-num-xl {
  font-family: var(--font-h);
  font-weight: 900;
  font-size: clamp(3.5rem, 8vw, 6rem);
  letter-spacing: -0.06em;
  color: var(--red);
  line-height: 1;
  margin-bottom: 14px;
}
.vs-num-sm {
  font-family: var(--font-h);
  font-weight: 900;
  font-size: clamp(2.2rem, 4vw, 3.2rem);
  letter-spacing: -0.05em;
  color: var(--text);
  line-height: 1;
  margin-bottom: 10px;
}
.vs-num-sm-red { color: var(--red); }
.vs-bento-label {
  font-family: var(--font-b);
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--text);
  line-height: 1.35;
  margin-bottom: 6px;
}
.vs-bento-sub {
  font-family: var(--font-b);
  font-size: 0.75rem;
  color: var(--muted);
  line-height: 1.4;
}

/* ── IPI dimension row ─────────────────────────────────────────────────── */
.vs-dim-grid {
  display: grid;
  grid-template-columns: repeat(5, 1fr);
  gap: 3px;
  margin: 8px 0 24px;
  border-radius: var(--r);
  overflow: hidden;
}
.vs-dim-card {
  background: var(--surface);
  padding: 20px 18px;
  border-top: 2px solid var(--border);
  transition: border-color var(--t) var(--ease-out),
              background   var(--t) var(--ease-out);
  cursor: default;
  will-change: border-color, background;
}
.vs-dim-card:hover {
  background: var(--raised);
  border-top-color: var(--red);
}
.vs-dim-num {
  font-family: var(--font-m);
  font-size: 0.7rem;
  color: var(--faint);
  margin-bottom: 8px;
}
.vs-dim-title {
  font-family: var(--font-h);
  font-weight: 700;
  font-size: 0.85rem;
  color: var(--text);
  margin-bottom: 4px;
}
.vs-dim-weight {
  font-family: var(--font-m);
  font-size: 1.1rem;
  font-weight: 500;
  color: var(--red);
  margin-bottom: 8px;
}
.vs-dim-desc {
  font-family: var(--font-b);
  font-size: 0.72rem;
  color: var(--muted);
  line-height: 1.4;
}

/* ── Callouts ──────────────────────────────────────────────────────────── */
.vs-callout {
  border-left: 3px solid var(--red);
  background: var(--red-dim);
  padding: 14px 18px;
  border-radius: 0 var(--r-sm) var(--r-sm) 0;
  margin: 16px 0;
  font-family: var(--font-b);
  font-size: 0.875rem;
  color: var(--text);
  line-height: 1.6;
}
.vs-callout b { color: var(--red); }
.vs-callout-warn {
  border-left: 3px solid var(--amber);
  background: rgba(245,158,11,0.06);
  padding: 14px 18px;
  border-radius: 0 var(--r-sm) var(--r-sm) 0;
  margin: 10px 0;
  font-family: var(--font-b);
  font-size: 0.82rem;
  color: var(--muted);
  line-height: 1.5;
}
.vs-callout-warn b { color: var(--amber); }

/* ── MCP card ──────────────────────────────────────────────────────────── */
.vs-mcp-card {
  background: var(--surface);
  border: 1px solid var(--border);
  border-top: 2px solid var(--blue);
  border-radius: var(--r);
  padding: 24px 28px;
  margin: 8px 0;
}
.vs-mcp-card h4 {
  font-family: var(--font-h);
  font-weight: 700;
  font-size: 1rem;
  color: #60a5fa;
  margin: 0 0 8px;
  letter-spacing: -0.02em;
}
.vs-mcp-card p {
  font-family: var(--font-b);
  font-size: 0.82rem;
  color: var(--muted);
  margin: 0 0 14px;
  line-height: 1.5;
}
.vs-mcp-tool {
  display: inline-block;
  font-family: var(--font-m);
  font-size: 0.65rem;
  color: #60a5fa;
  background: rgba(59,130,246,0.08);
  border: 1px solid rgba(59,130,246,0.2);
  border-radius: 4px;
  padding: 3px 9px;
  margin: 3px 3px 3px 0;
}

/* ── Stack badges ──────────────────────────────────────────────────────── */
.vs-stack-row {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 8px 0 20px;
}
.vs-stack-badge {
  font-family: var(--font-m);
  font-size: 0.65rem;
  color: var(--muted);
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 20px;
  padding: 4px 12px;
  cursor: default;
  transition: color var(--t) var(--ease), border-color var(--t) var(--ease);
}
.vs-stack-badge:hover { color: var(--text); border-color: var(--border-h); }
.vs-stack-badge.red {
  color: var(--red);
  border-color: var(--red-mid);
  background: var(--red-dim);
}

/* ── Nav links — main content (pill buttons via st.page_link) ──────────── */
.vs-nav-links {
  margin: 8px 0 32px;
  animation: fadeUp 0.4s var(--ease-out) 0.22s both;
}
/* Stagger each column's page link */
.vs-nav-links .stHorizontalBlock > div:nth-child(1) [data-testid="stPageLink"] a { animation-delay: 0ms; }
.vs-nav-links .stHorizontalBlock > div:nth-child(2) [data-testid="stPageLink"] a { animation-delay: 50ms; }
.vs-nav-links .stHorizontalBlock > div:nth-child(3) [data-testid="stPageLink"] a { animation-delay: 100ms; }
.vs-nav-links .stHorizontalBlock > div:nth-child(4) [data-testid="stPageLink"] a { animation-delay: 150ms; }
.vs-nav-links .stHorizontalBlock > div:nth-child(5) [data-testid="stPageLink"] a { animation-delay: 200ms; }
.vs-nav-links [data-testid="stPageLink"] a {
  animation: fadeUp 0.35s var(--ease-out) both;
}

/* ── IPI step (metodología) ────────────────────────────────────────────── */
.vs-ipi-step {
  display: flex;
  align-items: flex-start;
  gap: 16px;
  padding: 16px 0;
  border-bottom: 1px solid var(--border);
}
.vs-ipi-step:last-child { border-bottom: none; }
.vs-ipi-idx {
  font-family: var(--font-m);
  font-size: 0.65rem;
  color: var(--red);
  background: var(--red-dim);
  border: 1px solid var(--red-mid);
  border-radius: 4px;
  padding: 3px 8px;
  flex-shrink: 0;
  margin-top: 2px;
}
.vs-ipi-title {
  font-family: var(--font-h);
  font-weight: 700;
  font-size: 0.875rem;
  color: var(--text);
  margin-bottom: 4px;
}
.vs-ipi-desc {
  font-family: var(--font-b);
  font-size: 0.78rem;
  color: var(--muted);
  line-height: 1.5;
}

/* ── kv row (sidebar stats) ────────────────────────────────────────────── */
.vs-kv {
  font-family: var(--font-m);
  font-size: 0.78rem;
  color: var(--muted);
  margin: 5px 0;
}
.vs-kv b { color: var(--text); font-weight: 500; }

/* ── Reduced motion ────────────────────────────────────────────────────── */
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
</style>
"""


def inject_global_css() -> None:
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)


SIDEBAR_BRAND = """
<div class="vs-sidebar-brand">
  <div class="vs-logo-text">
    <div class="vs-logo-dot"></div>
    VíaSegura AI
  </div>
  <div class="vs-logo-sub">Bogotá · SIMUR · 2016–2019</div>
</div>
"""
