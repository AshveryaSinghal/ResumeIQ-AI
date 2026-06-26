
"""
app.py — ResumeIQ AI: AI Career Copilot
Production-grade UI with improved dashboard, comparison UX, empty states,
loading animations, mobile responsiveness, and robust error handling.
"""

from dotenv import load_dotenv
load_dotenv()

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import time
from datetime import datetime

from modules import (
    jd_extractor, resume_parser, matcher, ats, llm,
    storage, auth, company_profiles, roadmap, report,
)

storage.init_db()

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ResumeIQ — AI Career Copilot",
    page_icon="",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Design tokens ── */
:root {
    --bg-page:        #ffffff;
    --bg-card:        #f8fafc;
    --bg-card-hover:  #f1f5f9;
    --bg-sidebar:     #f8fafc;
    --border:         #e2e8f0;
    --text-primary:   #0f172a;
    --text-secondary: #475569;
    --text-muted:     #94a3b8;
    --accent:         #3b5bdb;
    --accent-hover:   #2f4ac0;
    --accent-soft:    #eef2ff;
    --success:        #059669;
    --success-soft:   #ecfdf5;
    --warning:        #d97706;
    --warning-soft:   #fffbeb;
    --danger:         #dc2626;
    --danger-soft:    #fef2f2;
    --tag-matched-bg: #d1fae5;
    --tag-matched-fg: #065f46;
    --tag-matched-bd: #6ee7b7;
    --tag-missing-bg: #fee2e2;
    --tag-missing-fg: #991b1b;
    --tag-missing-bd: #fca5a5;
    --tag-extra-bg:   #eff6ff;
    --tag-extra-fg:   #1e40af;
    --tag-extra-bd:   #93c5fd;
    --shadow-sm:      0 1px 3px rgba(0,0,0,0.08);
    --shadow-md:      0 4px 12px rgba(0,0,0,0.10);
    --radius-sm:      6px;
    --radius-md:      10px;
    --radius-lg:      14px;
}

/* Dark mode override */
@media (prefers-color-scheme: dark) {
    :root {
        --bg-page:        #0d1117;
        --bg-card:        #161b22;
        --bg-card-hover:  #1c2332;
        --bg-sidebar:     #0d1117;
        --border:         #30363d;
        --text-primary:   #e6edf3;
        --text-secondary: #8b949e;
        --text-muted:     #6e7681;
        --accent:         #58a6ff;
        --accent-hover:   #79b8ff;
        --accent-soft:    #1a2744;
        --success:        #3fb950;
        --success-soft:   #0d2615;
        --warning:        #d29922;
        --warning-soft:   #2d1f05;
        --danger:         #f85149;
        --danger-soft:    #2d0f0f;
        --tag-matched-bg: #0d2615;
        --tag-matched-fg: #3fb950;
        --tag-matched-bd: #1f6331;
        --tag-missing-bg: #2d0f0f;
        --tag-missing-fg: #f85149;
        --tag-missing-bd: #6e1a1a;
        --tag-extra-bg:   #0d1f3c;
        --tag-extra-fg:   #79b8ff;
        --tag-extra-bd:   #1a3a6e;
        --shadow-sm:      0 1px 3px rgba(0,0,0,0.3);
        --shadow-md:      0 4px 12px rgba(0,0,0,0.4);
    }
}

[data-theme="dark"] {
    --bg-page:        #0d1117;
    --bg-card:        #161b22;
    --bg-card-hover:  #1c2332;
    --bg-sidebar:     #0d1117;
    --border:         #30363d;
    --text-primary:   #e6edf3;
    --text-secondary: #8b949e;
    --text-muted:     #6e7681;
    --accent:         #58a6ff;
    --accent-hover:   #79b8ff;
    --accent-soft:    #1a2744;
    --success:        #3fb950;
    --success-soft:   #0d2615;
    --warning:        #d29922;
    --warning-soft:   #2d1f05;
    --danger:         #f85149;
    --danger-soft:    #2d0f0f;
    --tag-matched-bg: #0d2615;
    --tag-matched-fg: #3fb950;
    --tag-matched-bd: #1f6331;
    --tag-missing-bg: #2d0f0f;
    --tag-missing-fg: #f85149;
    --tag-missing-bd: #6e1a1a;
    --tag-extra-bg:   #0d1f3c;
    --tag-extra-fg:   #79b8ff;
    --tag-extra-bd:   #1a3a6e;
    --shadow-sm:      0 1px 3px rgba(0,0,0,0.3);
    --shadow-md:      0 4px 12px rgba(0,0,0,0.4);
}

/* ── Base ── */
html, body, [class*="css"], [data-testid="stAppViewContainer"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
}

#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1280px;
}

.stMarkdown, .stMarkdown p, .stMarkdown li, .stText, p, li, span {
    color: inherit;
}

/* ── App header ── */
.riq-header {
    padding-bottom: 1.25rem;
    margin-bottom: 1rem;
    border-bottom: 1px solid var(--border);
}
.riq-title {
    font-size: 1.75rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: var(--text-primary);
    margin: 0;
    line-height: 1;
}
.riq-subtitle {
    font-size: 0.875rem;
    color: var(--text-secondary);
    margin-top: 0.35rem;
}

/* ── KPI Grid ── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 0.75rem;
    margin-bottom: 1.25rem;
}
@media (max-width: 768px) {
    .kpi-grid { grid-template-columns: repeat(2, 1fr); }
}
.kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1rem 1.1rem;
    box-shadow: var(--shadow-sm);
    transition: box-shadow 0.2s, transform 0.2s;
}
.kpi-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
}
.kpi-label {
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    margin-bottom: 0.3rem;
}
.kpi-value {
    font-size: 1.7rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    color: var(--text-primary);
    line-height: 1.2;
}
.kpi-value.good { color: var(--success); }
.kpi-value.mid { color: var(--warning); }
.kpi-value.low { color: var(--danger); }
.kpi-sub {
    font-size: 0.7rem;
    color: var(--text-muted);
    margin-top: 0.2rem;
}

/* ── Score cards ── */
.score-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 0.75rem;
    margin-bottom: 1.25rem;
}
@media (max-width: 768px) {
    .score-grid { grid-template-columns: repeat(2, 1fr); }
}
.score-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1.1rem 1rem;
    text-align: center;
    box-shadow: var(--shadow-sm);
    transition: box-shadow 0.2s, transform 0.2s;
}
.score-card:hover {
    box-shadow: var(--shadow-md);
    transform: translateY(-1px);
}
.score-card .sc-label {
    font-size: 0.68rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--text-muted);
    margin-bottom: 0.5rem;
}
.score-card .sc-value {
    font-size: 1.9rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
    line-height: 1;
}
.sc-value.good { color: var(--success); }
.sc-value.mid  { color: var(--warning); }
.sc-value.low  { color: var(--danger); }

/* ── Progress bars ── */
.progress-wrap {
    margin-bottom: 0.75rem;
}
.progress-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.2rem;
}
.progress-label {
    font-size: 0.8rem;
    font-weight: 500;
    color: var(--text-primary);
}
.progress-value {
    font-size: 0.8rem;
    font-weight: 600;
    font-family: 'JetBrains Mono', monospace;
}
.progress-track {
    background: var(--border);
    border-radius: 999px;
    height: 8px;
    overflow: hidden;
}
.progress-fill {
    height: 100%;
    border-radius: 999px;
    transition: width 0.6s ease;
}
.progress-fill.good { background: var(--success); }
.progress-fill.mid { background: var(--warning); }
.progress-fill.low { background: var(--danger); }

/* ── Section headings ── */
.section-heading {
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    margin: 1.5rem 0 0.75rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid var(--border);
}

/* ── Banners ── */
.banner {
    padding: 0.75rem 1rem;
    border-radius: var(--radius-sm);
    font-size: 0.875rem;
    font-weight: 500;
    margin-bottom: 0.5rem;
    border-left: 3px solid;
}
.banner.success {
    background: var(--success-soft);
    color: var(--success);
    border-color: var(--success);
}
.banner.danger {
    background: var(--danger-soft);
    color: var(--danger);
    border-color: var(--danger);
}
.banner.warning {
    background: var(--warning-soft);
    color: var(--warning);
    border-color: var(--warning);
}
.banner.info {
    background: var(--accent-soft);
    color: var(--accent);
    border-color: var(--accent);
}

