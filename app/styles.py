"""
app/styles.py — VíaSegura AI Design System
Applied: taste-skill (DESIGN_VARIANCE:8 MOTION:6 DENSITY:4) + redesign-skill audit
Inject in every page: from app.styles import inject_global_css; inject_global_css()
"""

import streamlit as st

GLOBAL_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@300;400;500;600;700&family=Geist+Mono:wght@400;500;600;700&display=swap');

/* ── Variables ─────────────────────────────────────────────────────────── */
:root {
  --c-bg:          #080b12;
  --c-surface:     #0d1117;
  --c-glass:       rgba(255,255,255,0.03);
  --c-glass-h:     rgba(255,255,255,0.055);
  --c-border:      rgba(255,255,255,0.07);
  --c-border-acc:  rgba(230,57,70,0.4);
  --c-accent:      #e63946;
  --c-accent-dim:  rgba(230,57,70,0.1);
  --c-text:        #edf2f7;
  --c-muted:       #68778d;
  --c-sidebar:     #050711;
  --radius:        16px;
  --radius-sm:     8px;
  --spring:        cubic-bezier(0.16, 1, 0.3, 1);
  --t:             0.25s;
}

/* Smooth scroll */
html { scroll-behavior: smooth; }

/* ── Base ──────────────────────────────────────────────────────────────── */
.stApp {
  background: var(--c-bg) !important;
  font-family: 'Geist', sans-serif !important;
  color: var(--c-text) !important;
}
.main .block-container {
  padding-top: 1.5rem !important;
  padding-bottom: 3rem !important;
  max-width: 1280px;
}

/* Grain noise overlay — breaks digital flatness (taste-skill §4) */
.stApp::before {
  content: '';
  position: fixed;
  inset: 0;
  background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='250' height='250'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.85' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  opacity: 0.022;
  pointer-events: none;
  z-index: 9999;
  mix-blend-mode: overlay;
}

/* ── Sidebar ───────────────────────────────────────────────────────────── */
[data-testid="stSidebar"] {
  background: var(--c-sidebar) !important;
  border-right: 1px solid var(--c-border) !important;
}
[data-testid="stSidebar"] > div:first-child {
  padding: 1.25rem 1rem !important;
}

/* Nav links — auto-generated */
[data-testid="stSidebarNavLink"] {
  border-radius: var(--radius-sm) !important;
  font-family: 'Geist', sans-serif !important;
  font-size: 0.875rem !important;
  font-weight: 400 !important;
  color: var(--c-muted) !important;
  margin: 2px 0 !important;
  transition: background var(--t) var(--spring),
              color var(--t) var(--spring) !important;
}
[data-testid="stSidebarNavLink"]:hover {
  background: rgba(255,255,255,0.05) !important;
  color: var(--c-text) !important;
}
[data-testid="stSidebarNavLink"][aria-current="page"] {
  background: var(--c-accent-dim) !important;
  color: var(--c-accent) !important;
  border-left: 2px solid var(--c-accent) !important;
  font-weight: 500 !important;
}

/* Nav links — manual st.page_link() */
[data-testid="stPageLink"] a {
  border-radius: var(--radius-sm) !important;
  font-family: 'Geist', sans-serif !important;
  font-size: 0.875rem !important;
  font-weight: 400 !important;
  color: var(--c-muted) !important;
  transition: background var(--t) var(--spring),
              color var(--t) var(--spring) !important;
  padding: 0.45rem 0.75rem !important;
  display: block !important;
  text-decoration: none !important;
}
[data-testid="stPageLink"] a:hover {
  background: rgba(255,255,255,0.05) !important;
  color: var(--c-text) !important;
}

