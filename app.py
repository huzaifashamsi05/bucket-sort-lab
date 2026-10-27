import random
import time

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from bucket_sort import (Entry, bucket_sort, insertion_sort, merge_sort,
                         quick_sort, time_it)

st.set_page_config(page_title="Bucket Sort Lab — P-12.61", page_icon="🪣", layout="wide")

# ------------------------------------------------------------------ styling
st.markdown("""
<style>
.block-container {padding-top: 1.6rem; max-width: 1200px;}
.hero {background: linear-gradient(120deg,#1F4E79,#2E75B6); color:#fff; padding:28px 32px; border-radius:16px; margin-bottom:18px;}
.hero h1 {color:#fff; margin:0 0 6px 0; font-size:2.1rem;}
.hero p {color:#e8f1fb; margin:0; font-size:1.05rem;}
.card {border:1px solid #d9e2ec; border-radius:12px; padding:16px 18px; background:#fbfcfe; height:100%;}
.card h4 {margin:0 0 6px 0; color:#1F4E79;}
.step {display:inline-block; background:#1F4E79; color:#fff; border-radius:50%; width:28px; height:28px; text-align:center; line-height:28px; font-weight:700; margin-right:8px;}
.chip {display:inline-block; padding:4px 9px; margin:3px; border-radius:6px; background:#eef2f7; border:1px solid #c9d4e0; font-family:monospace; font-size:0.95rem;}
.chip.cur {background:#ffd27f; border-color:#e69500; font-weight:700;}
.chip.done {background:#cfe8d5; border-color:#7bbf8e;}
.chip.ghost {opacity:0.35;}
.bwrap {display:flex; flex-wrap:wrap; gap:8px; margin:6px 0 10px 0;}
.bucket {min-width:74px; flex:1 1 74px; max-width:120px; border:2px solid #2E75B6; border-top:none; border-radius:0 0 10px 10px; background:#f4f9ff; min-height:90px; padding:4px; text-align:center;}
.bucket.hot {border-color:#e69500; background:#fff7e6;}
.bucket.read {border-color:#2e8b57; background:#eaf7ee;}
.bucket .lbl {font-weight:700; color:#1F4E79; font-size:0.85rem; border-bottom:1px dashed #9ab; margin-bottom:4px;}
.msg {background:#fff7e6; border-left:5px solid #e69500; padding:10px 14px; border-radius:6px; margin:8px 0; font-size:1.02rem;}
.small {color:#5a6475; font-size:0.9rem;}
</style>
""", unsafe_allow_html=True)

FIRST_NAMES = ["Ali", "Ahmed", "Sara", "Ayesha", "Hamza", "Fatima", "Usman", "Zainab", "Bilal", "Hira",
               "Omar", "Maryam", "Saad", "Iqra", "Hassan", "Amna", "Danish", "Noor", "Faizan", "Mahnoor",
               "Talha", "Areeba", "Rehan", "Laiba", "Shahzaib", "Kinza", "Arsalan", "Sana", "Junaid", "Hafsa"]

COLORS = {"Bucket sort": "#1f77b4", "Merge sort": "#ff7f0e", "Quick sort": "#2ca02c",
          "Insertion sort": "#d62728", "Python sorted()": "#9467bd"}

REPORT_A = [(1000, 0.31, 2.32, 1.61, 27.85, 0.08), (2000, 0.41, 3.77, 2.91, 91.45, 0.18),
            (5000, 0.73, 9.88, 5.93, 529.28, 0.63), (10000, 2.07, 18.56, 11.03, None, 1.27),
            (20000, 2.58, 48.18, 23.43, None, 2.74), (50000, 6.36, 114.42, 56.40, None, 9.24),
            (100000, 12.63, 240.43, 110.69, None, 14.85)]
REPORT_B = [(10, 0.94, 16.78), (100, 1.02, 17.21), (1000, 1.41, 19.39), (10000, 2.42, 18.65),
            (100000, 13.65, 23.16), (1000000, 175.81, 18.00)]


# ------------------------------------------------------------------ state
def set_data(items, N, kind):
    st.session_state.data_items = items
    st.session_state.N = N
    st.session_state.kind = kind
    st.session_state.step = 0


if "data_items" not in st.session_state:
    rng = random.Random(7)
    set_data([(rng.randrange(10), f"S{i+1}") for i in range(10)], 10, "numbers")