/* ── Empty state ── */
.empty-state {
    text-align: center;
    padding: 3rem 2rem;
    background: var(--bg-card);
    border: 1px dashed var(--border);
    border-radius: var(--radius-lg);
    margin: 1.5rem 0;
}
.empty-state-icon {
    font-size: 2.5rem;
    margin-bottom: 0.75rem;
}
.empty-state-title {
    font-size: 1rem;
    font-weight: 600;
    color: var(--text-primary);
    margin-bottom: 0.4rem;
}
.empty-state-desc {
    font-size: 0.85rem;
    color: var(--text-secondary);
    max-width: 400px;
    margin: 0 auto;
    line-height: 1.6;
}

/* ── Skill tags ── */
.skill-tag {
    display: inline-block;
    padding: 0.22rem 0.65rem;
    border-radius: 4px;
    font-size: 0.76rem;
    font-weight: 500;
    margin: 0.2rem 0.15rem;
    font-family: 'JetBrains Mono', monospace;
    letter-spacing: 0.01em;
}
.skill-tag.matched {
    background: var(--tag-matched-bg);
    color: var(--tag-matched-fg);
    border: 1px solid var(--tag-matched-bd);
}
.skill-tag.missing {
    background: var(--tag-missing-bg);
    color: var(--tag-missing-fg);
    border: 1px solid var(--tag-missing-bd);
}
.skill-tag.extra {
    background: var(--tag-extra-bg);
    color: var(--tag-extra-fg);
    border: 1px solid var(--tag-extra-bd);
}

/* ── Roadmap cards ── */
.week-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1rem 1.25rem;
    margin-bottom: 0.65rem;
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    box-shadow: var(--shadow-sm);
}
.week-badge {
    background: var(--accent);
    color: #fff;
    font-size: 0.7rem;
    font-weight: 700;
    padding: 0.3rem 0.65rem;
    border-radius: 4px;
    white-space: nowrap;
    font-family: 'JetBrains Mono', monospace;
    flex-shrink: 0;
    margin-top: 2px;
}
.week-priority {
    font-size: 0.66rem;
    font-weight: 600;
    letter-spacing: 0.05em;
    padding: 0.15rem 0.45rem;
    border-radius: 3px;
    flex-shrink: 0;
    margin-top: 2px;
}
.week-priority.High   { background: var(--danger-soft); color: var(--danger); }
.week-priority.Medium { background: var(--warning-soft); color: var(--warning); }
.week-priority.Low    { background: var(--accent-soft); color: var(--accent); }
.week-content { flex: 1; min-width: 0; }
.week-skills {
    font-weight: 600;
    font-size: 0.875rem;
    color: var(--text-primary);
    margin-bottom: 0.25rem;
}
.week-focus {
    font-size: 0.8rem;
    color: var(--text-secondary);
}
.week-resource {
    font-size: 0.75rem;
    color: var(--text-muted);
    margin-top: 0.25rem;
    font-style: italic;
}

/* ── Company fit ── */
.fit-section {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1.25rem;
    margin-bottom: 1rem;
}
.fit-company-name {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-primary);
    margin-bottom: 0.25rem;
}
.fit-focus {
    font-size: 0.8rem;
    color: var(--text-secondary);
    margin-bottom: 0.75rem;
}
.fit-score-row {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-bottom: 0.5rem;
}
.fit-score-number {
    font-size: 2rem;
    font-weight: 700;
    font-family: 'JetBrains Mono', monospace;
}
.fit-score-label {
    font-size: 0.75rem;
    color: var(--text-muted);
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.fit-bar-track {
    background: var(--border);
    border-radius: 999px;
    height: 8px;
    overflow: hidden;
    margin-top: 0.5rem;
}
.fit-bar-fill {
    height: 100%;
    border-radius: 999px;
    background: linear-gradient(90deg, var(--accent), #818cf8);
    transition: width 0.6s ease;
}

/* ── Chips ── */
.chip {
    display: inline-block;
    padding: 0.2rem 0.65rem;
    border-radius: 20px;
    font-size: 0.76rem;
    font-weight: 500;
    margin: 0.2rem 0.15rem;
    font-family: 'JetBrains Mono', monospace;
}
.chip.has {
    background: var(--tag-matched-bg);
    color: var(--tag-matched-fg);
    border: 1px solid var(--tag-matched-bd);
}
.chip.lacks {
    background: var(--tag-missing-bg);
    color: var(--tag-missing-fg);
    border: 1px solid var(--tag-missing-bd);
}

/* ── Q&A cards ── */
.qa-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 0.9rem 1.1rem;
    margin-bottom: 0.5rem;
    font-size: 0.875rem;
    color: var(--text-primary);
    box-shadow: var(--shadow-sm);
}
.qa-category {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: var(--accent);
    margin-bottom: 0.3rem;
}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: var(--bg-sidebar);
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] .block-container {
    padding-top: 1.25rem;
}
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] p,
section[data-testid="stSidebar"] span,
section[data-testid="stSidebar"] div {
    color: var(--text-primary) !important;
}

/* ── Pill info ── */
.pill-info {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 0.6rem 0.8rem;
    font-size: 0.8rem;
    color: var(--text-secondary);
    margin-top: 0.5rem;
}
.pill-info strong { color: var(--text-primary); }

/* ── Comparison winner cards ── */
.winner-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 0.75rem;
    margin-bottom: 1.25rem;
}
@media (max-width: 768px) {
    .winner-grid { grid-template-columns: 1fr; }
}
.winner-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 1rem 1.25rem;
    box-shadow: var(--shadow-sm);
}
.winner-label {
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-muted);
    margin-bottom: 0.3rem;
}
.winner-value {
    font-size: 1.1rem;
    font-weight: 700;
    color: var(--text-primary);
}
.winner-value.good { color: var(--success); }
.winner-value.mid { color: var(--warning); }

/* ── Streamlit overrides ── */
.stButton > button {
    font-family: 'Inter', sans-serif;
    font-weight: 500;
    font-size: 0.875rem;
    border-radius: var(--radius-sm);
    transition: background 0.15s, transform 0.1s;
}
.stButton > button:active { transform: scale(0.98); }

.stButton > button[kind="primary"],
.stButton > button[data-testid*="primary"] {
    background: var(--accent) !important;
    color: #fff !important;
    border: none !important;
}
.stButton > button[kind="primary"]:hover {
    background: var(--accent-hover) !important;
}

.stTabs [data-baseweb="tab-list"] {
    gap: 0;
    border-bottom: 1px solid var(--border);
    background: transparent;
}
.stTabs [data-baseweb="tab"] {
    font-size: 0.82rem;
    font-weight: 500;
    padding: 0.55rem 0.9rem;
    color: var(--text-secondary);
    background: transparent;
    border-bottom: 2px solid transparent;
    margin-bottom: -1px;
}
.stTabs [aria-selected="true"] {
    color: var(--accent) !important;
    border-bottom: 2px solid var(--accent) !important;
    background: transparent !important;
}
.stTabs [data-baseweb="tab"]:hover {
    color: var(--text-primary);
    background: var(--bg-card-hover);
}

[data-testid="stMetricValue"] {
    font-size: 1.6rem !important;
    font-family: 'JetBrains Mono', monospace !important;
    font-weight: 700 !important;
    color: var(--text-primary) !important;
}
[data-testid="stMetricLabel"] {
    color: var(--text-muted) !important;
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.06em !important;
}

.stAlert { border-radius: var(--radius-sm) !important; }
hr { border-color: var(--border) !important; }
.stTextInput input, .stTextArea textarea {
    border-color: var(--border) !important;
    border-radius: var(--radius-sm) !important;
}
.stDataFrame { border-radius: var(--radius-sm); overflow: hidden; }
.streamlit-expanderHeader {
    font-size: 0.875rem !important;
    font-weight: 500 !important;
    color: var(--text-secondary) !important;
}
.stSpinner > div { color: var(--text-secondary) !important; }
.stCaption, .stCaption p { color: var(--text-muted) !important; }