/* ── Metric cards — Liquid Glass (taste-skill §4) ──────────────────────── */
[data-testid="stMetric"] {
  background: var(--c-glass) !important;
  border: 1px solid var(--c-border) !important;
  border-left: 2px solid var(--c-accent) !important;
  border-radius: var(--radius) !important;
  padding: 1.25rem 1.5rem !important;
  backdrop-filter: blur(20px) saturate(180%) !important;
  -webkit-backdrop-filter: blur(20px) saturate(180%) !important;
  /* Edge refraction — inner border highlight */
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.07),
              0 1px 4px rgba(0,0,0,0.35) !important;
  transition: transform var(--t) var(--spring),
              box-shadow var(--t) var(--spring),
              border-color var(--t) var(--spring) !important;
  animation: fadeInUp 0.5s var(--spring) both;
}

/* Staggered waterfall entry (taste-skill §4) */
.stHorizontalBlock > div:nth-child(1) [data-testid="stMetric"] { animation-delay:   0ms; }
.stHorizontalBlock > div:nth-child(2) [data-testid="stMetric"] { animation-delay:  70ms; }
.stHorizontalBlock > div:nth-child(3) [data-testid="stMetric"] { animation-delay: 140ms; }
.stHorizontalBlock > div:nth-child(4) [data-testid="stMetric"] { animation-delay: 210ms; }
.stHorizontalBlock > div:nth-child(5) [data-testid="stMetric"] { animation-delay: 280ms; }

[data-testid="stMetric"]:hover {
  transform: translateY(-2px) !important;
  border-color: var(--c-border-acc) !important;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.1),
              0 8px 24px rgba(0,0,0,0.4),
              0 0 0 1px rgba(230,57,70,0.07) !important;
}
/* Physical press (taste-skill §3 Rule 5) */
[data-testid="stMetric"]:active {
  transform: translateY(0) scale(0.99) !important;
}

[data-testid="stMetricLabel"] > div {
  font-family: 'Geist', sans-serif !important;
  font-size: 0.66rem !important;
  font-weight: 500 !important;
  letter-spacing: 0.09em !important;
  text-transform: uppercase !important;
  color: var(--c-muted) !important;
}
[data-testid="stMetricValue"] > div {
  font-family: 'Geist Mono', monospace !important;
  font-size: 1.75rem !important;
  font-weight: 600 !important;
  color: var(--c-text) !important;
  letter-spacing: -0.04em !important;
  font-variant-numeric: tabular-nums !important;
}
[data-testid="stMetricDelta"] > div {
  font-family: 'Geist', sans-serif !important;
  font-size: 0.7rem !important;
  color: var(--c-muted) !important;
}

/* ── Header bar ────────────────────────────────────────────────────────── */
header[data-testid="stHeader"] {
  background: rgba(8,11,18,0.8) !important;
  backdrop-filter: blur(20px) saturate(150%) !important;
  border-bottom: 1px solid var(--c-border) !important;
}

/* ── Tabs ──────────────────────────────────────────────────────────────── */
[data-testid="stTabs"] > div:first-child {
  border-bottom: 1px solid var(--c-border) !important;
  gap: 4px;
}
button[data-baseweb="tab"] {
  font-family: 'Geist', sans-serif !important;
  font-size: 0.875rem !important;
  font-weight: 400 !important;
  color: var(--c-muted) !important;
  border-radius: var(--radius-sm) var(--radius-sm) 0 0 !important;
  transition: color var(--t) var(--spring),
              background var(--t) var(--spring) !important;
  letter-spacing: -0.01em !important;
}
button[data-baseweb="tab"]:hover {
  color: var(--c-text) !important;
  background: rgba(255,255,255,0.04) !important;
}
button[data-baseweb="tab"][aria-selected="true"] {
  color: var(--c-accent) !important;
  border-bottom-color: var(--c-accent) !important;
  font-weight: 600 !important;
}

/* ── Divider ───────────────────────────────────────────────────────────── */
hr {
  border: none !important;
  height: 1px !important;
  background: var(--c-border) !important;
  margin: 1rem 0 !important;
}