def make_students(n, max_marks, seed=None):
    rng = random.Random(seed)
    items = []
    for i in range(n):
        name = rng.choice(FIRST_NAMES)
        items.append((rng.randint(0, max_marks), f"{name}-{i+1}"))
    return items


def make_numbers(n, N, seed=None):
    rng = random.Random(seed)
    return [(rng.randrange(N), f"#{i+1}") for i in range(n)]


def items_df(items, key_name):
    return pd.DataFrame({"Position": range(1, len(items) + 1),
                         "Label": [lbl for _, lbl in items],
                         key_name: [k for k, _ in items]})


def key_name():
    return "Marks (key)" if st.session_state.kind == "students" else "Key"


# ------------------------------------------------------------------ bucket sort steps (for the animation)
def bucket_steps(items, N):
    steps = []
    B = [[] for _ in range(N)]
    snap = lambda: [list(b) for b in B]
    steps.append(dict(phase="start", cur=None, hot=None, read=None, buckets=snap(), out=[],
                      msg=f"We create <b>{N} empty buckets</b>, one for every possible key from 0 to {N-1}."))
    for idx, (k, lbl) in enumerate(items):
        B[k].append((k, lbl))
        steps.append(dict(phase="scatter", cur=idx, hot=k, read=None, buckets=snap(), out=[],
                          msg=f"<b>Scatter:</b> item <b>{lbl}</b> has key <b>{k}</b> → it goes to the end of <b>bucket {k}</b>. No comparison needed."))
    out = []
    for k in range(N):
        if B[k]:
            for e in B[k]:
                out.append(e)
            steps.append(dict(phase="gather", cur=None, hot=None, read=k, buckets=snap(), out=list(out),
                              msg=f"<b>Gather:</b> bucket <b>{k}</b> is read from front to back → {len(B[k])} item(s) copied to the sorted list."))
    steps.append(dict(phase="done", cur=None, hot=None, read=None, buckets=snap(), out=list(out),
                      msg="<b>Done!</b> All buckets were read in order 0, 1, 2, … so the list is sorted — and equal keys kept their original order (stable)."))
    return steps


def render_step(s, items, N):
    chips = []
    for idx, (k, lbl) in enumerate(items):
        cls = "chip"
        if s["phase"] == "scatter":
            if idx == s["cur"]:
                cls += " cur"
            elif idx < s["cur"]:
                cls += " ghost"
        elif s["phase"] in ("gather", "done"):
            cls += " ghost"
        chips.append(f'<span class="{cls}">{lbl}: {k}</span>')
    html = '<div class="small"><b>Input list</b></div><div>' + "".join(chips) + "</div>"

    show = list(range(N)) if N <= 30 else [k for k in range(N) if s["buckets"][k]]
    html += f'<div class="small" style="margin-top:10px"><b>Buckets</b>'
    if N > 30:
        html += f" (showing the {len(show)} non-empty buckets; the other {N-len(show)} are empty but still created and checked)"
    html += '</div><div class="bwrap">'
    for k in show:
        cls = "bucket" + (" hot" if s["hot"] == k else "") + (" read" if s["read"] == k else "")
        inner = "".join(f'<span class="chip">{lbl}</span><br>' for _, lbl in s["buckets"][k])
        html += f'<div class="{cls}"><div class="lbl">B[{k}]</div>{inner}</div>'
    html += "</div>"
    out = "".join(f'<span class="chip done">{lbl}: {k}</span>' for k, lbl in s["out"])
    html += '<div class="small"><b>Sorted output</b></div><div>' + (out or '<span class="small">— empty —</span>') + "</div>"
    return html


# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.markdown("## 🪣 Bucket Sort Lab")
    st.caption("Data Structures Lab · Project P-12.61")
    page = st.radio("Go to", ["🏠 Home", "🎲 1. Make Data", "🎬 2. Watch Bucket Sort", "⚡ 3. Race the Algorithms",
                              "📈 4. Experiments & Graphs", "✅ 5. Tests", "💻 6. Source Code", "ℹ️ About"],
                    label_visibility="collapsed")
    st.divider()
    st.markdown("**Current data**")
    st.write(f"{len(st.session_state.data_items)} items · keys 0 to {st.session_state.N - 1}")
    st.caption("Change it on the *Make Data* page.")
    st.divider()
    st.caption("Team: M. Abdul Rahman Khan (106) · M. Huzaifa Shamsi (135) · Basit Mirza (140) · M. Hashir (152)")


