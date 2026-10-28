import random
import time

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from bucket_sort import (Entry, bucket_sort, insertion_sort, merge_sort,
                         quick_sort, time_it)

st.set_page_config(page_title="Bucket Sort Lab — P-12.61", page_icon="🪣", layout="wide",
                   initial_sidebar_state="auto")

# =====================================================================  design tokens
INK = "#0E1A2B"        # deep midnight, main text + sidebar
INK_2 = "#16263D"
MUTED = "#5B6B82"
LINE = "#E3E8F0"
PAPER = "#F5F7FB"      # page background
CARD = "#FFFFFF"
GOLD = "#C8962B"       # the one luxury accent
GOLD_SOFT = "#F6ECD6"
ROYAL = "#2F5BEA"
GOOD = "#1F8A5B"

COLORS = {"Bucket sort": GOLD, "Merge sort": "#3B4A6B", "Quick sort": "#1F8A84",
          "Insertion sort": "#C2415B", "Python sorted()": "#7A5AF8"}

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Serif+Display:ital@0;1&family=Manrope:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

:root {{
  --ink:{INK}; --ink2:{INK_2}; --muted:{MUTED}; --line:{LINE}; --paper:{PAPER}; --card:{CARD};
  --gold:{GOLD}; --gold-soft:{GOLD_SOFT}; --royal:{ROYAL}; --good:{GOOD};
  --serif:'DM Serif Display', Georgia, 'Times New Roman', serif;
  --sans:'Manrope', 'Segoe UI', system-ui, sans-serif;
  --mono:'JetBrains Mono', Consolas, monospace;
}}
.stApp {{ background: var(--paper); font-family: var(--sans); color: var(--ink); }}
.stApp p, .stApp li, .stApp label, .stMarkdown, .stCaption {{ font-family: var(--sans); }}
.block-container {{ padding-top: 2.2rem; padding-bottom: 4rem; max-width: 1220px; }}
#MainMenu, footer, [data-testid="stAppDeployButton"], [data-testid="stDecoration"] {{ visibility: hidden; height: 0; }}
[data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapsedControl"], [data-testid="stSidebarCollapseButton"] {{ visibility: visible !important; }}
@media (max-width: 768px) {{ .block-container {{ padding-top: 3.4rem; }} .ph h1 {{ font-size: 2.1rem; }} .hero {{ padding: 30px 24px; }} .hero .eyebrow {{ letter-spacing: .1em; }} .kpi {{ padding: 12px; }} .kpi .v {{ font-size: 1.2rem; white-space: nowrap; }} }}
header[data-testid="stHeader"] {{ background: transparent; }}

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] {{ background: linear-gradient(180deg, {INK} 0%, #0B1524 100%); border-right: 1px solid #1E2F48; }}
[data-testid="stSidebar"] * {{ color: #D9E2EF; }}
[data-testid="stSidebar"] .brand {{ display:flex; align-items:center; gap:12px; margin: 4px 0 6px; }}
[data-testid="stSidebar"] .brand .logo {{ width:42px; height:42px; border-radius:12px; display:grid; place-items:center;
   background: linear-gradient(135deg, {GOLD}, #E4BF6A); color:{INK}; font-family: var(--serif); font-size:22px; box-shadow: 0 6px 18px rgba(200,150,43,.35); }}
[data-testid="stSidebar"] .brand .t {{ font-family: var(--serif); font-size: 1.35rem; color:#fff; line-height:1.1; }}
[data-testid="stSidebar"] .brand .s {{ font-size: .72rem; letter-spacing: .14em; text-transform: uppercase; color: {GOLD}; }}
[data-testid="stSidebar"] [role="radiogroup"] {{ gap: 4px; }}
[data-testid="stSidebar"] [role="radiogroup"] label {{ padding: 10px 14px; border-radius: 12px; margin: 0; width: 100%;
   transition: background .15s ease; border: 1px solid transparent; }}
[data-testid="stSidebar"] [role="radiogroup"] label:hover {{ background: rgba(255,255,255,.06); }}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) {{ background: rgba(200,150,43,.14); border-color: rgba(200,150,43,.45); }}
[data-testid="stSidebar"] [role="radiogroup"] label:has(input:checked) p {{ color: #fff; font-weight: 700; }}
[data-testid="stSidebar"] [role="radiogroup"] label > div:first-child {{ display: none; }}
[data-testid="stSidebar"] [role="radiogroup"] label p {{ font-size: .95rem; font-weight: 500; }}
[data-testid="stSidebar"] hr {{ border-color: #1E2F48; }}
.sb-box {{ background: rgba(255,255,255,.04); border: 1px solid #1E2F48; border-radius: 14px; padding: 14px 16px; }}
.sb-box .k {{ font-size:.7rem; letter-spacing:.14em; text-transform:uppercase; color:{GOLD} !important; }}
.sb-box .v {{ font-family: var(--serif); font-size: 1.6rem; color: #fff !important; line-height: 1.2; }}
.sb-box .d {{ font-size: .82rem; color: #93A3BA !important; }}
.sb-team {{ font-size: .78rem; line-height: 1.7; color: #93A3BA !important; }}

/* ---------- typography ---------- */
.stApp h1, .stApp h2, .stApp h3 {{ font-family: var(--serif); color: var(--ink); font-weight: 400; letter-spacing: -.01em; }}
.eyebrow {{ font-size: .74rem; font-weight: 700; letter-spacing: .18em; text-transform: uppercase; color: var(--gold); }}
.ph {{ margin: 0 0 22px; }}
.ph h1 {{ font-size: 2.7rem; margin: 6px 0 6px; line-height: 1.05; text-wrap: balance; }}
.ph p {{ color: var(--muted); font-size: 1.05rem; max-width: 720px; margin: 0; }}
.sec {{ font-family: var(--serif); font-size: 1.55rem; margin: 30px 0 12px; color: var(--ink); }}

/* ---------- hero ---------- */
.hero {{ position: relative; overflow: hidden; border-radius: 26px; padding: 44px 46px 40px;
   background: radial-gradient(1200px 400px at 85% -10%, rgba(200,150,43,.28), transparent 60%),
               linear-gradient(135deg, {INK} 0%, {INK_2} 60%, #1C3354 100%);
   color: #fff; box-shadow: 0 24px 60px rgba(14,26,43,.28); margin-bottom: 26px; }}
.hero .eyebrow {{ color: #E4BF6A; }}
.hero h1 {{ font-family: var(--serif); color: #fff; font-size: 3.4rem; line-height: 1.02; margin: 12px 0 14px; font-weight: 400; max-width: 58%; }}
.hero h1 em {{ color: #E4BF6A; font-style: italic; }}
.hero p {{ color: #C9D5E6; font-size: 1.1rem; max-width: 56%; margin: 0; }}
.hero .art {{ position: absolute; right: 40px; top: 36px; width: 330px; max-width: 36%; opacity: .95; }}
.kpis {{ display: grid; grid-template-columns: repeat(4, minmax(0,1fr)); gap: 14px; margin-top: 30px; max-width: 100%; }}
.kpi {{ background: rgba(255,255,255,.06); border: 1px solid rgba(255,255,255,.12); border-radius: 16px; padding: 14px 16px; backdrop-filter: blur(6px); }}
.kpi .v {{ font-family: var(--serif); font-size: 1.9rem; color: #fff; line-height: 1; }}
.kpi .l {{ font-size: .78rem; color: #A9B8CD; margin-top: 6px; }}
@media (max-width: 900px) {{ .hero .art {{ display:none; }} .hero h1, .hero p {{ max-width: 100%; }} .kpis {{ grid-template-columns: repeat(2, minmax(0,1fr)); }} .hero h1 {{ font-size: 2.4rem; }} }}

/* ---------- cards ---------- */
.card {{ background: var(--card); border: 1px solid var(--line); border-radius: 20px; padding: 22px 22px 20px; height: 100%;
   box-shadow: 0 1px 2px rgba(14,26,43,.04), 0 10px 30px rgba(14,26,43,.05); transition: transform .18s ease, box-shadow .18s ease; color: var(--ink); }}
.card:hover {{ transform: translateY(-2px); box-shadow: 0 2px 4px rgba(14,26,43,.05), 0 18px 40px rgba(14,26,43,.09); }}
.card h4 {{ font-family: var(--serif); font-weight: 400; font-size: 1.3rem; margin: 10px 0 6px; color: var(--ink); }}
.card p {{ color: var(--muted); margin: 0; font-size: .95rem; line-height: 1.55; }}
.card .num {{ width: 34px; height: 34px; border-radius: 10px; display: grid; place-items: center; font-weight: 800; font-size: .9rem;
   background: var(--gold-soft); color: #8A6414; }}
.card .big {{ font-family: var(--serif); font-size: 2.6rem; color: var(--ink); line-height: 1; }}
.card .big.gold {{ color: var(--gold); }}
.card .cap {{ color: var(--muted); font-size: .9rem; margin-top: 6px; }}
.phase {{ background: var(--card); border: 1px solid var(--line); border-radius: 20px; padding: 20px; height: 100%; color: var(--ink); }}
.phase .tag {{ display:inline-block; font-size:.72rem; font-weight:800; letter-spacing:.12em; text-transform:uppercase; padding:4px 10px; border-radius:999px; }}
.phase h4 {{ font-family: var(--serif); font-weight:400; font-size:1.35rem; margin:12px 0 4px; color: var(--ink); }}
.phase p {{ color: var(--muted); margin:0; font-size:.93rem; }}
.phase .o {{ font-family: var(--mono); font-size:.85rem; color: var(--ink); margin-top:12px; background: var(--paper); display:inline-block; padding:4px 10px; border-radius:8px; }}

.stat {{ background: var(--card); border: 1px solid var(--line); border-radius: 18px; padding: 16px 18px; color: var(--ink); }}
.stat .l {{ font-size: .74rem; font-weight: 700; letter-spacing: .12em; text-transform: uppercase; color: var(--muted); }}
.stat .v {{ font-family: var(--serif); font-size: 2.1rem; line-height: 1.1; margin-top: 4px; color: var(--ink); font-variant-numeric: tabular-nums; }}

.note {{ background: var(--card); border: 1px solid var(--line); border-left: 4px solid var(--gold); border-radius: 14px; padding: 14px 18px; color: var(--ink); margin: 6px 0 14px; }}
.note b {{ color: var(--ink); }}
.banner {{ border-radius: 18px; padding: 18px 22px; display:flex; gap:16px; align-items:center; margin: 10px 0 16px; color: var(--ink); }}
.banner.gold {{ background: linear-gradient(135deg, #FBF4E3, #F6ECD6); border: 1px solid #EBD6A6; }}
.banner.good {{ background: #EAF6EF; border: 1px solid #BFE3CF; }}
.banner .ic {{ font-size: 1.9rem; }}
.banner .t {{ font-family: var(--serif); font-size: 1.35rem; color: var(--ink); }}
.banner .d {{ color: var(--muted); font-size: .93rem; }}

/* ---------- widgets ---------- */
.stButton > button, .stDownloadButton > button {{ border-radius: 12px; font-family: var(--sans); font-weight: 700; padding: .62rem 1.15rem;
   border: 1px solid var(--line); transition: all .15s ease; }}
.stButton > button[kind="primary"], .stDownloadButton > button[kind="primary"] {{ background: linear-gradient(135deg, {INK}, #22395C); border: 1px solid {INK}; color: #fff;
   box-shadow: 0 8px 20px rgba(14,26,43,.18); }}
.stButton > button[kind="primary"]:hover, .stDownloadButton > button[kind="primary"]:hover {{ border-color: var(--gold); box-shadow: 0 10px 26px rgba(200,150,43,.30); }}
.stButton > button[kind="secondary"]:hover {{ border-color: var(--gold); color: var(--ink); }}
.stTabs [data-baseweb="tab-list"] {{ gap: 6px; background: #EAEEF5; padding: 6px; border-radius: 14px; }}
.stTabs [data-baseweb="tab"] {{ border-radius: 10px; padding: 8px 16px; height: auto; }}
.stTabs [aria-selected="true"] {{ background: #fff; box-shadow: 0 2px 8px rgba(14,26,43,.08); }}
.stTabs [data-baseweb="tab-highlight"], .stTabs [data-baseweb="tab-border"] {{ display: none; }}
[data-testid="stDataFrame"] {{ border-radius: 14px; overflow: hidden; border: 1px solid var(--line); }}
[data-testid="stExpander"] {{ background: var(--card); border-radius: 14px; border: 1px solid var(--line); }}
[data-testid="stPlotlyChart"] {{ background: var(--card); border: 1px solid var(--line); border-radius: 20px; padding: 10px 8px 2px; }}
.stProgress > div > div > div > div {{ background: linear-gradient(90deg, {GOLD}, #E4BF6A); }}

/* ---------- bucket visual ---------- */
.lane-l {{ font-size:.74rem; font-weight:700; letter-spacing:.12em; text-transform:uppercase; color: var(--muted); margin: 14px 0 8px; }}
.chips {{ display:flex; flex-wrap:wrap; gap:6px; }}
.chip {{ display:inline-flex; align-items:center; gap:6px; padding:5px 10px; border-radius:10px; font-family: var(--mono); font-size:.82rem;
   background: var(--card); border:1px solid var(--line); color: var(--ink); transition: all .2s ease; }}
.chip .k {{ font-weight:700; padding:1px 7px; border-radius:6px; color:#fff; }}
.chip.cur {{ border-color: var(--gold); box-shadow: 0 0 0 3px rgba(200,150,43,.25); transform: translateY(-2px); }}
.chip.ghost {{ opacity:.28; }}
.chip.done {{ background: #F3FAF6; border-color: #BFE3CF; }}
.bwrap {{ display:grid; grid-template-columns: repeat(auto-fill, minmax(86px, 1fr)); gap:10px; }}
.bucket {{ position:relative; min-height:118px; border-radius: 6px 6px 18px 18px; padding: 30px 6px 8px; text-align:center;
   background: linear-gradient(180deg, #FFFFFF, #F1F4FA); border: 1px solid #D5DDEA; border-top: 4px solid #C9D3E3; }}
.bucket .lbl {{ position:absolute; top:6px; left:0; right:0; font-family: var(--mono); font-size:.75rem; font-weight:700; color: var(--muted); }}
.bucket .it {{ display:block; margin:4px auto; font-family: var(--mono); font-size:.74rem; padding:3px 6px; border-radius:7px; color:#fff; max-width: 100%;
   overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }}
.bucket.hot {{ border-color: var(--gold); border-top-color: var(--gold); box-shadow: 0 10px 24px rgba(200,150,43,.25); background: linear-gradient(180deg,#FFFDF7,#FBF2DE); }}
.bucket.read {{ border-color: #8CCBA9; border-top-color: var(--good); background: linear-gradient(180deg,#FBFFFD,#E8F6EE); }}
.timeline {{ display:flex; gap:8px; margin: 4px 0 14px; flex-wrap: wrap; }}
.timeline .st {{ flex:1; min-width: 120px; padding:10px 14px; border-radius:12px; background: var(--card); border:1px solid var(--line); font-size:.85rem; color: var(--muted); }}
.timeline .st b {{ display:block; font-family: var(--serif); font-weight:400; font-size:1.05rem; color: var(--ink); }}
.timeline .st.on {{ border-color: var(--gold); background: #FBF4E3; color: #8A6414; }}
.msg {{ background: var(--card); border:1px solid var(--line); border-radius: 14px; padding: 14px 18px; font-size: 1rem; color: var(--ink); }}

/* ---------- team ---------- */
.member {{ display:flex; gap:14px; align-items:center; background: var(--card); border:1px solid var(--line); border-radius:18px; padding:16px; color: var(--ink); }}
.member .av {{ width:48px; height:48px; border-radius:14px; display:grid; place-items:center; font-weight:800; color:#fff;
   background: linear-gradient(135deg, {INK}, #2A4A78); flex-shrink:0; }}
.member .n {{ font-weight:700; color: var(--ink); line-height:1.25; }}
.member .r {{ font-family: var(--mono); font-size:.8rem; color: var(--gold); }}
.foot {{ margin-top: 48px; padding-top: 18px; border-top: 1px solid var(--line); color: var(--muted); font-size: .85rem; display:flex; justify-content:space-between; flex-wrap:wrap; gap:8px; }}
</style>
""", unsafe_allow_html=True)

# =====================================================================  data
FIRST_NAMES = ["Ali", "Ahmed", "Sara", "Ayesha", "Hamza", "Fatima", "Usman", "Zainab", "Bilal", "Hira",
               "Omar", "Maryam", "Saad", "Iqra", "Hassan", "Amna", "Danish", "Noor", "Faizan", "Mahnoor",
               "Talha", "Areeba", "Rehan", "Laiba", "Shahzaib", "Kinza", "Arsalan", "Sana", "Junaid", "Hafsa"]

TEAM = [("Muhammad Abdul Rahman Khan", "25F-DS-106"), ("Muhammad Huzaifa Shamsi", "25F-DS-135"),
        ("Basit Mirza", "25F-DS-140"), ("Muhammad Hashir", "25F-DS-152")]

REPORT_A = [(1000, 0.31, 2.32, 1.61, 27.85, 0.08), (2000, 0.41, 3.77, 2.91, 91.45, 0.18),
            (5000, 0.73, 9.88, 5.93, 529.28, 0.63), (10000, 2.07, 18.56, 11.03, None, 1.27),
            (20000, 2.58, 48.18, 23.43, None, 2.74), (50000, 6.36, 114.42, 56.40, None, 9.24),
            (100000, 12.63, 240.43, 110.69, None, 14.85)]
REPORT_B = [(10, 0.94, 16.78), (100, 1.02, 17.21), (1000, 1.41, 19.39), (10000, 2.42, 18.65),
            (100000, 13.65, 23.16), (1000000, 175.81, 18.00)]

PAGES = ["Overview", "Make data", "Watch bucket-sort", "Race the algorithms",
         "Experiments & graphs", "Correctness tests", "Source code", "Team & report"]


def set_data(items, N, kind):
    st.session_state.data_items = items
    st.session_state.N = N
    st.session_state.kind = kind
    st.session_state.step = 0


if "data_items" not in st.session_state:
    rng = random.Random(7)
    set_data([(rng.randrange(10), f"S{i+1}") for i in range(10)], 10, "numbers")
if "page" not in st.session_state:
    st.session_state.page = PAGES[0]


def make_students(n, max_marks, seed=None):
    rng = random.Random(seed)
    return [(rng.randint(0, max_marks), f"{rng.choice(FIRST_NAMES)}-{i+1}") for i in range(n)]


def make_numbers(n, N, seed=None):
    rng = random.Random(seed)
    return [(rng.randrange(N), f"#{i+1}") for i in range(n)]


def items_df(items, key_name):
    return pd.DataFrame({"Position": range(1, len(items) + 1),
                         "Label": [lbl for _, lbl in items],
                         key_name: [k for k, _ in items]})


def key_name():
    return "Marks (key)" if st.session_state.kind == "students" else "Key"


def key_color(k, N):
    hue = int(215 + (k / max(N - 1, 1)) * 160) % 360
    return f"hsl({hue}, 58%, 46%)"


def page_header(eyebrow, title, sub):
    st.markdown(f'<div class="ph"><div class="eyebrow">{eyebrow}</div><h1>{title}</h1><p>{sub}</p></div>',
                unsafe_allow_html=True)


def stat(col, label, value):
    col.markdown(f'<div class="stat"><div class="l">{label}</div><div class="v">{value}</div></div>', unsafe_allow_html=True)


def go_to(name):
    st.session_state.page = name


def style_fig(fig, title, height=440, xtitle="", ytitle=""):
    fig.update_layout(
        title=dict(text=title, font=dict(family="DM Serif Display, Georgia, serif", size=20, color=INK), x=0.01, y=0.96),
        font=dict(family="Manrope, Segoe UI, sans-serif", color=INK, size=13),
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", height=height,
        margin=dict(t=70, l=60, r=24, b=56),
        legend=dict(orientation="h", yanchor="bottom", y=1.0, xanchor="right", x=1, bgcolor="rgba(0,0,0,0)"),
        hoverlabel=dict(bgcolor=INK, font=dict(color="#fff", family="Manrope")),
        xaxis=dict(title=xtitle, gridcolor="#EDF1F7", zerolinecolor=LINE, linecolor=LINE),
        yaxis=dict(title=ytitle, gridcolor="#EDF1F7", zerolinecolor=LINE, linecolor=LINE))
    return fig


# =====================================================================  bucket sort steps
def bucket_steps(items, N):
    steps = []
    B = [[] for _ in range(N)]
    snap = lambda: [list(b) for b in B]
    steps.append(dict(phase="start", cur=None, hot=None, read=None, buckets=snap(), out=[],
                      msg=f"We create <b>{N} empty buckets</b>, one for every possible key from 0 to {N-1}."))
    for idx, (k, lbl) in enumerate(items):
        B[k].append((k, lbl))
        steps.append(dict(phase="scatter", cur=idx, hot=k, read=None, buckets=snap(), out=[],
                          msg=f"Item <b>{lbl}</b> has key <b>{k}</b>, so it goes to the end of <b>bucket {k}</b>. No comparison is needed."))
    out = []
    for k in range(N):
        if B[k]:
            out.extend(B[k])
            steps.append(dict(phase="gather", cur=None, hot=None, read=k, buckets=snap(), out=list(out),
                              msg=f"Bucket <b>{k}</b> is read from front to back and its {len(B[k])} item(s) are copied to the sorted list."))
    steps.append(dict(phase="done", cur=None, hot=None, read=None, buckets=snap(), out=list(out),
                      msg="<b>Done.</b> The buckets were read in order 0, 1, 2 … so the list is sorted, and equal keys kept their original order (stable)."))
    return steps


def render_step(s, items, N):
    chips = []
    for idx, (k, lbl) in enumerate(items):
        cls = "chip"
        if s["phase"] == "scatter":
            cls += " cur" if idx == s["cur"] else (" ghost" if idx < s["cur"] else "")
        elif s["phase"] in ("gather", "done"):
            cls += " ghost"
        chips.append(f'<span class="{cls}">{lbl}<span class="k" style="background:{key_color(k, N)}">{k}</span></span>')
    html = '<div class="lane-l">Input list</div><div class="chips">' + "".join(chips) + "</div>"
    show = list(range(N)) if N <= 30 else [k for k in range(N) if s["buckets"][k]]
    note = f" · showing the {len(show)} non-empty buckets, the other {N-len(show)} are empty but still created and checked" if N > 30 else ""
    html += f'<div class="lane-l">Buckets{note}</div><div class="bwrap">'
    for k in show:
        cls = "bucket" + (" hot" if s["hot"] == k else "") + (" read" if s["read"] == k else "")
        inner = "".join(f'<span class="it" style="background:{key_color(kk, N)}">{lbl}</span>' for kk, lbl in s["buckets"][k])
        html += f'<div class="{cls}"><div class="lbl">B[{k}]</div>{inner}</div>'
    html += "</div>"
    out = "".join(f'<span class="chip done">{lbl}<span class="k" style="background:{key_color(k, N)}">{k}</span></span>' for k, lbl in s["out"])
    html += '<div class="lane-l">Sorted output</div><div class="chips">' + (out or '<span style="color:#8A97AB">Empty for now</span>') + "</div>"
    return html


def timeline(phase):
    names = [("start", "Create", "N empty buckets"), ("scatter", "Scatter", "items into buckets"),
             ("gather", "Gather", "buckets back to list"), ("done", "Done", "sorted and stable")]
    return '<div class="timeline">' + "".join(
        f'<div class="st{" on" if p == phase else ""}"><b>{t}</b>{d}</div>' for p, t, d in names) + "</div>"


# =====================================================================  sidebar
with st.sidebar:
    st.markdown('<div class="brand"><div class="logo">B</div><div><div class="t">Bucket Sort Lab</div>'
                '<div class="s">Project P-12.61</div></div></div>', unsafe_allow_html=True)
    st.write("")
    page = st.radio("Navigate", PAGES, key="page", label_visibility="collapsed")
    st.write("")
    items_sb, N_sb = st.session_state.data_items, st.session_state.N
    st.markdown(f'<div class="sb-box"><div class="k">Current data</div><div class="v">{len(items_sb):,} items</div>'
                f'<div class="d">keys from 0 to {N_sb - 1:,} · {N_sb:,} buckets</div></div>', unsafe_allow_html=True)
    st.write("")
    st.markdown('<div class="sb-team">Data Structures Lab · DUET<br>Submitted to Sir Jamal<br><br>'
                + "<br>".join(f"{n} · {r[-3:]}" for n, r in TEAM) + "</div>", unsafe_allow_html=True)


def footer():
    st.markdown('<div class="foot"><span>Bucket Sort Lab · P-12.61 · Data Structures Lab</span>'
                '<span>Goodrich, Tamassia &amp; Goldwasser, §12.4.2</span></div>', unsafe_allow_html=True)


# =====================================================================  pages
if page == "Overview":
    art = """<svg class="art" viewBox="0 0 380 210" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
      <g font-family="JetBrains Mono, monospace" font-size="12">
        <g fill="none" stroke="#E4BF6A" stroke-opacity=".55" stroke-width="2">
          <path d="M20 90 L20 180 Q20 196 36 196 L74 196 Q90 196 90 180 L90 90"/>
          <path d="M110 90 L110 180 Q110 196 126 196 L164 196 Q180 196 180 180 L180 90"/>
          <path d="M200 90 L200 180 Q200 196 216 196 L254 196 Q270 196 270 180 L270 90"/>
          <path d="M290 90 L290 180 Q290 196 306 196 L344 196 Q360 196 360 180 L360 90"/>
        </g>
        <g fill="#C9D5E6" fill-opacity=".8"><text x="44" y="80">B[0]</text><text x="134" y="80">B[1]</text><text x="224" y="80">B[2]</text><text x="314" y="80">B[3]</text></g>
        <g><rect x="30" y="160" width="50" height="24" rx="6" fill="#4F7BE8"/><rect x="30" y="130" width="50" height="24" rx="6" fill="#4F7BE8"/>
           <rect x="120" y="160" width="50" height="24" rx="6" fill="#3FA3A0"/>
           <rect x="210" y="160" width="50" height="24" rx="6" fill="#8C6BE8"/>
           <rect x="300" y="160" width="50" height="24" rx="6" fill="#C8962B"/><rect x="300" y="130" width="50" height="24" rx="6" fill="#C8962B"/><rect x="300" y="100" width="50" height="24" rx="6" fill="#C8962B"/></g>
        <g fill="#fff"><text x="51" y="177">0</text><text x="51" y="147">0</text><text x="141" y="177">1</text><text x="231" y="177">2</text><text x="321" y="177">3</text><text x="321" y="147">3</text><text x="321" y="117">3</text></g>
        <g fill="#E4BF6A"><rect x="150" y="14" width="80" height="28" rx="8" fill-opacity=".18" stroke="#E4BF6A"/><text x="166" y="33" fill="#fff">key 3</text></g>
        <path d="M230 34 C 290 34, 325 50, 325 92" stroke="#E4BF6A" stroke-width="2" fill="none" stroke-dasharray="4 5"/>
      </g></svg>"""
    st.markdown(f"""<div class="hero">{art}
      <div class="eyebrow">Data Structures Lab · Project P-12.61</div>
      <h1>Sorting without a single <em>comparison</em>.</h1>
      <p>Bucket-sort for integer keys in the range [0, N−1], running in O(n + N) time. Make your own data, watch every item drop into its bucket, and race it against the classics.</p>
      <div class="kpis">
        <div class="kpi"><div class="v">O(n+N)</div><div class="l">running time</div></div>
        <div class="kpi"><div class="v">19×</div><div class="l">faster than merge sort at n = 100k</div></div>
        <div class="kpi"><div class="v">4 / 4</div><div class="l">correctness tests passed</div></div>
        <div class="kpi"><div class="v">5</div><div class="l">algorithms compared</div></div>
      </div></div>""", unsafe_allow_html=True)

    st.markdown('<div class="sec">How bucket-sort works</div>', unsafe_allow_html=True)
    a, b, c = st.columns(3, gap="medium")
    a.markdown('<div class="phase"><span class="tag" style="background:#E8EEFD;color:#2F5BEA">Step 1 · Create</span>'
               '<h4>N empty buckets</h4><p>One bucket for every possible key, B[0] to B[N−1].</p><span class="o">O(N)</span></div>', unsafe_allow_html=True)
    b.markdown('<div class="phase"><span class="tag" style="background:#FBF0D9;color:#8A6414">Step 2 · Scatter</span>'
               '<h4>Drop each item in</h4><p>Each entry goes to the end of the bucket that matches its key.</p><span class="o">O(n)</span></div>', unsafe_allow_html=True)
    c.markdown('<div class="phase"><span class="tag" style="background:#E3F4EA;color:#1F8A5B">Step 3 · Gather</span>'
               '<h4>Read buckets in order</h4><p>Buckets 0 to N−1 are emptied back into the list, already sorted.</p><span class="o">O(n + N)</span></div>', unsafe_allow_html=True)

    st.markdown('<div class="sec">Explore the lab</div>', unsafe_allow_html=True)
    tiles = [("Make data", "Student marks, random numbers, your own list or a CSV file. One click."),
             ("Watch bucket-sort", "An animated, step-by-step view of scatter and gather."),
             ("Race the algorithms", "Bucket, merge, quick, insertion and Python's sorted() on the same data."),
             ("Experiments & graphs", "The two experiments from our report, live or from saved results."),
             ("Correctness tests", "The four automated tests, run with one button."),
             ("Source code", "The exact program used in the project, ready to download.")]
    for row in range(2):
        cols = st.columns(3, gap="medium")
        for j, col in enumerate(cols):
            i = row * 3 + j
            t, d = tiles[i]
            with col:
                st.markdown(f'<div class="card"><div class="num">{i+1}</div><h4>{t}</h4><p>{d}</p></div>', unsafe_allow_html=True)
                st.button(f"Open {t.lower()}", key=f"open{i}", on_click=go_to, args=(PAGES[i + 1],), width="stretch")
    footer()


elif page == "Make data":
    page_header("Step 1 · Prepare", "Make data", "Create the list that every other page will sort. No code needed, pick a preset or build your own.")
    st.markdown('<div class="sec" style="margin-top:6px">Quick presets</div>', unsafe_allow_html=True)
    presets = [("Small class", "15 students, marks 0–20", lambda: set_data(make_students(15, 20), 21, "students")),
               ("Twelve numbers", "12 keys from 0 to 9", lambda: set_data(make_numbers(12, 10), 10, "numbers")),
               ("Full class", "60 students, marks 0–100", lambda: set_data(make_students(60, 100), 101, "students")),
               ("Big data", "10,000 keys from 0 to 999", lambda: set_data(make_numbers(10000, 1000), 1000, "numbers"))]
    cols = st.columns(4, gap="medium")
    for col, (t, d, fn) in zip(cols, presets):
        with col:
            st.markdown(f'<div class="card"><h4 style="margin-top:0">{t}</h4><p>{d}</p></div>', unsafe_allow_html=True)
            if st.button(f"Use {t.lower()}", key=f"pre_{t}", width="stretch"):
                fn(); st.rerun()

    st.markdown('<div class="sec">Build your own</div>', unsafe_allow_html=True)
    t1, t2, t3, t4 = st.tabs(["Student marks", "Random numbers", "Type numbers", "Upload CSV"])
    with t1:
        c1, c2 = st.columns(2, gap="large")
        n = c1.slider("How many students?", 2, 2000, 20)
        mx = c2.slider("Total marks of the paper (marks go from 0 to this)", 1, 1000, 50)
        if st.button("Generate students", type="primary"):
            set_data(make_students(n, mx), mx + 1, "students"); st.rerun()
    with t2:
        c1, c2 = st.columns(2, gap="large")
        n = c1.number_input("How many numbers (n)?", 1, 200000, 25, step=1)
        N = c2.number_input("Key range N (numbers will be 0 to N−1)", 2, 1000000, 10, step=1)
        if st.button("Generate numbers", type="primary"):
            set_data(make_numbers(int(n), int(N)), int(N), "numbers"); st.rerun()
    with t3:
        txt = st.text_input("Type whole numbers separated by spaces or commas", "4 1 3 1 0 4 2")
        if st.button("Use these numbers", type="primary"):
            try:
                vals = [int(x) for x in txt.replace(",", " ").split()]
                if not vals or min(vals) < 0:
                    st.error("Type at least one number, and no negative numbers.")
                else:
                    set_data([(v, f"#{i+1}") for i, v in enumerate(vals)], max(max(vals) + 1, 2), "numbers"); st.rerun()
            except ValueError:
                st.error("Only whole numbers, for example 4 1 3 0.")
    with t4:
        st.caption("A CSV file with two columns: **name** and **key** (key is a whole number, 0 or more).")
        st.download_button("Download a sample CSV", "name,key\nAli,78\nSara,91\nHamza,78\nAyesha,85\n", "sample.csv")
        up = st.file_uploader("Upload CSV", type="csv")
        if up is not None:
            try:
                df = pd.read_csv(up)
                df.columns = [c.strip().lower() for c in df.columns]
                keys = df["key"].astype(int).tolist()
                if min(keys) < 0:
                    st.error("Keys must be 0 or more.")
                elif st.button("Use this file", type="primary"):
                    set_data(list(zip(keys, df["name"].astype(str))), max(max(keys) + 1, 2), "students"); st.rerun()
            except Exception:
                st.error("Could not read the file. It needs the columns 'name' and 'key'.")

    items, N = st.session_state.data_items, st.session_state.N
    st.markdown('<div class="sec">Your data</div>', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4, gap="medium")
    used = len(set(k for k, _ in items))
    stat(m1, "Items (n)", f"{len(items):,}")
    stat(m2, "Buckets (N)", f"{N:,}")
    stat(m3, "Keys in use", f"{used:,}")
    stat(m4, "Empty buckets", f"{N - used:,}")
    st.write("")
    left, right = st.columns([5, 7], gap="medium")
    with left:
        st.dataframe(items_df(items[:1000], key_name()), width="stretch", hide_index=True, height=360)
        if len(items) > 1000:
            st.caption("Showing the first 1,000 rows.")
    with right:
        counts = [0] * N
        for k, _ in items:
            counts[k] += 1
        fig = go.Figure(go.Bar(x=list(range(N)), y=counts, marker_color=GOLD, marker_line_width=0,
                               hovertemplate="Key %{x}: %{y} item(s)<extra></extra>"))
        st.plotly_chart(style_fig(fig, "How the keys are spread", 360, "Key", "Items"), width="stretch")
    footer()


elif page == "Watch bucket-sort":
    page_header("Step 2 · Visualise", "Watch bucket-sort", "Every item drops into the bucket with its key, then the buckets are read back in order. Press play, or drag the slider.")
    items, N = st.session_state.data_items, st.session_state.N
    if len(items) > 40 or N > 200:
        st.markdown(f'<div class="note">Your data has <b>{len(items):,} items</b> and <b>{N:,} buckets</b>, too many to animate one by one. '
                    'Below is how full each bucket is after sorting. For the animation, choose a small preset on <b>Make data</b>.</div>', unsafe_allow_html=True)
        sorted_items = bucket_sort(list(items), N, key=lambda e: e[0])
        counts = [0] * N
        for k, _ in items:
            counts[k] += 1
        empty = counts.count(0)
        a, b, c = st.columns(3, gap="medium")
        stat(a, "Buckets filled", f"{N - empty:,}")
        stat(b, "Buckets empty", f"{empty:,}")
        stat(c, "Largest bucket", f"{max(counts):,}")
        st.write("")
        fig = go.Figure(go.Bar(x=list(range(N)), y=counts, marker_color=GOLD, marker_line_width=0,
                               hovertemplate="Bucket %{x}: %{y} item(s)<extra></extra>"))
        st.plotly_chart(style_fig(fig, "Items in each bucket", 380, "Bucket (key)", "Items"), width="stretch")
        st.caption("Empty buckets are still created and checked. That is the “+N” in O(n + N).")
        st.dataframe(items_df(sorted_items[:1000], key_name()), width="stretch", hide_index=True, height=280)
    else:
        steps = bucket_steps(items, N)
        c1, c2, c3 = st.columns([1.2, 1, 4], gap="medium")
        play = c1.button("▶  Play", type="primary", width="stretch")
        if c2.button("Reset", width="stretch"):
            st.session_state.step = 0
        speed = c3.select_slider("Speed", ["Slow", "Normal", "Fast"], value="Normal", label_visibility="collapsed")
        delay = {"Slow": 1.2, "Normal": 0.6, "Fast": 0.25}[speed]
        st.session_state.step = min(st.session_state.get("step", 0), len(steps) - 1)
        k = st.slider(f"Step (of {len(steps) - 1})", 0, len(steps) - 1, st.session_state.step)
        st.session_state.step = k
        tl, msg_box, view = st.empty(), st.empty(), st.empty()

        def show(i):
            s = steps[i]
            tl.markdown(timeline(s["phase"]), unsafe_allow_html=True)
            msg_box.markdown(f'<div class="msg">{s["msg"]}</div>', unsafe_allow_html=True)
            view.markdown(render_step(s, items, N), unsafe_allow_html=True)

        if play:
            for i in range(k, len(steps)):
                show(i)
                time.sleep(delay)
            st.session_state.step = len(steps) - 1
        else:
            show(k)

        st.write("")
        with st.expander("What is happening in the code?"):
            st.code("""B = [[] for _ in range(N)]        # Step 1: N empty buckets      O(N)
for e in entries:                  # Step 2: scatter              O(n)
    B[key(e)].append(e)
i = 0
for bucket in B:                   # Step 3: gather               O(n + N)
    for e in bucket:
        entries[i] = e
        i += 1""", language="python")
    footer()


elif page == "Race the algorithms":
    page_header("Step 3 · Compare", "Race the algorithms", "Every algorithm sorts the same keys. Each runs three times and keeps its best time.")
    items, N = st.session_state.data_items, st.session_state.N
    keys = [k for k, _ in items]
    a, b, c = st.columns(3, gap="medium")
    stat(a, "Keys to sort", f"{len(keys):,}")
    stat(b, "Key range", f"0 – {N - 1:,}")
    stat(c, "Insertion sort", "included" if len(keys) <= 5000 else "skipped")
    st.write("")
    if len(keys) < 1000:
        st.markdown('<div class="note">The current data is very small, so every algorithm finishes in a fraction of a millisecond. '
                    'Load bigger data for a clear result.</div>', unsafe_allow_html=True)
        if st.button("Load 20,000 random keys (0–999)"):
            set_data(make_numbers(20000, 1000), 1000, "numbers"); st.rerun()
    use_ins = len(keys) <= 5000
    if st.button("Start the race", type="primary"):
        algos = {"Bucket sort": lambda arr: bucket_sort(arr, N, key=lambda x: x), "Merge sort": merge_sort,
                 "Quick sort": quick_sort, "Python sorted()": sorted}
        if use_ins:
            algos["Insertion sort"] = insertion_sort
        res, ok = {}, {}
        expected = sorted(keys)
        bar = st.progress(0.0, text="Racing…")
        for i, (name, f) in enumerate(algos.items()):
            res[name] = time_it(f, keys, repeats=1 if name == "Insertion sort" else 3) * 1000
            ok[name] = f(keys[:]) == expected
            bar.progress((i + 1) / len(algos), text=f"{name} finished")
        bar.empty()
        st.session_state.race = (res, ok, len(keys))
    if "race" in st.session_state:
        res, ok, nkeys = st.session_state.race
        order = sorted(res, key=res.get)
        best = order[0]
        st.markdown(f'<div class="banner gold"><div class="ic">🏆</div><div><div class="t">{best} wins in {res[best]:.2f} ms</div>'
                    f'<div class="d">Race on {nkeys:,} keys. All results were checked against Python\'s sorted().</div></div></div>', unsafe_allow_html=True)
        if "Bucket sort" in res:
            cols = st.columns(2, gap="medium")
            for col, other in zip(cols, ("Merge sort", "Quick sort")):
                x = res[other] / max(res["Bucket sort"], 1e-9)
                col.markdown(f'<div class="card"><div class="big gold">{x:.1f}×</div><div class="cap">bucket sort vs {other.lower()} on this data</div></div>', unsafe_allow_html=True)
            st.write("")
        fig = go.Figure(go.Bar(x=[res[a] for a in order], y=order, orientation="h",
                               marker=dict(color=[COLORS[a] for a in order]),
                               text=[f"{res[a]:.2f} ms" for a in order], textposition="outside",
                               hovertemplate="%{y}: %{x:.3f} ms<extra></extra>"))
        style_fig(fig, "Running time, lower is better", 380, "Time (ms)")
        fig.update_layout(yaxis=dict(autorange="reversed", title=""), showlegend=False)
        st.plotly_chart(fig, width="stretch")
        st.dataframe(pd.DataFrame({"Rank": range(1, len(order) + 1), "Algorithm": order,
                                   "Time (ms)": [f"{res[a]:.3f}" for a in order],
                                   "Correct result": ["Yes" if ok[a] else "No" for a in order]}),
                     hide_index=True, width="stretch")
        st.caption("Python's sorted() is written in C, so it is very fast. All the others are plain Python.")
    footer()


elif page == "Experiments & graphs":
    page_header("Step 4 · Measure", "Experiments & graphs", "The two experiments from our report. View the saved results instantly, or run them live.")
    mode = st.radio("Data source", ["Results from our report", "Run live now"], horizontal=True, label_visibility="collapsed")

    def fig_a(rows):
        n = [r[0] for r in rows]
        fig = go.Figure()
        for idx, name, sym in [(1, "Bucket sort", "circle"), (2, "Merge sort", "square"), (3, "Quick sort", "triangle-up")]:
            fig.add_trace(go.Scatter(x=n, y=[r[idx] for r in rows], mode="lines+markers", name=name,
                                     line=dict(color=COLORS[name], width=4 if idx == 1 else 2.2, shape="spline"),
                                     marker=dict(symbol=sym, size=9, line=dict(width=2, color="#fff"))))
        ins = [(r[0], r[4]) for r in rows if r[4] is not None]
        if ins:
            fig.add_trace(go.Scatter(x=[x for x, _ in ins], y=[y for _, y in ins], mode="lines+markers", name="Insertion sort",
                                     line=dict(color=COLORS["Insertion sort"], dash="dash"), marker=dict(symbol="x", size=9)))
        style_fig(fig, "Running time vs n (N = 1000)", 460, "Number of entries n", "Time (ms)")
        fig.update_layout(yaxis_range=[0, max(r[2] for r in rows) * 1.15], hovermode="x unified")
        return fig

    def fig_b(rows):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[r[0] for r in rows], y=[r[1] for r in rows], mode="lines+markers", name="Bucket sort",
                                 line=dict(color=COLORS["Bucket sort"], width=4), marker=dict(size=10, line=dict(width=2, color="#fff"))))
        fig.add_trace(go.Scatter(x=[r[0] for r in rows], y=[r[2] for r in rows], mode="lines+markers", name="Merge sort",
                                 line=dict(color=COLORS["Merge sort"], width=2.2), marker=dict(symbol="square", size=9, line=dict(width=2, color="#fff"))))
        style_fig(fig, "Running time vs key range N (n = 10,000)", 460, "Key range N (log scale)", "Time (ms)")
        fig.update_layout(xaxis_type="log", hovermode="x unified")
        return fig

    rows_a, rows_b = REPORT_A, REPORT_B
    if mode == "Run live now":
        c1, c2 = st.columns(2, gap="large")
        sizes = c1.multiselect("Values of n for Experiment A", [1000, 2000, 5000, 10000, 20000, 50000, 100000],
                               default=[1000, 2000, 5000, 10000, 20000, 50000])
        Ns = c2.multiselect("Values of N for Experiment B", [10, 100, 1000, 10000, 100000, 1000000],
                            default=[10, 100, 1000, 10000, 100000, 1000000])
        st.caption("Bigger values give clearer results but take longer, up to about a minute.")
        if st.button("Run both experiments", type="primary"):
            random.seed(42)
            bar = st.progress(0.0, text="Starting…")
            total, done = max(len(sizes) + len(Ns), 1), 0
            rows_a = []
            for n in sorted(sizes):
                bar.progress(done / total, text=f"Experiment A · n = {n:,}")
                data = [random.randrange(1000) for _ in range(n)]
                tb = time_it(lambda arr: bucket_sort(arr, 1000, key=lambda x: x), data) * 1000
                tm = time_it(merge_sort, data) * 1000
                tq = time_it(quick_sort, data) * 1000
                ti = time_it(insertion_sort, data, repeats=1) * 1000 if n <= 5000 else None
                ts = time_it(sorted, data) * 1000
                rows_a.append((n, tb, tm, tq, ti, ts))
                done += 1
            rows_b = []
            for N in sorted(Ns):
                bar.progress(done / total, text=f"Experiment B · N = {N:,}")
                data = [random.randrange(N) for _ in range(10000)]
                tb = time_it(lambda arr, N=N: bucket_sort(arr, N, key=lambda x: x), data) * 1000
                tm = time_it(merge_sort, data) * 1000
                rows_b.append((N, tb, tm))
                done += 1
            bar.empty()
            st.session_state.live = (rows_a, rows_b)
        if "live" in st.session_state:
            rows_a, rows_b = st.session_state.live
            st.markdown('<div class="banner good"><div class="ic">✓</div><div><div class="t">Live results</div>'
                        '<div class="d">The graphs below come from the run you just made.</div></div></div>', unsafe_allow_html=True)
        else:
            st.markdown('<div class="note">Press <b>Run both experiments</b>. Until then the saved report results are shown.</div>', unsafe_allow_html=True)

    tabA, tabB = st.tabs(["Experiment A · grow n", "Experiment B · grow N"])
    with tabA:
        if rows_a:
            last = rows_a[-1]
            a, b, c = st.columns(3, gap="medium")
            a.markdown(f'<div class="card"><div class="big gold">{last[2]/last[1]:.0f}×</div><div class="cap">faster than merge sort at n = {last[0]:,}</div></div>', unsafe_allow_html=True)
            b.markdown(f'<div class="card"><div class="big">{last[3]/last[1]:.0f}×</div><div class="cap">faster than quick sort at n = {last[0]:,}</div></div>', unsafe_allow_html=True)
            c.markdown(f'<div class="card"><div class="big">{last[1]:.1f} ms</div><div class="cap">bucket sort on {last[0]:,} keys</div></div>', unsafe_allow_html=True)
            st.write("")
            st.plotly_chart(fig_a(rows_a), width="stretch")
            st.dataframe(pd.DataFrame([{"n": f"{r[0]:,}", "Bucket (ms)": f"{r[1]:.2f}", "Merge (ms)": f"{r[2]:.2f}", "Quick (ms)": f"{r[3]:.2f}",
                                        "Insertion (ms)": "skipped" if r[4] is None else f"{r[4]:.2f}", "sorted() (ms)": f"{r[5]:.2f}"} for r in rows_a]),
                         hide_index=True, width="stretch")
            st.markdown('<div class="note"><b>What this shows.</b> The gold bucket-sort line stays at the bottom and grows like a straight line, '
                        'which is linear O(n). Merge and quick sort climb like O(n log n). Insertion sort shoots off the top, the O(n²) pattern, '
                        'so it is skipped after 5,000.</div>', unsafe_allow_html=True)
    with tabB:
        if rows_b:
            big = rows_b[-1]
            a, b = st.columns(2, gap="medium")
            a.markdown(f'<div class="card"><div class="big">{big[1]/big[2]:.0f}×</div><div class="cap">slower than merge sort at N = {big[0]:,}</div></div>', unsafe_allow_html=True)
            b.markdown(f'<div class="card"><div class="big gold">{big[0]:,}</div><div class="cap">buckets created for only 10,000 entries</div></div>', unsafe_allow_html=True)
            st.write("")
            st.plotly_chart(fig_b(rows_b), width="stretch")
            st.dataframe(pd.DataFrame([{"N": f"{r[0]:,}", "Bucket (ms)": f"{r[1]:.2f}", "Merge (ms)": f"{r[2]:.2f}",
                                        "Faster": "Bucket" if r[1] < r[2] else "Merge"} for r in rows_b]),
                         hide_index=True, width="stretch")
            st.markdown('<div class="note"><b>What this shows.</b> Merge sort stays flat because it only compares keys. Bucket sort is fast while N is '
                        'close to n, but with a huge N it must create and check mostly empty buckets. The “+N” in O(n + N) is a real cost.</div>', unsafe_allow_html=True)
    footer()


elif page == "Correctness tests":
    page_header("Step 5 · Verify", "Correctness tests", "The same four checks that run in our program. Each one must pass.")
    if st.button("Run all tests", type="primary"):
        data = [Entry(3, "c1"), Entry(0, "a"), Entry(3, "c2"), Entry(1, "b"), Entry(2, "x"), Entry(0, "a2"), Entry(3, "c3")]
        before = repr(data)
        bucket_sort(data, 4)
        t1 = [e.key for e in data] == [0, 0, 1, 2, 3, 3, 3] and [e.value for e in data if e.key == 3] == ["c1", "c2", "c3"]
        t2 = True
        for _ in range(200):
            N = random.randint(2, 50); n = random.randint(0, 100)
            nums = [random.randrange(N) for _ in range(n)]
            t2 &= bucket_sort(nums[:], N, key=lambda x: x) == sorted(nums)
        cases = [([], 5, []), ([4], 5, [4]), ([1, 1, 1], 2, [1, 1, 1]), ([4, 3, 2, 1, 0], 5, [0, 1, 2, 3, 4]), ([0, 1, 2, 3], 4, [0, 1, 2, 3])]
        t3 = all(bucket_sort(list(a), N, key=lambda x: x) == exp for a, N, exp in cases)
        t4 = True
        for a, N in ([[5], 5], [[-1], 5], [[0], 1]):
            try:
                bucket_sort(a, N, key=lambda x: x); t4 = False
            except ValueError:
                pass
        st.session_state.tests = (t1, t2, t3, t4, before, repr(data))
    tests = st.session_state.get("tests")
    info = [("Small example and stability", "Seven entries are sorted, and c1, c2, c3 (all key 3) keep their order."),
            ("200 random lists", "Random n and N each time, compared with Python's sorted()."),
            ("Edge cases", "Empty list, one item, all equal, reversed and already sorted."),
            ("Wrong input", "Key equal to N, a negative key and N = 1 must raise ValueError.")]
    if tests:
        passed = sum(tests[:4])
        cls = "good" if passed == 4 else "gold"
        st.markdown(f'<div class="banner {cls}"><div class="ic">{"✓" if passed == 4 else "!"}</div><div><div class="t">{passed} of 4 tests passed</div>'
                    '<div class="d">Every check uses the real bucket_sort() function from bucket_sort.py.</div></div></div>', unsafe_allow_html=True)
    cols = st.columns(2, gap="medium")
    for i, (t, d) in enumerate(info):
        if tests is None:
            pill = '<span class="tag" style="background:#EEF1F6;color:#5B6B82">Not run yet</span>'
        elif tests[i]:
            pill = '<span class="tag" style="background:#E3F4EA;color:#1F8A5B">Passed</span>'
        else:
            pill = '<span class="tag" style="background:#FBE4E8;color:#C2415B">Failed</span>'
        with cols[i % 2]:
            st.markdown(f'<div class="phase" style="margin-bottom:14px">{pill}<h4>Test {i+1} · {t}</h4><p>{d}</p></div>', unsafe_allow_html=True)
    if tests:
        st.code(f"Before : {tests[4]}\nAfter  : {tests[5]}", language="text")
        if all(tests[:4]) and not st.session_state.get("ballooned"):
            st.session_state.ballooned = True
            st.balloons()
    footer()


elif page == "Source code":
    page_header("Step 6 · Read", "Source code", "The exact program used in the project. This app imports and runs these same functions.")
    src = open("bucket_sort.py", encoding="utf-8").read()
    a, b, c = st.columns(3, gap="medium")
    stat(a, "Lines of code", f"{len(src.splitlines())}")
    stat(b, "Functions", f"{src.count(chr(10) + 'def ')}")
    stat(c, "Main algorithm", "bucket_sort()")
    st.write("")
    st.download_button("Download bucket_sort.py", src, "bucket_sort.py", type="primary")
    st.write("")
    parts = {"bucket_sort() · the main algorithm": "def bucket_sort", "Entry · the data structure": "class Entry",
             "insertion_sort()": "def insertion_sort", "merge_sort()": "def merge_sort", "quick_sort()": "def quick_sort",
             "time_it() · the stopwatch": "def time_it"}
    lines = src.split("\n")
    for title, start in parts.items():
        with st.expander(title, expanded=title.startswith("bucket")):
            i = next(j for j, l in enumerate(lines) if l.startswith(start))
            j = i + 1
            while j < len(lines) and (lines[j].startswith(" ") or lines[j] == ""):
                j += 1
            st.code("\n".join(lines[i:j]).rstrip(), language="python")
    with st.expander("Full program"):
        st.code(src, language="python", line_numbers=True)
    footer()


else:
    page_header("About the project", "Team & report", "P-12.61 · Design and implement a version of the bucket-sort algorithm for sorting a list of n entries "
                "with integer keys taken from the range [0, N−1], for N ≥ 2. The algorithm should run in O(n + N) time.")
    cols = st.columns(2, gap="medium")
    for i, (n, r) in enumerate(TEAM):
        initials = n.split()[0][0] + n.split()[1][0]
        cols[i % 2].markdown(f'<div class="member" style="margin-bottom:12px"><div class="av">{initials}</div>'
                             f'<div><div class="n">{n}</div><div class="r">{r}</div></div></div>', unsafe_allow_html=True)
    st.markdown('<div class="sec">Course</div>', unsafe_allow_html=True)
    st.markdown('<div class="note">Data Structures Lab · Dawood University of Engineering &amp; Technology · Submitted to <b>Sir Jamal</b></div>', unsafe_allow_html=True)
    try:
        with open("Bucket_Sort_Project_Report.pdf", "rb") as f:
            st.download_button("Download the full project report (PDF)", f.read(), "Bucket_Sort_Project_Report.pdf",
                               "application/pdf", type="primary")
    except FileNotFoundError:
        pass
    st.markdown('<div class="sec">References</div>', unsafe_allow_html=True)
    st.markdown("""
1. Goodrich, M. T., Tamassia, R., & Goldwasser, M. H. (2013). *Data Structures and Algorithms in Python*. Wiley. Section 12.4.2.
2. [Python documentation · time.perf_counter()](https://docs.python.org/3/library/time.html#time.perf_counter)
3. [Python documentation · random](https://docs.python.org/3/library/random.html)
4. [Streamlit documentation](https://docs.streamlit.io) · [Plotly for Python](https://plotly.com/python/)
""")
    footer()