/* ── Buttons ───────────────────────────────────────────────────────────── */
.stDownloadButton > button,
.stButton > button {
  font-family: 'Geist', sans-serif !important;
  font-weight: 500 !important;
  letter-spacing: -0.01em !important;
  border-radius: var(--radius-sm) !important;
  transition: all var(--t) var(--spring) !important;
  cursor: pointer !important;
}
.stDownloadButton > button {
  background: var(--c-accent) !important;
  border: none !important;
  color: #fff !important;
  box-shadow: 0 1px 3px rgba(0,0,0,0.35),
              inset 0 1px 0 rgba(255,255,255,0.12) !important;
}
.stDownloadButton > button:hover {
  background: #c8313d !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 14px rgba(200,49,61,0.4),
              inset 0 1px 0 rgba(255,255,255,0.12) !important;
}
.stDownloadButton > button:active {
  transform: translateY(0) scale(0.98) !important;
  box-shadow: 0 1px 3px rgba(0,0,0,0.35) !important;
}
[data-testid="stSidebar"] .stButton > button {
  background: var(--c-glass) !important;
  border: 1px solid var(--c-border) !important;
  color: var(--c-muted) !important;
  width: 100%;
  font-size: 0.82rem !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  border-color: var(--c-border-acc) !important;
  color: var(--c-text) !important;
  background: var(--c-glass-h) !important;
}

/* ── Inputs / Selects ──────────────────────────────────────────────────── */
[data-testid="stTextInput"] input,
[data-baseweb="select"] > div {
  background: rgba(255,255,255,0.04) !important;
  border: 1px solid var(--c-border) !important;
  border-radius: var(--radius-sm) !important;
  color: var(--c-text) !important;
  font-family: 'Geist', sans-serif !important;
  transition: border-color var(--t) var(--spring) !important;
}
[data-testid="stTextInput"] input:focus {
  border-color: var(--c-accent) !important;
  box-shadow: 0 0 0 3px rgba(230,57,70,0.1) !important;
  outline: none !important;
}

/* ── Multiselect tags ──────────────────────────────────────────────────── */
span[data-baseweb="tag"] {
  background: var(--c-accent-dim) !important;
  border: 1px solid rgba(230,57,70,0.3) !important;
  border-radius: 4px !important;
  color: var(--c-accent) !important;
  font-size: 0.75rem !important;
  font-family: 'Geist', sans-serif !important;
}

/* ── Radio labels ──────────────────────────────────────────────────────── */
[data-testid="stRadio"] label {
  font-family: 'Geist', sans-serif !important;
  font-size: 0.875rem !important;
  color: var(--c-muted) !important;
  transition: color var(--t) var(--spring) !important;
}
[data-testid="stRadio"] label:hover {
  color: var(--c-text) !important;
}

/* ── DataFrames ────────────────────────────────────────────────────────── */
.stDataFrame {
  border: 1px solid var(--c-border) !important;
  border-radius: var(--radius) !important;
  overflow: hidden !important;
}
.stDataFrame thead th {
  background: rgba(12,7,9,0.9) !important;
  color: var(--c-accent) !important;
  font-family: 'Geist', sans-serif !important;
  font-weight: 600 !important;
  font-size: 0.7rem !important;
  letter-spacing: 0.07em !important;
  text-transform: uppercase !important;
}
.stDataFrame tbody tr:hover td {
  background: rgba(255,255,255,0.025) !important;
}
.stDataFrame td {
  font-family: 'Geist', sans-serif !important;
  font-size: 0.875rem !important;
}
/* Monospace for numeric columns */
.stDataFrame td:has(> div > span[data-testid]),
.stDataFrame td[data-type="number"] {
  font-family: 'Geist Mono', monospace !important;
  font-variant-numeric: tabular-nums !important;
}

/* ── Alerts ────────────────────────────────────────────────────────────── */
[data-testid="stAlert"] {
  border-radius: var(--radius) !important;
  border: 1px solid var(--c-border) !important;
  font-family: 'Geist', sans-serif !important;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.05) !important;
  backdrop-filter: blur(8px) !important;
}