# ------------------------------------------------------------------ pages
if page == "🏠 Home":
    st.markdown("""<div class="hero"><h1>Bucket-Sort for Integer Keys</h1>
    <p>Sorting n entries with keys in the range [0, N−1] in O(n + N) time — explained, animated and measured.</p></div>""",
                unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown('<div class="card"><h4>What is sorting?</h4>Putting things in order — like arranging exam copies by roll number, or students by marks.</div>', unsafe_allow_html=True)
    with c2:
        st.markdown('<div class="card"><h4>What is bucket-sort?</h4>Like a post office: every letter goes straight into the box with its number. Then the boxes are emptied in order. <b>No two keys are ever compared.</b></div>', unsafe_allow_html=True)
    with c3:
        st.markdown('<div class="card"><h4>Why is it fast?</h4>Comparison sorts can\'t beat O(n log n). Bucket-sort uses the key as an index, so it runs in <b>O(n + N)</b>.</div>', unsafe_allow_html=True)

    st.markdown("### How to use this app")
    steps = [("Make Data", "Create random student marks, random numbers, or type your own — one click."),
             ("Watch Bucket Sort", "See every item drop into its bucket and come back out sorted, step by step."),
             ("Race the Algorithms", "Run bucket, merge, quick and insertion sort on the same data and compare times."),
             ("Experiments & Graphs", "Repeat the two experiments from our report and draw the graphs live."),
             ("Tests", "Run the correctness tests and see them pass."),
             ("Source Code", "Read and download the exact code used in the project.")]
    for i, (t, d) in enumerate(steps, 1):
        st.markdown(f'<span class="step">{i}</span><b>{t}</b> — {d}', unsafe_allow_html=True)

    st.markdown("### The three steps of bucket-sort")
    a, b, c = st.columns(3)
    a.info("**1. Create** N empty buckets B[0] … B[N−1]  \n⏱ O(N)")
    b.warning("**2. Scatter** — put each entry at the end of bucket B[key]  \n⏱ O(n)")
    c.success("**3. Gather** — read buckets 0 → N−1 back into the list  \n⏱ O(n + N)")


elif page == "🎲 1. Make Data":
    st.title("🎲 Make Data")
    st.write("Choose how you want to create the data. Everything else in the app uses this data.")

    st.markdown("#### Quick presets")
    p1, p2, p3, p4 = st.columns(4)
    if p1.button("🧑‍🎓 Class of 15 (marks 0–20)", width="stretch"):
        set_data(make_students(15, 20), 21, "students"); st.rerun()
    if p2.button("🔢 12 numbers (0–9)", width="stretch"):
        set_data(make_numbers(12, 10), 10, "numbers"); st.rerun()
    if p3.button("🏫 Class of 60 (marks 0–100)", width="stretch"):
        set_data(make_students(60, 100), 101, "students"); st.rerun()
    if p4.button("📦 Big data: 10,000 keys (0–999)", width="stretch"):
        set_data(make_numbers(10000, 1000), 1000, "numbers"); st.rerun()

    st.markdown("#### Or build your own")
    t1, t2, t3, t4 = st.tabs(["🧑‍🎓 Student marks", "🔢 Random numbers", "✍️ Type numbers", "📄 Upload CSV"])
    with t1:
        c1, c2 = st.columns(2)
        n = c1.slider("How many students?", 2, 2000, 20)
        mx = c2.slider("Total marks of the paper (marks go from 0 to this)", 1, 1000, 50)
        if st.button("Generate students", type="primary"):
            set_data(make_students(n, mx), mx + 1, "students"); st.rerun()
    with t2:
        c1, c2 = st.columns(2)
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
                    st.error("Please type at least one number, and no negative numbers.")
                else:
                    set_data([(v, f"#{i+1}") for i, v in enumerate(vals)], max(max(vals) + 1, 2), "numbers"); st.rerun()
            except ValueError:
                st.error("Only whole numbers please, e.g. 4 1 3 0")
    with t4:
        st.caption("CSV with two columns: **name** and **key** (key = whole number ≥ 0).")
        sample = "name,key\nAli,78\nSara,91\nHamza,78\nAyesha,85\n"
        st.download_button("Download a sample CSV", sample, "sample.csv")
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
                st.error("Could not read the file. It needs columns 'name' and 'key'.")

    st.divider()
    items, N = st.session_state.data_items, st.session_state.N
    m1, m2, m3 = st.columns(3)
    m1.metric("Items (n)", f"{len(items):,}")
    m2.metric("Buckets (N)", f"{N:,}")
    m3.metric("Different keys used", f"{len(set(k for k, _ in items)):,}")
    st.dataframe(items_df(items[:1000], key_name()), width="stretch", hide_index=True, height=300)
    if len(items) > 1000:
        st.caption("Showing the first 1,000 rows.")


elif page == "🎬 2. Watch Bucket Sort":
    st.title("🎬 Watch Bucket Sort")
    items, N = st.session_state.data_items, st.session_state.N
    if len(items) > 40 or N > 200:
        st.info(f"Your data has {len(items):,} items and {N:,} buckets — too big to animate item by item. "
                "Here is what the buckets look like after sorting. For the animation, pick a small preset on *Make Data*.")
        sorted_items = bucket_sort(list(items), N, key=lambda e: e[0])
        counts = [0] * N
        for k, _ in items:
            counts[k] += 1
        fig = go.Figure(go.Bar(x=list(range(N)), y=counts, marker_color="#2E75B6"))
        fig.update_layout(title="How many items landed in each bucket", xaxis_title="Bucket (key)",
                          yaxis_title="Items", height=380, margin=dict(t=50, b=40))
        st.plotly_chart(fig, width="stretch")
        empty = counts.count(0)
        st.write(f"**{N - empty:,}** buckets got items, **{empty:,}** stayed empty (but were still created and checked — that is the “+N” in O(n + N)).")
        st.dataframe(items_df(sorted_items[:1000], key_name()), width="stretch", hide_index=True, height=280)
    else:
        steps = bucket_steps(items, N)
        st.write(f"{len(items)} items, {N} buckets → **{len(steps)} steps**. Press **Play** or move the slider.")
        c1, c2, c3 = st.columns([1, 1, 4])
        speed = c3.select_slider("Speed", ["Slow", "Normal", "Fast"], value="Normal")
        delay = {"Slow": 1.2, "Normal": 0.6, "Fast": 0.25}[speed]
        play = c1.button("▶ Play", type="primary", width="stretch")
        if c2.button("⟲ Reset", width="stretch"):
            st.session_state.step = 0
        st.session_state.step = min(st.session_state.get("step", 0), len(steps) - 1)
        k = st.slider("Step", 0, len(steps) - 1, st.session_state.step)
        st.session_state.step = k
        msg_box, view = st.empty(), st.empty()

        def show(i):
            s = steps[i]
            phase = {"start": "Step 1 · Create", "scatter": "Step 2 · Scatter", "gather": "Step 3 · Gather", "done": "Finished"}[s["phase"]]
            msg_box.markdown(f'<div class="msg"><b>{phase}</b> — {s["msg"]}</div>', unsafe_allow_html=True)
            view.markdown(render_step(s, items, N), unsafe_allow_html=True)

        if play:
            for i in range(k, len(steps)):
                show(i)
                time.sleep(delay)
            st.session_state.step = len(steps) - 1
        else:
            show(k)

        with st.expander("What is happening in the code?"):
            st.code("""B = [[] for _ in range(N)]        # Step 1: N empty buckets      O(N)
for e in entries:                  # Step 2: scatter              O(n)
    B[key(e)].append(e)
i = 0
for bucket in B:                   # Step 3: gather               O(n + N)
    for e in bucket:
        entries[i] = e
        i += 1""", language="python")


elif page == "⚡ 3. Race the Algorithms":
    st.title("⚡ Race the Algorithms")
    items, N = st.session_state.data_items, st.session_state.N
    keys = [k for k, _ in items]
    st.write(f"All algorithms sort the **same {len(keys):,} keys** (range 0–{N-1}). Each one runs 3 times and the best time is kept.")
    if len(keys) < 1000:
        st.info("Your current data is very small, so every algorithm finishes in a tiny fraction of a millisecond "
                "and the race is not fair to judge. Load bigger data for a clear result:")
        if st.button("📦 Load 20,000 random keys (0–999) and race"):
            set_data(make_numbers(20000, 1000), 1000, "numbers"); st.rerun()
    use_ins = len(keys) <= 5000
    if not use_ins:
        st.caption("Insertion sort is skipped for more than 5,000 items because it is O(n²) and would take too long.")
    if st.button("🏁 Start the race", type="primary"):
        algos = {"Bucket sort": lambda a: bucket_sort(a, N, key=lambda x: x), "Merge sort": merge_sort,
                 "Quick sort": quick_sort, "Python sorted()": sorted}
        if use_ins:
            algos["Insertion sort"] = insertion_sort
        res, ok = {}, {}
        expected = sorted(keys)
        bar = st.progress(0.0)
        for i, (name, f) in enumerate(algos.items()):
            res[name] = time_it(f, keys, repeats=1 if name == "Insertion sort" else 3) * 1000
            ok[name] = f(keys[:]) == expected
            bar.progress((i + 1) / len(algos))
        bar.empty()
        order = sorted(res, key=res.get)
        fig = go.Figure(go.Bar(x=[res[a] for a in order], y=order, orientation="h",
                               marker_color=[COLORS[a] for a in order],
                               text=[f"{res[a]:.2f} ms" for a in order], textposition="outside"))
        fig.update_layout(title="Running time (lower is better)", xaxis_title="Time (ms)", height=360,
                          yaxis=dict(autorange="reversed"), margin=dict(t=50, l=10, r=40))
        st.plotly_chart(fig, width="stretch")
        best = order[0]
        st.success(f"🏆 Fastest: **{best}** ({res[best]:.2f} ms)")
        if "Bucket sort" in res:
            for other in ("Merge sort", "Quick sort"):
                st.write(f"Bucket sort is **{res[other] / max(res['Bucket sort'], 1e-9):.1f}×** faster than {other.lower()} on this data.")
        st.dataframe(pd.DataFrame({"Algorithm": order, "Time (ms)": [round(res[a], 3) for a in order],
                                   "Correct result?": ["✅ Yes" if ok[a] else "❌ No" for a in order]}),
                     hide_index=True, width="stretch")
        st.caption("Python's sorted() is written in C, so it is very fast. All the others are written in plain Python.")


elif page == "📈 4. Experiments & Graphs":
    st.title("📈 Experiments & Graphs")
    st.write("These are the two experiments from our report. You can see the report's numbers instantly, or run the experiments live.")
    mode = st.radio("Data source", ["📄 Results from our report", "▶ Run live now"], horizontal=True)
    tabA, tabB = st.tabs(["Experiment A — grow n (N = 1000)", "Experiment B — grow N (n = 10,000)"])

    def fig_a(rows):
        n = [r[0] for r in rows]
        fig = go.Figure()
        for idx, name, sym in [(1, "Bucket sort", "circle"), (2, "Merge sort", "square"), (3, "Quick sort", "triangle-up")]:
            fig.add_trace(go.Scatter(x=n, y=[r[idx] for r in rows], mode="lines+markers", name=f"{name}",
                                     line=dict(color=COLORS[name], width=4 if idx == 1 else 2), marker=dict(symbol=sym, size=9)))
        ins = [(r[0], r[4]) for r in rows if r[4] is not None]
        if ins:
            fig.add_trace(go.Scatter(x=[x for x, _ in ins], y=[y for _, y in ins], mode="lines+markers", name="Insertion sort",
                                     line=dict(color=COLORS["Insertion sort"], dash="dash"), marker=dict(symbol="x", size=9)))
        fig.update_layout(title="Running time vs n (N = 1000)", xaxis_title="Number of entries n", yaxis_title="Time (ms)",
                          height=450, yaxis=dict(range=[0, max(r[2] for r in rows) * 1.15]), hovermode="x unified")
        return fig

    def fig_b(rows):
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=[r[0] for r in rows], y=[r[1] for r in rows], mode="lines+markers", name="Bucket sort",
                                 line=dict(color=COLORS["Bucket sort"], width=4), marker=dict(size=9)))
        fig.add_trace(go.Scatter(x=[r[0] for r in rows], y=[r[2] for r in rows], mode="lines+markers", name="Merge sort",
                                 line=dict(color=COLORS["Merge sort"]), marker=dict(symbol="square", size=9)))
        fig.update_layout(title="Running time vs key range N (n = 10,000)", xaxis_title="Key range N (log scale)",
                          yaxis_title="Time (ms)", xaxis_type="log", height=450, hovermode="x unified")
        return fig

    rows_a, rows_b = REPORT_A, REPORT_B
    if mode == "▶ Run live now":
        c1, c2 = st.columns(2)
        sizes = c1.multiselect("Values of n for Experiment A", [1000, 2000, 5000, 10000, 20000, 50000, 100000],
                               default=[1000, 2000, 5000, 10000, 20000, 50000])
        Ns = c2.multiselect("Values of N for Experiment B", [10, 100, 1000, 10000, 100000, 1000000],
                            default=[10, 100, 1000, 10000, 100000, 1000000])
        st.caption("Tip: bigger values give clearer results but take longer (up to a minute).")
        if st.button("▶ Run both experiments", type="primary"):
            random.seed(42)
            bar, status = st.progress(0.0), st.empty()
            total, done = len(sizes) + len(Ns), 0
            rows_a = []
            for n in sorted(sizes):
                status.write(f"Experiment A: n = {n:,} …")
                data = [random.randrange(1000) for _ in range(n)]
                tb = time_it(lambda a: bucket_sort(a, 1000, key=lambda x: x), data) * 1000
                tm = time_it(merge_sort, data) * 1000
                tq = time_it(quick_sort, data) * 1000
                ti = time_it(insertion_sort, data, repeats=1) * 1000 if n <= 5000 else None
                ts = time_it(sorted, data) * 1000
                rows_a.append((n, tb, tm, tq, ti, ts))
                done += 1; bar.progress(done / total)
            rows_b = []
            for N in sorted(Ns):
                status.write(f"Experiment B: N = {N:,} …")
                data = [random.randrange(N) for _ in range(10000)]
                tb = time_it(lambda a, N=N: bucket_sort(a, N, key=lambda x: x), data) * 1000
                tm = time_it(merge_sort, data) * 1000
                rows_b.append((N, tb, tm))
                done += 1; bar.progress(done / total)
            bar.empty(); status.success("Done! Graphs below are from this live run.")
            st.session_state.live = (rows_a, rows_b)
        if "live" in st.session_state:
            rows_a, rows_b = st.session_state.live
        else:
            st.info("Press the button to run. Until then, the report's results are shown.")

    with tabA:
        if rows_a:
            st.plotly_chart(fig_a(rows_a), width="stretch")
            st.dataframe(pd.DataFrame([{"n": f"{r[0]:,}", "Bucket (ms)": f"{r[1]:.2f}", "Merge (ms)": f"{r[2]:.2f}", "Quick (ms)": f"{r[3]:.2f}",
                                        "Insertion (ms)": "skipped" if r[4] is None else f"{r[4]:.2f}", "sorted() (ms)": f"{r[5]:.2f}"} for r in rows_a]),
                         hide_index=True, width="stretch")
            last = rows_a[-1]
            st.markdown(f"""**What this shows**
- The blue bucket-sort line stays at the bottom and grows like a straight line → **linear, O(n)**.
- At n = {last[0]:,}, bucket sort is **{last[2]/last[1]:.0f}×** faster than merge sort and **{last[3]/last[1]:.0f}×** faster than quick sort.
- The red insertion-sort line shoots off the top → **O(n²)**, so it is skipped after 5,000.""")
    with tabB:
        if rows_b:
            st.plotly_chart(fig_b(rows_b), width="stretch")
            st.dataframe(pd.DataFrame([{"N": f"{r[0]:,}", "Bucket (ms)": f"{r[1]:.2f}", "Merge (ms)": f"{r[2]:.2f}",
                                        "Winner": "Bucket" if r[1] < r[2] else "Merge"} for r in rows_b]),
                         hide_index=True, width="stretch")
            big = rows_b[-1]
            st.markdown(f"""**What this shows**
- Merge sort stays flat — it only compares keys, so the key range does not matter.
- Bucket sort is fast while N ≤ n, but at N = {big[0]:,} it must create and check {big[0]:,} buckets (most empty) and becomes **{big[1]/big[2]:.0f}×** slower than merge sort.
- This proves the **“+N”** in O(n + N) is a real cost.""")