/* ── Loading animation ── */
.loading-step {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.4rem 0;
    font-size: 0.875rem;
    color: var(--text-secondary);
    animation: fadeIn 0.3s ease;
}
.loading-step .dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--accent);
    animation: pulse 1.2s infinite;
}
@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
@keyframes fadeIn { from{opacity:0;transform:translateY(4px)} to{opacity:1;transform:none} }

/* ── Mobile responsiveness ── */
@media (max-width: 768px) {
    .block-container { padding: 1rem !important; }
    .score-grid { grid-template-columns: repeat(2, 1fr); }
    .kpi-grid { grid-template-columns: repeat(2, 1fr); }
    .winner-grid { grid-template-columns: 1fr; }
    .riq-title { font-size: 1.25rem; }
}
</style>
""", unsafe_allow_html=True)


# ── Session state defaults ─────────────────────────────────────────────────
DEFAULTS = {
    "user": None, "resume_text": None, "sections": None, "resume_version_id": None,
    "jd_text": None, "jd_structured": None, "ats_result": None,
    "resume_versions_cache": [], "sw": None, "qs": None,
    "company_fit": None, "roadmap_plan": None,
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Helpers ────────────────────────────────────────────────────────────────

def score_class(score: float) -> str:
    if score >= 70: return "good"
    if score >= 45: return "mid"
    return "low"

def score_color(score: float) -> str:
    if score >= 70: return "var(--success)"
    if score >= 45: return "var(--warning)"
    return "var(--danger)"

def skill_tags_html(skills: list, cls: str) -> str:
    return " ".join(f'<span class="skill-tag {cls}">{s}</span>' for s in skills)

def chip_html(skills: list, has: bool) -> str:
    cls = "has" if has else "lacks"
    return " ".join(f'<span class="chip {cls}">{s}</span>' for s in skills)

def progress_bar_html(label: str, value: float) -> str:
    sc = score_class(value)
    color = "var(--success)" if sc == "good" else "var(--warning)" if sc == "mid" else "var(--danger)"
    return f"""
    <div class="progress-wrap">
        <div class="progress-header">
            <span class="progress-label">{label}</span>
            <span class="progress-value" style="color:{color}">{value:.1f}%</span>
        </div>
        <div class="progress-track">
            <div class="progress-fill {sc}" style="width:{value}%"></div>
        </div>
    </div>"""

def empty_state_html(icon: str, title: str, desc: str) -> str:
    return f"""
    <div class="empty-state">
        <div class="empty-state-icon">{icon}</div>
        <div class="empty-state-title">{title}</div>
        <div class="empty-state-desc">{desc}</div>
    </div>"""

def loading_step(message: str) -> str:
    return f'<div class="loading-step"><span class="dot"></span>{message}</div>'

def plotly_layout_defaults():
    return dict(
        font_family="Inter",
        font_color="var(--text-primary)",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=0, r=0, t=40, b=0),
        title_font_size=13,
    )


# ── Authentication ─────────────────────────────────────────────────────────
def render_auth():
    col = st.columns([1, 1.8, 1])[1]
    with col:
        st.markdown("""
        <div style="text-align:center;padding:3rem 0 1.5rem">
            <div style="font-size:2rem;font-weight:700;letter-spacing:-0.04em;
                        color:var(--text-primary)">ResumeIQ</div>
            <div style="font-size:0.9rem;color:var(--text-secondary);margin-top:0.4rem">
                AI-powered resume analysis and career coaching
            </div>
        </div>
        """, unsafe_allow_html=True)

        t_in, t_up, t_guest = st.tabs(["Sign in", "Create account", "Guest"])

        with t_in:
            u = st.text_input("Username", key="li_u", placeholder="username")
            p = st.text_input("Password", type="password", key="li_p", placeholder="password")
            if st.button("Sign in", type="primary", use_container_width=True, key="li_btn"):
                try:
                    r = auth.login(u, p)
                    if r["success"]:
                        st.session_state.user = r["user"]; st.rerun()
                    else:
                        st.error(r["error"])
                except Exception as e:
                    st.error(f"Login failed: {e}")

        with t_up:
            u2 = st.text_input("Username", key="su_u", placeholder="choose a username")
            p2 = st.text_input("Password", type="password", key="su_p",
                                placeholder="at least 6 characters")
            if st.button("Create account", type="primary", use_container_width=True, key="su_btn"):
                try:
                    r = auth.signup(u2, p2)
                    if r["success"]:
                        st.session_state.user = r["user"]; st.rerun()
                    else:
                        st.error(r["error"])
                except Exception as e:
                    st.error(f"Sign-up failed: {e}")

        with t_guest:
            st.caption("History, version tracking, and dashboard are not saved in guest mode.")
            if st.button("Continue as guest", use_container_width=True, key="g_btn"):
                st.session_state.user = {"id": None, "username": "guest"}; st.rerun()


if st.session_state.user is None:
    render_auth()
    st.stop()

is_guest = st.session_state.user["id"] is None


# ── Sidebar ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(f"""
    <div style="font-size:0.8rem;color:var(--text-secondary);margin-bottom:0.5rem">
        Signed in as <strong style="color:var(--text-primary)">
        {st.session_state.user['username']}</strong>
        {'&nbsp;<span style="color:var(--text-muted)">(guest)</span>' if is_guest else ''}
    </div>
    """, unsafe_allow_html=True)
    if st.button("Sign out", use_container_width=True, key="signout"):
        for k in DEFAULTS:
            st.session_state[k] = DEFAULTS[k]
        st.rerun()

    st.divider()

    # ── Target Job section ──
    st.markdown('<div style="font-size:0.75rem;font-weight:600;text-transform:uppercase;'
                'letter-spacing:0.08em;color:var(--text-muted);margin-bottom:0.5rem">'
                'Target Job</div>', unsafe_allow_html=True)

    # Company selector
    company_options = ["—"] + company_profiles.list_supported_companies()
    selected_company = st.selectbox("Target company", company_options,
                                     label_visibility="collapsed")
    if selected_company == "—":
        selected_company = None

    jd_mode = st.radio("JD input", ["Paste text", "From URL"],
                        label_visibility="collapsed", horizontal=True)

    if jd_mode == "From URL":
        jd_url = st.text_input("Job URL", placeholder="https://...",
                                label_visibility="collapsed")
        if st.button("Fetch JD", use_container_width=True) and jd_url:
            with st.spinner("Fetching job description..."):
                try:
                    raw = jd_extractor.fetch_jd_text_from_url(jd_url)
                    st.session_state.jd_text = raw
                    with st.spinner("Structuring with AI..."):
                        st.session_state.jd_structured = llm.structure_job_description(raw)
                    st.success("JD extracted.")
                except jd_extractor.JDFetchError as e:
                    st.error(str(e))
                except Exception as e:
                    st.error(f"Failed to fetch JD: {e}")
    else:
        jd_paste = st.text_area("Paste JD", height=120, label_visibility="collapsed",
                                 placeholder="Paste the full job description here...")
        if st.button("Use this JD", use_container_width=True) and jd_paste.strip():
            st.session_state.jd_text = jd_paste
            with st.spinner("Structuring with AI..."):
                try:
                    st.session_state.jd_structured = llm.structure_job_description(jd_paste)
                    st.success("JD ready.")
                except Exception as e:
                    st.warning(f"AI structuring failed: {e}")
                    st.session_state.jd_structured = None

    if st.session_state.jd_structured:
        jd = st.session_state.jd_structured
        st.markdown(f"""
        <div class="pill-info">
            <strong>{jd.get('job_title', '—')}</strong><br>
            <span style="color:var(--text-muted)">{jd.get('company', '—')}</span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Resume section ──
    st.markdown('<div style="font-size:0.75rem;font-weight:600;text-transform:uppercase;'
                'letter-spacing:0.08em;color:var(--text-muted);margin-bottom:0.5rem">'
                'Resume</div>', unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="collapsed")
    vlabel = st.text_input("Version label", placeholder="e.g. v2 — added Docker",
                            label_visibility="collapsed")

    if uploaded and st.button("Parse & Analyze", use_container_width=True, type="primary"):
        status_placeholder = st.empty()
        try:
            # Step 1: Extract text
            status_placeholder.markdown(loading_step("Extracting text from PDF..."),
                                        unsafe_allow_html=True)
            full_text = resume_parser.extract_text(uploaded)
            if not full_text.strip():
                st.error("Could not extract text from this PDF. It may be image-only or corrupted.")
                st.stop()
            st.session_state.resume_text = full_text

            # Step 2: Parse sections
            status_placeholder.markdown(loading_step("Parsing resume sections..."),
                                        unsafe_allow_html=True)
            st.session_state.sections = resume_parser.split_into_sections(full_text)

            # Step 3: Save version
            if not is_guest:
                status_placeholder.markdown(loading_step("Saving version..."),
                                            unsafe_allow_html=True)
                lbl = vlabel.strip() or f"Version {len(st.session_state.resume_versions_cache) + 1}"
                vid = storage.save_resume_version(
                    st.session_state.user["id"], lbl, full_text, uploaded.name)
                st.session_state.resume_version_id = vid
                st.session_state.resume_versions_cache = storage.get_resume_versions(
                    st.session_state.user["id"])

            status_placeholder.empty()
            st.success("Resume parsed successfully.")

        except Exception as e:
            status_placeholder.empty()
            st.error(f"Failed to parse resume: {e}")

    if st.session_state.resume_text:
        wc = len(st.session_state.resume_text.split())
        secs = list(st.session_state.sections.keys()) if st.session_state.sections else []
        st.markdown(f"""
        <div class="pill-info">
            <strong>{wc:,} words</strong> &nbsp;|&nbsp; {len(secs)} sections<br>
            <span style="color:var(--text-muted);font-size:0.75rem">{', '.join(secs[:4])}{'...' if len(secs) > 4 else ''}</span>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # ── Quick Analysis ──
    if st.session_state.resume_text and st.session_state.jd_text:
        if st.button("Run Full Analysis", type="primary", use_container_width=True, key="sidebar_run"):
            st.session_state["_trigger_analysis"] = True
            st.rerun()


# ── Main header ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="riq-header">
    <div class="riq-title">ResumeIQ</div>
    <div class="riq-subtitle">AI Career Copilot — ATS scoring, keyword gaps, company fit, interview prep</div>
</div>
""", unsafe_allow_html=True)