/* ── Captions ──────────────────────────────────────────────────────────── */
[data-testid="stCaptionContainer"], .stCaption, small {
  color: var(--c-muted) !important;
  font-size: 0.72rem !important;
  font-family: 'Geist', sans-serif !important;
}

/* ── Chat (Agente IA) ──────────────────────────────────────────────────── */
[data-testid="stChatMessage"] {
  background: var(--c-glass) !important;
  border: 1px solid var(--c-border) !important;
  border-radius: var(--radius) !important;
  font-family: 'Geist', sans-serif !important;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.05) !important;
  animation: fadeInUp 0.3s var(--spring) both;
}
[data-testid="stChatInputContainer"] {
  background: var(--c-glass) !important;
  border: 1px solid var(--c-border) !important;
  border-radius: 12px !important;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.05) !important;
  transition: border-color var(--t) var(--spring),
              box-shadow var(--t) var(--spring) !important;
}
[data-testid="stChatInputContainer"]:focus-within {
  border-color: var(--c-accent) !important;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.08),
              0 0 0 3px rgba(230,57,70,0.1) !important;
}

/* ── Animations ────────────────────────────────────────────────────────── */
@keyframes fadeInUp {
  from { opacity: 0; transform: translateY(10px); }
  to   { opacity: 1; transform: translateY(0); }
}
@keyframes pulseDot {
  0%, 100% { opacity: 1;   transform: scale(1); }
  50%       { opacity: 0.35; transform: scale(0.65); }
}

/* ── Reusable components ───────────────────────────────────────────────── */
.vs-hero {
  padding: 0.25rem 0 1.75rem;
  animation: fadeInUp 0.5s var(--spring) both;
}
.vs-brand {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 8px;
}
.vs-brand-dot {
  width: 9px;
  height: 9px;
  border-radius: 50%;
  background: var(--c-accent);
  flex-shrink: 0;
  animation: pulseDot 3s ease-in-out infinite;
}
.vs-brand-name {
  font-family: 'Geist', sans-serif;
  font-size: 2rem;
  font-weight: 700;
  color: var(--c-text);
  letter-spacing: -0.05em;
  line-height: 1;
}
.vs-brand-badge {
  font-family: 'Geist Mono', monospace;
  font-size: 0.58rem;
  font-weight: 600;
  letter-spacing: 0.1em;
  color: var(--c-accent);
  border: 1px solid rgba(230,57,70,0.45);
  border-radius: 4px;
  padding: 2px 6px;
  opacity: 0.8;
  align-self: center;
}
.vs-subtitle {
  font-family: 'Geist', sans-serif;
  font-size: 0.875rem;
  color: var(--c-muted);
  margin: 0 0 0 21px;
  font-weight: 400;
}
.vs-page-title {
  font-family: 'Geist', sans-serif;
  font-size: 1.4rem;
  font-weight: 600;
  color: var(--c-text);
  letter-spacing: -0.03em;
  margin: 0 0 16px;
  padding-bottom: 14px;
  border-bottom: 1px solid var(--c-border);
  animation: fadeInUp 0.4s var(--spring) both;
  text-wrap: balance;
}
.vs-section-label {
  font-family: 'Geist', sans-serif;
  font-size: 0.66rem;
  font-weight: 500;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  color: var(--c-muted);
  margin: 20px 0 12px;
  padding-bottom: 8px;
  border-bottom: 1px solid var(--c-border);
}
.vs-sidebar-brand {
  padding: 0 4px 16px;
  border-bottom: 1px solid var(--c-border);
  margin-bottom: 8px;
}
.vs-kv {
  font-family: 'Geist Mono', monospace;
  font-size: 0.82rem;
  color: var(--c-muted);
  margin: 4px 0;
  font-variant-numeric: tabular-nums;
}
.vs-kv b {
  color: var(--c-text);
  font-weight: 500;
}