elif page == "✅ 5. Tests":
    st.title("✅ Correctness Tests")
    st.write("These are the same four tests that run in our program. Press the button to run them now.")
    if st.button("Run all tests", type="primary"):
        data = [Entry(3, "c1"), Entry(0, "a"), Entry(3, "c2"), Entry(1, "b"), Entry(2, "x"), Entry(0, "a2"), Entry(3, "c3")]
        before = repr(data)
        bucket_sort(data, 4)
        t1 = [e.key for e in data] == [0, 0, 1, 2, 3, 3, 3] and [e.value for e in data if e.key == 3] == ["c1", "c2", "c3"]
        (st.success if t1 else st.error)("**Test 1 — small example + stability** " + ("passed" if t1 else "failed"))
        st.code(f"Before : {before}\nAfter  : {data}", language="text")

        t2 = True
        for _ in range(200):
            N = random.randint(2, 50); n = random.randint(0, 100)
            nums = [random.randrange(N) for _ in range(n)]
            t2 &= bucket_sort(nums[:], N, key=lambda x: x) == sorted(nums)
        (st.success if t2 else st.error)("**Test 2 — 200 random lists match Python's sorted()** " + ("passed" if t2 else "failed"))

        cases = [([], 5, []), ([4], 5, [4]), ([1, 1, 1], 2, [1, 1, 1]), ([4, 3, 2, 1, 0], 5, [0, 1, 2, 3, 4]), ([0, 1, 2, 3], 4, [0, 1, 2, 3])]
        t3 = all(bucket_sort(list(a), N, key=lambda x: x) == exp for a, N, exp in cases)
        (st.success if t3 else st.error)("**Test 3 — edge cases (empty, one item, all equal, reversed, sorted)** " + ("passed" if t3 else "failed"))

        t4 = True
        for a, N in ([[5], 5], [[-1], 5], [[0], 1]):
            try:
                bucket_sort(a, N, key=lambda x: x); t4 = False
            except ValueError:
                pass
        (st.success if t4 else st.error)("**Test 4 — wrong input raises ValueError (key = N, negative key, N < 2)** " + ("passed" if t4 else "failed"))
        if t1 and t2 and t3 and t4:
            st.balloons()