# ── Empty states for missing data ──
if not st.session_state.resume_text or not st.session_state.jd_text:
    col1, col2 = st.columns(2)
    with col1:
        if st.session_state.jd_text:
            st.markdown("""
            <div style="background:var(--bg-card);border:1px solid var(--border);
                        border-radius:var(--radius-md);padding:1.25rem;text-align:center;">
                <div style="font-size:2rem;margin-bottom:0.5rem;">📄</div>
                <div style="font-weight:600;color:var(--text-primary);">Job Description Loaded</div>
                <div style="font-size:0.85rem;color:var(--text-secondary);">Ready for analysis</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(empty_state_html("📄", "Step 1: Job Description",
                                         "Paste or fetch a job description in the sidebar."),
                        unsafe_allow_html=True)
    with col2:
        if st.session_state.resume_text:
            st.markdown("""
            <div style="background:var(--bg-card);border:1px solid var(--border);
                        border-radius:var(--radius-md);padding:1.25rem;text-align:center;">
                <div style="font-size:2rem;margin-bottom:0.5rem;">📋</div>
                <div style="font-weight:600;color:var(--text-primary);">Resume Parsed</div>
                <div style="font-size:0.85rem;color:var(--text-secondary);">Ready for analysis</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(empty_state_html("📋", "Step 2: Resume",
                                         "Upload your PDF resume in the sidebar."),
                        unsafe_allow_html=True)
    st.stop()


# ── Tabs ────────────────────────────────────────────────────────────────────
TAB_NAMES = [
    "Analysis", "Strengths & Bullets", "Company Fit",
    "Skill Roadmap", "Interview Prep", "Rewrite Section",
    "PDF Report", "Dashboard", "Compare Resumes",
    "Compare JDs", "Similar Roles",
]
tabs = st.tabs(TAB_NAMES)


# ══════════════════════════════════════════════════════════════════════════════
# TAB 0 — Analysis
# ══════════════════════════════════════════════════════════════════════════════
with tabs[0]:
    run_col, _ = st.columns([2, 5])
    with run_col:
        run_clicked = st.button("Run Analysis", type="primary",
                                use_container_width=True, key="run_analysis")

    if run_clicked or st.session_state.get("_trigger_analysis", False):
        st.session_state["_trigger_analysis"] = False
        status_area = st.empty()

        steps = [
            "Parsing resume sections...",
            "Extracting skills from job description...",
            "Computing keyword gap...",
            "Calculating ATS score...",
            "Checking eligibility...",
        ]

        try:
            for i, step in enumerate(steps):
                status_area.markdown(loading_step(step), unsafe_allow_html=True)
                time.sleep(0.2)

            candidate_months = resume_parser.estimate_experience_months(
                st.session_state.resume_text)
            jd_skills_llm = (st.session_state.jd_structured or {}).get("skills", [])
            result = ats.compute_ats_score(
                st.session_state.resume_text,
                st.session_state.jd_text,
                st.session_state.sections,
                candidate_months,
                jd_structured_skills=jd_skills_llm,
            )
            result["eligibility"] = ats.check_eligibility(
                result["required_years"], candidate_months)
            st.session_state.ats_result = result
            status_area.empty()

            if not is_guest:
                try:
                    storage.save_analysis(
                        st.session_state.user["id"],
                        st.session_state.resume_version_id,
                        (st.session_state.jd_structured or {}).get("job_title", "JD"),
                        st.session_state.jd_text,
                        result["overall"],
                        result["breakdown"],
                        result["keyword_gap"],
                    )
                except Exception as e:
                    # Don't break UI for storage errors
                    pass

        except Exception as e:
            status_area.empty()
            st.error(f"Analysis failed: {e}")

    if st.session_state.ats_result:
        r = st.session_state.ats_result
        bd = r["breakdown"]

        scores = [
            ("Overall ATS", r["overall"]),
            ("Skill Match", bd["skill_match"]),
            ("Text Similarity", bd["text_similarity"]),
            ("Experience Match", bd["experience_match"]),
            ("Section Score", bd["section_completeness"]),
        ]
        card_html = '<div class="score-grid">'
        for label, val in scores:
            cc = score_class(val)
            card_html += f"""
            <div class="score-card">
                <div class="sc-label">{label}</div>
                <div class="sc-value {cc}">{val:.1f}%</div>
            </div>"""
        card_html += "</div>"
        st.markdown(card_html, unsafe_allow_html=True)

        elig = r["eligibility"]
        if elig["eligible"]:
            st.markdown(f'<div class="banner success"><strong>Eligible</strong> — {elig["reason"]}</div>',
                        unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="banner danger"><strong>Not eligible</strong> — {elig["reason"]}</div>',
                        unsafe_allow_html=True)
            if elig.get("recommendation"):
                st.markdown(f'<div class="banner warning">Recommendation: {elig["recommendation"]}</div>',
                            unsafe_allow_html=True)

        st.markdown('<div class="section-heading">Keyword Gap Analysis</div>',
                    unsafe_allow_html=True)
        gap = r["keyword_gap"]
        gc1, gc2 = st.columns(2)
        with gc1:
            st.markdown(f"**Matched skills ({len(gap['matched'])})**")
            if gap["matched"]:
                st.markdown(skill_tags_html(gap["matched"], "matched"),
                            unsafe_allow_html=True)
            else:
                st.caption("No skills matched from the known skill database.")
        with gc2:
            st.markdown(f"**Missing skills ({len(gap['missing'])})**")
            if gap["missing"]:
                st.markdown(skill_tags_html(gap["missing"], "missing"),
                            unsafe_allow_html=True)
            else:
                st.caption("No missing skills — strong match.")

        if gap.get("extra"):
            with st.expander(f"Additional skills on your resume not in JD ({len(gap['extra'])})"):
                st.markdown(skill_tags_html(gap["extra"], "extra"),
                            unsafe_allow_html=True)

        if st.session_state.jd_structured:
            jd = st.session_state.jd_structured
            if jd.get("skills"):
                with st.expander("Skills mentioned in job description"):
                    st.markdown(skill_tags_html(
                        [s for s in jd["skills"] if s], "extra"),
                        unsafe_allow_html=True)
    else:
        st.caption("Click 'Run Analysis' to compute your ATS score.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — Strengths & Bullet Improvement
# ══════════════════════════════════════════════════════════════════════════════
with tabs[1]:
    if not st.session_state.ats_result:
        st.markdown('<div class="banner info">Run the Analysis tab first.</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<div class="section-heading">Strengths & Weaknesses</div>',
                    unsafe_allow_html=True)
        if st.button("Generate AI analysis", key="gen_sw"):
            with st.spinner("Analyzing with AI..."):
                try:
                    st.session_state.sw = llm.generate_strengths_weaknesses(
                        st.session_state.resume_text,
                        st.session_state.jd_text,
                        st.session_state.ats_result,
                    )
                except Exception as e:
                    st.error(f"AI analysis failed: {e}")

        if st.session_state.sw:
            sw = st.session_state.sw
            sc1, sc2 = st.columns(2)
            with sc1:
                st.markdown("**Strengths**")
                for s in sw.get("strengths", []):
                    st.markdown(f'<div class="qa-card">'
                                f'<div class="qa-category">strength</div>{s}</div>',
                                unsafe_allow_html=True)
            with sc2:
                st.markdown("**Gaps**")
                for w in sw.get("weaknesses", []):
                    st.markdown(f'<div class="qa-card">'
                                f'<div class="qa-category" style="color:var(--danger)">gap</div>{w}</div>',
                                unsafe_allow_html=True)

        st.markdown('<div class="section-heading">Resume Bullet Improver</div>',
                    unsafe_allow_html=True)
        st.caption("Paste a bullet point from your resume. The AI will rewrite it with stronger verbs and better JD alignment — without fabricating metrics.")
        bullet_input = st.text_area("Paste a bullet point", height=80,
                                     label_visibility="collapsed",
                                     placeholder="e.g. Worked on backend APIs for the mobile app.")
        if st.button("Improve this bullet", key="improve_bullet") and bullet_input.strip():
            with st.spinner("Rewriting..."):
                try:
                    improved = llm.improve_bullet(bullet_input, st.session_state.jd_text)
                    st.markdown("**Original:**")
                    st.code(bullet_input.strip(), language=None)
                    st.markdown("**Improved:**")
                    st.markdown(f'<div class="qa-card">{improved}</div>',
                                unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Rewrite failed: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — Company Fit
# ══════════════════════════════════════════════════════════════════════════════
with tabs[2]:
    if not st.session_state.ats_result:
        st.markdown('<div class="banner info">Run the Analysis tab first.</div>',
                    unsafe_allow_html=True)
    else:
        company_name = selected_company
        if not company_name:
            available = company_profiles.list_supported_companies()
            company_name = st.selectbox("Select a target company", ["—"] + available,
                                         key="company_fit_select")
            if company_name == "—":
                company_name = None

        if company_name:
            try:
                profile = company_profiles.get_profile(company_name)
                if profile:
                    fit = ats.compute_company_fit(
                        st.session_state.resume_text, profile)
                    st.session_state.company_fit = fit

                    fc = score_color(fit["fit_score"])
                    st.markdown(f"""
                    <div class="fit-section">
                        <div class="fit-company-name">{profile['name'].title()}</div>
                        <div class="fit-focus">{profile.get('hiring_focus', '')}</div>
                        <div class="fit-score-row">
                            <div>
                                <div class="fit-score-number" style="color:{fc}">
                                    {fit['fit_score']:.1f}%
                                </div>
                                <div class="fit-score-label">Company Fit Score</div>
                            </div>
                        </div>
                        <div class="fit-bar-track">
                            <div class="fit-bar-fill" style="width:{fit['fit_score']}%"></div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                    pc1, pc2 = st.columns(2)
                    with pc1:
                        st.markdown(f"**Priority skills you have ({len(fit['matched_priority'])})**")
                        if fit["matched_priority"]:
                            st.markdown(chip_html(fit["matched_priority"], has=True),
                                        unsafe_allow_html=True)
                        else:
                            st.caption("None of their priority skills detected on your resume.")
                    with pc2:
                        st.markdown(f"**Priority skills to add ({len(fit['missing_priority'])})**")
                        if fit["missing_priority"]:
                            st.markdown(chip_html(fit["missing_priority"], has=False),
                                        unsafe_allow_html=True)
                        else:
                            st.caption("You have all their priority skills.")

                    st.markdown('<div class="section-heading">Company Context</div>',
                                unsafe_allow_html=True)
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown("**Interview style**")
                        st.caption(profile.get("culture_notes", ""))
                    with col_b:
                        st.markdown("**Leveling notes**")
                        st.caption(profile.get("leveling_hint", ""))

                    st.markdown('<div class="section-heading">AI Feedback</div>',
                                unsafe_allow_html=True)
                    if st.button("Generate company-specific feedback", key="gen_company_feedback"):
                        with st.spinner("Generating personalized feedback..."):
                            try:
                                feedback = llm.generate_company_specific_feedback(
                                    st.session_state.resume_text,
                                    st.session_state.jd_text,
                                    st.session_state.ats_result,
                                    profile,
                                    fit,
                                )
                                st.markdown(f'<div class="qa-card">{feedback}</div>',
                                            unsafe_allow_html=True)
                            except Exception as e:
                                st.error(f"Feedback generation failed: {e}")
            except Exception as e:
                st.error(f"Failed to load company profile: {e}")
        else:
            st.caption("Select a company from the sidebar or dropdown above.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — Skill Roadmap
# ══════════════════════════════════════════════════════════════════════════════
with tabs[3]:
    if not st.session_state.ats_result:
        st.markdown('<div class="banner info">Run the Analysis tab first.</div>',
                    unsafe_allow_html=True)
    else:
        gap = st.session_state.ats_result["keyword_gap"]
        company_missing = []
        if st.session_state.company_fit:
            company_missing = st.session_state.company_fit.get("missing_priority", [])

        weeks_n = st.slider("Roadmap length (weeks)", 4, 12, 8, key="roadmap_weeks")

        col1, col2 = st.columns([2, 1])
        with col1:
            build_clicked = st.button("Build Roadmap", key="build_roadmap", type="primary")
        with col2:
            if st.session_state.roadmap_plan:
                if st.button("Reset", key="rebuild_roadmap"):
                    st.session_state.roadmap_plan = None
                    st.rerun()

        if build_clicked or (st.session_state.roadmap_plan and not build_clicked):
            if build_clicked:
                try:
                    plan = roadmap.build_roadmap(
                        gap["missing"], weeks_n, company_missing_priority=company_missing)
                    st.session_state.roadmap_plan = plan
                except Exception as e:
                    st.error(f"Failed to build roadmap: {e}")

            if st.session_state.roadmap_plan:
                plan = st.session_state.roadmap_plan
                if not plan:
                    st.markdown('<div class="banner success">No skill gaps detected — your resume already covers the key skills for this role.</div>',
                                unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="banner info">{len(plan)}-week learning plan covering {sum(len(w["skills"]) for w in plan)} skills.</div>',
                                unsafe_allow_html=True)
                    for w in plan:
                        priority = w.get("priority", "Medium")
                        skills_str = ", ".join(w["skills"])
                        st.markdown(f"""
                        <div class="week-card">
                            <span class="week-badge">Week {w['week']}</span>
                            <span class="week-priority {priority}">{priority}</span>
                            <div class="week-content">
                                <div class="week-skills">{skills_str}</div>
                                <div class="week-focus">{w['focus']}</div>
                                <div class="week-resource">Resource: {w.get('resource', '')}</div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
            elif not build_clicked:
                st.caption("Click 'Build Roadmap' to generate your personalized learning plan.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — Interview Prep
# ══════════════════════════════════════════════════════════════════════════════
with tabs[4]:
    if not st.session_state.ats_result:
        st.markdown('<div class="banner info">Run the Analysis tab first.</div>',
                    unsafe_allow_html=True)
    else:
        if st.button("Generate interview questions", key="gen_iq", type="primary"):
            with st.spinner("Generating personalized questions..."):
                try:
                    st.session_state.qs = llm.generate_interview_questions(
                        st.session_state.resume_text, st.session_state.jd_text)
                except Exception as e:
                    st.error(f"Question generation failed: {e}")

        if st.session_state.qs:
            qs = st.session_state.qs
            categories = [
                ("HR & Behavioral", qs.get("hr_questions", []), "var(--accent)"),
                ("Technical", qs.get("technical_questions", []), "var(--success)"),
                ("Project-based", qs.get("project_questions", []), "var(--warning)"),
            ]
            for cat_name, questions, color in categories:
                if questions:
                    st.markdown(f'<div class="section-heading">{cat_name}</div>',
                                unsafe_allow_html=True)
                    for q in questions:
                        st.markdown(
                            f'<div class="qa-card">'
                            f'<div class="qa-category" style="color:{color}">'
                            f'{cat_name.split(" ")[0].lower()}</div>{q}</div>',
                            unsafe_allow_html=True)
        else:
            st.caption("Click 'Generate interview questions' to get personalized prep questions.")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — Rewrite Section
# ══════════════════════════════════════════════════════════════════════════════
with tabs[5]:
    if not st.session_state.ats_result:
        st.markdown('<div class="banner info">Run the Analysis tab first.</div>',
                    unsafe_allow_html=True)
    else:
        sections = st.session_state.sections or {}
        available_sections = [s for s in ["experience", "skills", "projects"] if s in sections]

        if available_sections:
            st.markdown('<div class="section-heading">Section Rewrite</div>',
                        unsafe_allow_html=True)
            st.caption("Rewrites a specific section — stronger verbs, better JD alignment. Never fabricates experience or metrics.")
            chosen_section = st.selectbox("Section to rewrite", available_sections,
                                           format_func=str.title)
            if st.button(f"Rewrite {chosen_section.title()} section", type="primary",
                         key="rewrite_section"):
                with st.spinner(f"Rewriting {chosen_section.title()} section..."):
                    try:
                        rewritten = llm.rewrite_resume_section(
                            st.session_state.resume_text,
                            st.session_state.jd_text,
                            chosen_section,
                            sections[chosen_section],
                            st.session_state.ats_result["keyword_gap"]["missing"],
                        )
                        st.markdown(rewritten)
                        st.download_button(
                            f"Download rewritten {chosen_section}.md",
                            data=rewritten,
                            file_name=f"resume_{chosen_section}_rewrite.md",
                            mime="text/markdown",
                        )
                    except Exception as e:
                        st.error(f"Rewrite failed: {e}")
        else:
            st.caption("No Experience, Skills, or Projects sections found in your resume.")

        st.divider()
        st.markdown('<div class="section-heading">Full Resume Rewrite</div>',
                    unsafe_allow_html=True)
        st.caption("Rewrites the entire resume. Explicitly instructed not to fabricate experience.")
        if st.button("Generate full rewrite", key="full_rewrite"):
            with st.spinner("Rewriting..."):
                try:
                    full_rewrite = llm.rewrite_resume(
                        st.session_state.resume_text,
                        st.session_state.jd_text,
                        st.session_state.ats_result["keyword_gap"]["missing"],
                    )
                    st.markdown(full_rewrite)
                    st.download_button(
                        "Download full rewrite (Markdown)",
                        data=full_rewrite,
                        file_name="resume_full_rewrite.md",
                        mime="text/markdown",
                    )
                except Exception as e:
                    st.error(f"Rewrite failed: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — PDF Report
# ══════════════════════════════════════════════════════════════════════════════
with tabs[6]:
    if not st.session_state.ats_result:
        st.markdown('<div class="banner info">Run the Analysis tab first.</div>',
                    unsafe_allow_html=True)
    else:
        st.caption("Download a professional PDF report with your ATS score, "
                   "keyword gap, eligibility, and roadmap.")
        if st.button("Build PDF report", type="primary", key="build_pdf"):
            with st.spinner("Building PDF..."):
                try:
                    pdf_bytes = report.build_pdf_report(
                        st.session_state.jd_structured or {},
                        st.session_state.ats_result,
                        strengths_weaknesses=st.session_state.sw,
                        roadmap=st.session_state.roadmap_plan,
                    )
                    st.download_button(
                        "Download ATS Report (PDF)",
                        data=pdf_bytes,
                        file_name="resumeiq_report.pdf",
                        mime="application/pdf",
                    )
                except Exception as e:
                    st.error(f"PDF generation failed: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 7 — Dashboard (Professional Layout)
# ══════════════════════════════════════════════════════════════════════════════
with tabs[7]:
    if is_guest:
        st.markdown(empty_state_html("📊", "Sign In to View Dashboard",
                                     "Create a free account to track your ATS score over time, see improvement trends, and compare resume versions."),
                    unsafe_allow_html=True)
    else:
        try:
            analyses = storage.get_analyses(st.session_state.user["id"])
        except Exception as e:
            st.error(f"Could not load history: {e}")
            analyses = []

        if not analyses:
            st.markdown(empty_state_html("📊", "No Analyses Yet",
                                         "Upload a resume and run an analysis to start tracking your ATS score progress over time."),
                        unsafe_allow_html=True)
        else:
            # Build dataframe
            df = pd.DataFrame([{
                "run": i + 1,
                "label": f"#{i+1}",
                "resume": a.get("resume_label") or "Unknown",
                "jd": a.get("jd_label") or "Unknown JD",
                "overall_score": a["overall_score"],
                "skill_match": a["breakdown"]["skill_match"],
                "text_similarity": a["breakdown"]["text_similarity"],
                "experience_match": a["breakdown"]["experience_match"],
                "section_completeness": a["breakdown"]["section_completeness"],
                "date": a.get("created_at", datetime.now().strftime("%Y-%m-%d")),
            } for i, a in enumerate(analyses)])

            latest_score = df["overall_score"].iloc[-1]
            best_score = df["overall_score"].max()
            avg_score = df["overall_score"].mean()
            first_score = df["overall_score"].iloc[0]
            improvement = latest_score - first_score
            last_jd = df["jd"].iloc[-1]
            last_resume = df["resume"].iloc[-1]

            impr_color = "success" if improvement >= 0 else "danger"
            impr_prefix = "+" if improvement >= 0 else ""

            # ── ATS Score Cards ──
            st.markdown("""
            <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:0.75rem;margin-bottom:1.25rem;">
            """, unsafe_allow_html=True)

            scores = [
                ("Overall ATS Score", latest_score, "Latest Analysis"),
                ("Best Score", best_score, "All-time peak"),
                ("Average Score", avg_score, f"Across {len(df)} analyses"),
                ("Improvement", improvement, f"{impr_prefix}{improvement:.1f}% since first"),
            ]

            for label, val, sub in scores:
                if label == "Improvement":
                    cc = "success" if improvement >= 0 else "danger"
                    display_val = f"{impr_prefix}{val:.1f}%"
                else:
                    cc = score_class(val)
                    display_val = f"{val:.1f}%"

                st.markdown(f"""
                <div class="score-card" style="padding:1rem 1.1rem;">
                    <div class="sc-label">{label}</div>
                    <div class="sc-value {cc}">{display_val}</div>
                    <div style="font-size:0.65rem;color:var(--text-muted);margin-top:0.2rem;">{sub}</div>
                </div>
                """, unsafe_allow_html=True)

            st.markdown("</div>", unsafe_allow_html=True)

            # ── Recent Analysis Context ──
            st.markdown(f"""
            <div style="display:flex;gap:0.75rem;margin-bottom:1.25rem;flex-wrap:wrap;">
                <div class="pill-info" style="flex:1;min-width:150px;">
                    <strong>Last Role:</strong> {last_jd}
                </div>
                <div class="pill-info" style="flex:1;min-width:150px;">
                    <strong>Last Resume:</strong> {last_resume}
                </div>
                <div class="pill-info" style="flex:1;min-width:150px;">
                    <strong>Recent Score:</strong> {latest_score:.1f}%
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Two-column layout: Trends + Skill Match ──
            col_left, col_right = st.columns([3, 2])

            with col_left:
                # ATS Score Trends
                st.markdown('<div class="section-heading">ATS Score Trends</div>', unsafe_allow_html=True)

                # Show last 6 analyses or all if less
                display_df = df.tail(6) if len(df) > 6 else df

                fig1 = px.line(
                    display_df,
                    x="label",
                    y="overall_score",
                    markers=True,
                    hover_data=["resume", "jd"],
                    color_discrete_sequence=["#3b5bdb"],
                    title="",
                )
                fig1.add_hline(y=70, line_dash="dot", line_color="rgba(5,150,105,0.4)",
                               annotation_text="Target", annotation_position="bottom right")
                fig1.update_layout(
                    **plotly_layout_defaults(),
                    yaxis_range=[0, 100],
                    xaxis_title="Analysis",
                    yaxis_title="ATS Score (%)",
                    height=250,
                )
                fig1.update_traces(line_width=2.5, marker_size=8)
                st.plotly_chart(fig1, use_container_width=True)

                # Recent analyses table (compact)
                st.markdown('<div class="section-heading">Recent Analyses</div>', unsafe_allow_html=True)

                recent_df = df.tail(5)[["jd", "resume", "overall_score", "date"]].copy()
                recent_df.columns = ["Job Title", "Resume", "Score", "Date"]
                recent_df["Score"] = recent_df["Score"].apply(lambda x: f"{x:.1f}%")

                # Custom styling for table
                st.dataframe(
                    recent_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Job Title": st.column_config.TextColumn("Job Title"),
                        "Resume": st.column_config.TextColumn("Resume"),
                        "Score": st.column_config.TextColumn("Score"),
                        "Date": st.column_config.TextColumn("Date"),
                    }
                )

            with col_right:
                # Skill Match Overview
                st.markdown('<div class="section-heading">Skill Match Overview</div>', unsafe_allow_html=True)

                if st.session_state.ats_result:
                    gap = st.session_state.ats_result["keyword_gap"]

                    # Skill match percentage
                    total_skills = len(gap["matched"]) + len(gap["missing"])
                    match_pct = (len(gap["matched"]) / total_skills * 100) if total_skills > 0 else 0

                    st.markdown(f"""
                    <div style="text-align:center;padding:0.5rem 0 1rem;">
                        <div style="font-size:2.5rem;font-weight:700;font-family:'JetBrains Mono',monospace;
                                    color:{'var(--success)' if match_pct >= 70 else 'var(--warning)' if match_pct >= 45 else 'var(--danger)'};">
                            {match_pct:.0f}%
                        </div>
                        <div style="font-size:0.75rem;color:var(--text-muted);">Skill Match Rate</div>
                    </div>
                    """, unsafe_allow_html=True)

                    # Matched vs Missing
                    col_m1, col_m2 = st.columns(2)
                    with col_m1:
                        st.markdown(f"""
                        <div style="background:var(--success-soft);border-radius:var(--radius-sm);
                                    padding:0.75rem;text-align:center;">
                            <div style="font-size:1.5rem;font-weight:700;color:var(--success);">
                                {len(gap['matched'])}
                            </div>
                            <div style="font-size:0.7rem;color:var(--text-muted);">Matched</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col_m2:
                        st.markdown(f"""
                        <div style="background:var(--danger-soft);border-radius:var(--radius-sm);
                                    padding:0.75rem;text-align:center;">
                            <div style="font-size:1.5rem;font-weight:700;color:var(--danger);">
                                {len(gap['missing'])}
                            </div>
                            <div style="font-size:0.7rem;color:var(--text-muted);">Missing</div>
                        </div>
                        """, unsafe_allow_html=True)

                    # Top matching skills
                    st.markdown("""
                    <div style="margin-top:0.75rem;">
                        <div style="font-size:0.75rem;font-weight:600;color:var(--text-muted);margin-bottom:0.3rem;">
                            Top Matching Skills
                        </div>
                    """, unsafe_allow_html=True)

                    if gap["matched"]:
                        top_skills = gap["matched"][:5]
                        st.markdown(skill_tags_html(top_skills, "matched"), unsafe_allow_html=True)
                    else:
                        st.caption("No matching skills found.")

                    st.markdown("</div>", unsafe_allow_html=True)

                    # Missing skills (if any)
                    if gap["missing"]:
                        st.markdown("""
                        <div style="margin-top:0.5rem;">
                            <div style="font-size:0.75rem;font-weight:600;color:var(--text-muted);margin-bottom:0.3rem;">
                                Missing Skills
                            </div>
                        """, unsafe_allow_html=True)
                        missing_skills = gap["missing"][:5]
                        st.markdown(skill_tags_html(missing_skills, "missing"), unsafe_allow_html=True)
                        if len(gap["missing"]) > 5:
                            st.caption(f"+ {len(gap['missing']) - 5} more missing skills")
                        st.markdown("</div>", unsafe_allow_html=True)
                else:
                    st.caption("Run an analysis to see skill match overview.")

                # ── Recommendations ──
                st.markdown('<div class="section-heading">Recommendations</div>', unsafe_allow_html=True)

                if st.session_state.ats_result:
                    gap = st.session_state.ats_result["keyword_gap"]
                    recommendations = []

                    # High priority
                    if len(gap["missing"]) > 5:
                        recommendations.append(("High", f"Add {len(gap['missing'])} missing skills to improve your match"))
                    elif len(gap["missing"]) > 2:
                        recommendations.append(("Medium", f"Add {len(gap['missing'])} key skills to strengthen your profile"))

                    # Check experience
                    if st.session_state.ats_result.get("eligibility"):
                        elig = st.session_state.ats_result["eligibility"]
                        if not elig.get("eligible", True):
                            recommendations.append(("High", elig.get("recommendation", "Gain more experience in this domain")))

                    # Company-specific
                    if st.session_state.company_fit:
                        company_missing = st.session_state.company_fit.get("missing_priority", [])
                        if company_missing:
                            recommendations.append(("Medium", f"Add {len(company_missing)} company-specific priority skills"))

                    # Default recommendations if none
                    if not recommendations:
                        recommendations = [
                            ("Low", "Continue refining your resume with stronger action verbs"),
                            ("Low", "Consider adding measurable outcomes to your experience"),
                        ]

                    # Display recommendations with priority badges
                    for priority, text in recommendations[:3]:
                        priority_class = "High" if priority == "High" else "Medium" if priority == "Medium" else "Low"
                        bg_color = "var(--danger-soft)" if priority == "High" else "var(--warning-soft)" if priority == "Medium" else "var(--accent-soft)"
                        text_color = "var(--danger)" if priority == "High" else "var(--warning)" if priority == "Medium" else "var(--accent)"

                        st.markdown(f"""
                        <div style="display:flex;align-items:center;gap:0.5rem;padding:0.4rem 0.75rem;
                                    margin-bottom:0.3rem;background:var(--bg-card);border-radius:var(--radius-sm);
                                    border-left:3px solid {text_color};">
                            <span style="font-size:0.6rem;font-weight:700;text-transform:uppercase;
                                        letter-spacing:0.05em;color:{text_color};background:{bg_color};
                                        padding:0.1rem 0.4rem;border-radius:3px;">
                                {priority}
                            </span>
                            <span style="font-size:0.8rem;color:var(--text-primary);">{text}</span>
                        </div>
                        """, unsafe_allow_html=True)
                else:
                    st.caption("Run an analysis to get personalized recommendations.")

            # ── Full history expander ──
            with st.expander("Full History Table"):
                st.dataframe(
                    df[["run", "resume", "jd", "overall_score",
                        "skill_match", "text_similarity",
                        "experience_match", "section_completeness", "date"]],
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "run": "Run",
                        "resume": "Resume",
                        "jd": "Job Description",
                        "overall_score": st.column_config.NumberColumn("Overall", format="%.1f%%"),
                        "skill_match": st.column_config.NumberColumn("Skill Match", format="%.1f%%"),
                        "text_similarity": st.column_config.NumberColumn("Text Similarity", format="%.1f%%"),
                        "experience_match": st.column_config.NumberColumn("Experience", format="%.1f%%"),
                        "section_completeness": st.column_config.NumberColumn("Sections", format="%.1f%%"),
                        "date": "Date",
                    }
                )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 8 — Compare Resumes (Improved)
# ══════════════════════════════════════════════════════════════════════════════
with tabs[8]:
    if is_guest:
        st.markdown(empty_state_html("📋", "Sign In to Compare Resumes",
                                     "Create a free account to save resume versions and compare them side-by-side."),
                    unsafe_allow_html=True)
    else:
        try:
            versions = storage.get_resume_versions(st.session_state.user["id"])
        except Exception as e:
            st.error(f"Could not load resume versions: {e}")
            versions = []

        if len(versions) < 2:
            st.markdown(empty_state_html("📋", "Need at least 2 Versions",
                                         "Upload and parse multiple resume versions to compare them against the same job description."),
                        unsafe_allow_html=True)
        else:
            labels = [v["label"] for v in versions]
            # Smart default: latest and second-latest
            default_selection = labels[-2:] if len(labels) >= 2 else labels

            st.markdown('<div class="section-heading">Select Versions to Compare</div>', unsafe_allow_html=True)
            chosen = st.multiselect(
                "Choose resume versions",
                labels,
                default=default_selection,
                help="Select 2 or more resume versions to compare against the current JD."
            )

            if len(chosen) < 2:
                st.info("Select at least 2 versions to compare.")
            elif st.button("Compare Selected", key="compare_versions", type="primary"):
                with st.spinner("Comparing resume versions..."):
                    try:
                        selected_v = [v for v in versions if v["label"] in chosen]
                        resume_inputs = [(v["label"], v["resume_text"]) for v in selected_v]
                        sects_list = [resume_parser.split_into_sections(v["resume_text"]) for v in selected_v]
                        months_list = [resume_parser.estimate_experience_months(v["resume_text"])
                                       for v in selected_v]
                        jd_skills = (st.session_state.jd_structured or {}).get("skills", [])
                        results = ats.compare_resumes(
                            resume_inputs, st.session_state.jd_text, sects_list,
                            months_list, jd_structured_skills=jd_skills)

                        # Sort by score descending
                        results_sorted = sorted(results, key=lambda x: x["overall"], reverse=True)
                        winner = results_sorted[0]
                        runner = results_sorted[-1]
                        delta = winner["overall"] - runner["overall"]

                        # Winner cards
                        st.markdown('<div class="section-heading">Comparison Summary</div>', unsafe_allow_html=True)
                        st.markdown(f"""
                        <div class="winner-grid">
                            <div class="winner-card">
                                <div class="winner-label">Winner</div>
                                <div class="winner-value good">{winner['label']}</div>
                            </div>
                            <div class="winner-card">
                                <div class="winner-label">Score Advantage</div>
                                <div class="winner-value {'good' if delta >= 5 else 'mid'}">+{delta:.1f}%</div>
                            </div>
                            <div class="winner-card">
                                <div class="winner-label">Recommendation</div>
                                <div class="winner-value" style="font-size:0.95rem;">Use <strong>{winner['label']}</strong></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

                        # Score breakdown per version
                        st.markdown('<div class="section-heading">Score Breakdown by Version</div>', unsafe_allow_html=True)
                        for res in results_sorted:
                            st.markdown(f"**{res['label']}**")
                            st.markdown(progress_bar_html("Overall ATS", res["overall"]) +
                                        progress_bar_html("Skill Match", res["breakdown"]["skill_match"]) +
                                        progress_bar_html("Text Similarity", res["breakdown"]["text_similarity"]),
                                        unsafe_allow_html=True)

                        # Bar chart
                        cmp_df = pd.DataFrame([{
                            "Version": r["label"],
                            "Overall ATS": r["overall"],
                            "Skill Match": r["breakdown"]["skill_match"],
                            "Text Similarity": r["breakdown"]["text_similarity"],
                        } for r in results_sorted])

                        fig = px.bar(
                            cmp_df, x="Overall ATS", y="Version", orientation="h",
                            color="Overall ATS",
                            color_continuous_scale=["#dc2626", "#d97706", "#059669"],
                            range_color=[0, 100],
                            text="Overall ATS",
                        )
                        fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
                        fig.update_layout(
                            **plotly_layout_defaults(),
                            xaxis_range=[0, 110],
                            coloraxis_showscale=False,
                            title="ATS Score by Resume Version",
                        )
                        st.plotly_chart(fig, use_container_width=True)

                        with st.expander("Full comparison table"):
                            st.dataframe(cmp_df, use_container_width=True)

                    except Exception as e:
                        st.error(f"Comparison failed: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 9 — Compare JDs
# ══════════════════════════════════════════════════════════════════════════════
with tabs[9]:
    st.markdown('<div class="section-heading">Compare Against Multiple Job Descriptions</div>',
                unsafe_allow_html=True)
    st.caption("Paste 2–5 JDs to see which role your resume matches best.")

    n = st.number_input("Number of JDs", min_value=2, max_value=5, value=2, key="jd_compare_n")
    jd_inputs = []
    for i in range(int(n)):
        c1, c2 = st.columns([1, 4])
        with c1:
            lbl = st.text_input("Label", value=f"JD {i+1}", key=f"jdlabel_{i}")
        with c2:
            txt = st.text_area(f"JD {i+1}", key=f"jdtext_{i}", height=90,
                                label_visibility="collapsed",
                                placeholder=f"Paste job description {i+1}...")
            if txt.strip():
                jd_inputs.append((lbl, txt))

    if st.button("Compare JDs", key="compare_jds", type="primary"):
        if len(jd_inputs) < 2:
            st.warning("Please fill in at least 2 job descriptions.")
        elif not st.session_state.resume_text:
            st.error("Please upload and parse a resume first.")
        else:
            with st.spinner("Matching resume against all JDs..."):
                try:
                    months = resume_parser.estimate_experience_months(st.session_state.resume_text)
                    results = ats.compare_jds(
                        st.session_state.resume_text, jd_inputs, st.session_state.sections, months)

                    winner = results[0]
                    st.markdown(f'<div class="banner success">Best Match: <strong>{winner["label"]}</strong> at {winner["overall"]:.1f}%</div>',
                                unsafe_allow_html=True)

                    st.markdown('<div class="section-heading">Scores by Job</div>', unsafe_allow_html=True)
                    for res in results:
                        st.markdown(f"**{res['label']}**")
                        st.markdown(progress_bar_html("Overall ATS", res["overall"]) +
                                    progress_bar_html("Skill Match", res["breakdown"]["skill_match"]),
                                    unsafe_allow_html=True)

                    cmp_df = pd.DataFrame([{
                        "Job": r["label"],
                        "ATS Score": r["overall"],
                        "Skill Match": r["breakdown"]["skill_match"],
                    } for r in results])

                    fig = px.bar(
                        cmp_df, x="ATS Score", y="Job", orientation="h",
                        color="ATS Score",
                        color_continuous_scale=["#dc2626", "#d97706", "#059669"],
                        range_color=[0, 100],
                        text="ATS Score",
                        title="Resume Match by Job",
                    )
                    fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
                    fig.update_layout(
                        **plotly_layout_defaults(),
                        xaxis_range=[0, 110],
                        coloraxis_showscale=False,
                    )
                    st.plotly_chart(fig, use_container_width=True)
                except Exception as e:
                    st.error(f"Comparison failed: {e}")


# ══════════════════════════════════════════════════════════════════════════════
# TAB 10 — Similar Roles
# ══════════════════════════════════════════════════════════════════════════════
with tabs[10]:
    if not st.session_state.jd_structured:
        st.markdown(empty_state_html("🔍", "No Job Description",
                                     "Provide a structured job description first — use the JD URL or paste it in the sidebar."),
                    unsafe_allow_html=True)
    else:
        st.caption("AI-generated role recommendations based on your JD profile — starting points, not verified live postings.")
        if st.button("Suggest similar roles", key="suggest_roles", type="primary"):
            with st.spinner("Finding similar roles..."):
                try:
                    suggestions = llm.suggest_similar_jobs(st.session_state.jd_structured)
                    roles = suggestions.get("similar_roles", [])
                    if roles:
                        for role in roles:
                            st.markdown(
                                f'<div class="qa-card">'
                                f'<div class="qa-category">{role.get("company", "")}</div>'
                                f'<strong>{role.get("role_title", "")}</strong><br>'
                                f'<span style="color:var(--text-secondary);font-size:0.82rem">'
                                f'{role.get("why_similar", "")}</span></div>',
                                unsafe_allow_html=True)
                    else:
                        st.warning("No suggestions returned. Try again.")
                except Exception as e:
                    st.error(f"AI call failed: {e}")
        else:
            st.markdown(empty_state_html("🔍", "Discover Similar Roles",
                                         "Click 'Suggest similar roles' to find comparable positions at other companies you could also apply to."),
                        unsafe_allow_html=True)