/* ── Finding cards — hallazgos clave ──────────────────────────────────── */
.vs-finding-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin: 16px 0 28px;
}
.vs-finding-card {
  background: var(--c-glass);
  border: 1px solid var(--c-border);
  border-top: 2px solid var(--c-accent);
  border-radius: var(--radius);
  padding: 20px 22px;
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.05), 0 2px 8px rgba(0,0,0,0.3);
  transition: transform var(--t) var(--spring), border-color var(--t) var(--spring), box-shadow var(--t) var(--spring);
  animation: fadeInUp 0.5s var(--spring) both;
  cursor: default;
}
.vs-finding-card:hover {
  transform: translateY(-3px);
  border-color: var(--c-border-acc);
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.08), 0 12px 28px rgba(0,0,0,0.4), 0 0 0 1px rgba(230,57,70,0.08);
}
.vs-finding-card:nth-child(2) { animation-delay: 80ms; }
.vs-finding-card:nth-child(3) { animation-delay: 160ms; }
.vs-finding-number {
  font-family: 'Geist Mono', monospace;
  font-size: 2.6rem;
  font-weight: 700;
  color: var(--c-accent);
  letter-spacing: -0.05em;
  line-height: 1;
  font-variant-numeric: tabular-nums;
  margin-bottom: 8px;
}
.vs-finding-label {
  font-family: 'Geist', sans-serif;
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--c-text);
  line-height: 1.4;
  margin-bottom: 6px;
}
.vs-finding-sub {
  font-family: 'Geist', sans-serif;
  font-size: 0.7rem;
  color: var(--c-muted);
  line-height: 1.4;
}

/* ── Tech stack badges ──────────────────────────────────────────────────── */
.vs-stack-row {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin: 12px 0 24px;
}
.vs-stack-badge {
  font-family: 'Geist Mono', monospace;
  font-size: 0.68rem;
  font-weight: 500;
  letter-spacing: 0.04em;
  color: var(--c-muted);
  background: rgba(255,255,255,0.03);
  border: 1px solid var(--c-border);
  border-radius: 6px;
  padding: 4px 10px;
  transition: color var(--t) var(--spring), border-color var(--t) var(--spring), background var(--t) var(--spring);
  cursor: default;
}
.vs-stack-badge:hover {
  color: var(--c-text);
  border-color: rgba(255,255,255,0.15);
  background: rgba(255,255,255,0.06);
}
.vs-stack-badge.accent {
  color: var(--c-accent);
  border-color: rgba(230,57,70,0.35);
  background: var(--c-accent-dim);
}

/* ── Callout / insight box ──────────────────────────────────────────────── */
.vs-callout {
  background: rgba(230,57,70,0.06);
  border: 1px solid rgba(230,57,70,0.2);
  border-left: 3px solid var(--c-accent);
  border-radius: var(--radius-sm);
  padding: 14px 18px;
  margin: 16px 0;
  font-family: 'Geist', sans-serif;
  font-size: 0.875rem;
  color: var(--c-text);
  line-height: 1.6;
  animation: fadeInUp 0.4s var(--spring) both;
}
.vs-callout b { color: var(--c-accent); }