elif page == "💻 6. Source Code":
    st.title("💻 Source Code")
    src = open("bucket_sort.py", encoding="utf-8").read()
    st.write("This is the exact program used in the project. This app imports and uses these same functions.")
    st.download_button("⬇ Download bucket_sort.py", src, "bucket_sort.py", type="primary")
    parts = {"bucket_sort() — the main algorithm": "def bucket_sort", "Entry — the data structure": "class Entry",
             "insertion_sort()": "def insertion_sort", "merge_sort()": "def merge_sort", "quick_sort()": "def quick_sort",
             "time_it() — the stopwatch": "def time_it"}
    for title, start in parts.items():
        with st.expander(title, expanded=title.startswith("bucket")):
            lines = src.split("\n")
            i = next(j for j, l in enumerate(lines) if l.startswith(start))
            j = i + 1
            while j < len(lines) and (lines[j].startswith(" ") or lines[j] == ""):
                j += 1
            st.code("\n".join(lines[i:j]).rstrip(), language="python")
    with st.expander("Full program"):
        st.code(src, language="python", line_numbers=True)


else:
    st.title("ℹ️ About")
    st.markdown("""
**Project:** P-12.61 — Design and implement a version of the bucket-sort algorithm for sorting a list of n entries with
integer keys taken from the range [0, N−1], for N ≥ 2. The algorithm should run in O(n + N) time.

**Course:** Data Structures Lab · **Submitted to:** Sir Jamal
""")
    try:
        with open("Bucket_Sort_Project_Report.pdf", "rb") as f:
            st.download_button("⬇ Download the full project report (PDF)", f.read(), "Bucket_Sort_Project_Report.pdf",
                               "application/pdf", type="primary")
    except FileNotFoundError:
        pass
    st.dataframe(pd.DataFrame({"Name": ["Muhammad Abdul Rahman Khan", "Muhammad Huzaifa Shamsi", "Basit Mirza", "Muhammad Hashir"],
                               "Roll Number": ["25F-DS-106", "25F-DS-135", "25F-DS-140", "25F-DS-152"]}),
                 hide_index=True, width="stretch")
    st.markdown("""
**References**
1. Goodrich, Tamassia & Goldwasser (2013). *Data Structures and Algorithms in Python*. Wiley. Section 12.4.2.
2. [Python docs — time.perf_counter()](https://docs.python.org/3/library/time.html#time.perf_counter)
3. [Python docs — random](https://docs.python.org/3/library/random.html)
4. [Streamlit documentation](https://docs.streamlit.io) · [Plotly Python](https://plotly.com/python/)
""")