/* ── Limitation / warning callout ──────────────────────────────────────── */
.vs-callout-warn {
  background: rgba(251,191,36,0.05);
  border: 1px solid rgba(251,191,36,0.2);
  border-left: 3px solid #f59e0b;
  border-radius: var(--radius-sm);
  padding: 14px 18px;
  margin: 10px 0;
  font-family: 'Geist', sans-serif;
  font-size: 0.82rem;
  color: var(--c-muted);
  line-height: 1.5;
}
.vs-callout-warn b { color: #f59e0b; }

/* ── MCP server card ────────────────────────────────────────────────────── */
.vs-mcp-card {
  background: rgba(59,130,246,0.05);
  border: 1px solid rgba(59,130,246,0.2);
  border-radius: var(--radius);
  padding: 20px 24px;
  margin: 16px 0;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.04);
}
.vs-mcp-card h4 {
  font-family: 'Geist', sans-serif;
  font-size: 0.9rem;
  font-weight: 600;
  color: #60a5fa;
  margin: 0 0 8px;
  letter-spacing: -0.02em;
}
.vs-mcp-card p {
  font-family: 'Geist', sans-serif;
  font-size: 0.82rem;
  color: var(--c-muted);
  margin: 0 0 12px;
  line-height: 1.5;
}
.vs-mcp-tool {
  display: inline-block;
  font-family: 'Geist Mono', monospace;
  font-size: 0.68rem;
  color: #60a5fa;
  background: rgba(59,130,246,0.1);
  border: 1px solid rgba(59,130,246,0.2);
  border-radius: 4px;
  padding: 3px 8px;
  margin: 3px 3px 3px 0;
}

/* ── IPI dimension pill ─────────────────────────────────────────────────── */
.vs-ipi-step {
  display: flex;
  align-items: flex-start;
  gap: 14px;
  padding: 14px 0;
  border-bottom: 1px solid var(--c-border);
}
.vs-ipi-step:last-child { border-bottom: none; }
.vs-ipi-index {
  font-family: 'Geist Mono', monospace;
  font-size: 0.68rem;
  font-weight: 600;
  color: var(--c-accent);
  background: var(--c-accent-dim);
  border: 1px solid rgba(230,57,70,0.3);
  border-radius: 4px;
  padding: 3px 8px;
  flex-shrink: 0;
  margin-top: 2px;
}
.vs-ipi-title {
  font-family: 'Geist', sans-serif;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--c-text);
  margin-bottom: 4px;
}
.vs-ipi-desc {
  font-family: 'Geist', sans-serif;
  font-size: 0.78rem;
  color: var(--c-muted);
  line-height: 1.5;
}

/* ── Nav card grid ──────────────────────────────────────────────────────── */
.vs-nav-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(170px, 1fr));
  gap: 12px;
  margin: 20px 0;
}
.vs-nav-card {
  background: var(--c-glass);
  border: 1px solid var(--c-border);
  border-radius: var(--radius);
  padding: 18px 20px;
  cursor: pointer;
  transition: transform var(--t) var(--spring), border-color var(--t) var(--spring), background var(--t) var(--spring);
  text-decoration: none;
  display: block;
  animation: fadeInUp 0.5s var(--spring) both;
}
.vs-nav-card:nth-child(2) { animation-delay: 60ms; }
.vs-nav-card:nth-child(3) { animation-delay: 120ms; }
.vs-nav-card:nth-child(4) { animation-delay: 180ms; }
.vs-nav-card:hover {
  transform: translateY(-2px);
  border-color: rgba(255,255,255,0.12);
  background: var(--c-glass-h);
}
.vs-nav-icon {
  font-size: 1.4rem;
  margin-bottom: 10px;
  display: block;
}
.vs-nav-title {
  font-family: 'Geist', sans-serif;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--c-text);
  margin-bottom: 4px;
}
.vs-nav-desc {
  font-family: 'Geist', sans-serif;
  font-size: 0.72rem;
  color: var(--c-muted);
  line-height: 1.4;
}

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
  <div class="vs-brand" style="gap:8px;margin-bottom:4px">
    <div class="vs-brand-dot" style="width:8px;height:8px"></div>
    <span style="font-family:'Geist',sans-serif;font-size:1rem;font-weight:700;
                 color:#edf2f7;letter-spacing:-0.04em">VíaSegura AI</span>
  </div>
  <p style="font-family:'Geist',sans-serif;font-size:0.72rem;color:#68778d;
            margin:0 0 0 16px">Bogotá · 2016–2019</p>
</div>
<p class="vs-section-label" style="margin-top:12px">Navegación</p>
"""
