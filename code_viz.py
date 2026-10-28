import html
import inspect
import re
import sys
import time

import streamlit as st

import bucket_sort as bs

ALGOS = {
    "bucket_sort": "Bucket sort (main algorithm)",
    "insertion_sort": "Insertion sort",
    "merge_sort": "Merge sort (recursive)",
    "quick_sort": "Quick sort (recursive)",
}
TARGETS = set(ALGOS)
MAX_STEPS = 700

EXPLAIN = {
    "def bucket_sort(entries, N, key=lambda e: e.key):": "The function starts. It gets the list, the number of buckets N, and a key function.",
    "if N < 2:": "Check that N is at least 2, as the assignment requires.",
    'raise ValueError("N must be at least 2")': "N is too small, so the function stops with an error.",
    "B = [[] for _ in range(N)]": "Create N separate empty buckets. B[k] will hold every item whose key is k.",
    "for e in entries:": "Scatter loop: take the next item from the input list.",
    "k = key(e)": "Read the key of this item. For plain numbers the item is its own key.",
    "if not (0 <= k < N):": "Make sure the key is inside the range 0 to N−1.",
    'raise ValueError(f"key {k} is outside the range [0, {N - 1}]")': "The key is out of range, so the function stops with an error.",
    "B[k].append(e)": "Put the item at the END of bucket k. No comparison with other items is needed.",
    "i = 0": "Start writing the sorted result from position 0 of the original list.",
    "for bucket in B:": "Gather loop: visit the buckets in order 0, 1, 2 … even the empty ones.",
    "for e in bucket:": "Take the items of this bucket from front to back (this keeps the sort stable).",
    "entries[i] = e": "Write the item into position i of the original list.",
    "i += 1": "Move to the next position.",
    "return entries": "All buckets were read in order, so the list is now sorted.",
    "def insertion_sort(a):": "Insertion sort starts. It works like arranging playing cards in your hand.",
    "for j in range(1, len(a)):": "Pick the next item, starting from index 1 (index 0 alone is already sorted).",
    "cur = a[j]": "Hold this item in cur. Its old place is now a free gap.",
    "i = j": "The gap is at position i.",
    "while i > 0 and a[i - 1] > cur:": "Is the item left of the gap bigger than cur? Then it must move right.",
    "a[i] = a[i - 1]": "Shift the bigger item one place right, into the gap.",
    "i -= 1": "The gap moves one place left.",
    "a[i] = cur": "Drop cur into the gap. It is now in its correct place.",
    "return a": "Every item has been inserted, so the list is sorted.",
    "def merge_sort(a):": "Merge sort starts on this part of the list.",
    "if len(a) <= 1:": "A list with 0 or 1 items is already sorted (base case).",
    "return a[:]": "Return a copy of this tiny sorted list.",
    "mid = len(a) // 2": "Find the middle index to split the list in two halves.",
    "left, right = merge_sort(a[:mid]), merge_sort(a[mid:])": "Sort both halves by calling merge_sort again (recursion).",
    "out, i, j = [], 0, 0": "Prepare to merge: an empty output list and two fingers i and j.",
    "while i < len(left) and j < len(right):": "Both halves still have items, so compare their front items.",
    "if left[i] <= right[j]:": "Is the left front item smaller or equal? (<= keeps equal items in order)",
    "out.append(left[i]); i += 1": "Take the left item and move the left finger forward.",
    "else:": "Otherwise the right item is smaller.",
    "out.append(right[j]); j += 1": "Take the right item and move the right finger forward.",
    "out.extend(left[i:]); out.extend(right[j:])": "One half is finished. Add whatever is left in the other half.",
    "return out": "Return the merged, sorted list.",
    "def quick_sort(a):": "Quick sort starts on this part of the list.",
    "pivot = a[len(a) // 2]": "Choose the middle item as the pivot.",
    "smaller = [x for x in a if x < pivot]": "Collect every item smaller than the pivot.",
    "equal = [x for x in a if x == pivot]": "Collect every item equal to the pivot. These never need sorting again.",
    "bigger = [x for x in a if x > pivot]": "Collect every item bigger than the pivot.",
    "return quick_sort(smaller) + equal + quick_sort(bigger)": "Sort the smaller and bigger groups the same way, then join the three groups.",
}

KW = r"\b(def|for|in|if|not|and|or|while|return|raise|else|lambda|range|len)\b"


def _strip(code_line):
    return re.sub(r"\s+#.*$", "", code_line).strip()


def _esc(t):
    return html.escape(t).replace(" ", "&nbsp;")


def _hl(line):
    if line.strip().startswith("#"):
        return f'<span class="cv-c">{_esc(line)}</span>'
    m = re.search(r"\s+#", line)
    code, com = (line[:m.start()], line[m.start():]) if m else (line, "")
    parts = re.split(r'("[^"]*"|f"[^"]*")', code)
    out = []
    for p in parts:
        if p.startswith('"') or p.startswith('f"'):
            out.append(f'<span class="cv-s">{_esc(p)}</span>')
        else:
            e = _esc(p)
            e = re.sub(KW, r'<span class="cv-k">\1</span>', e)
            e = re.sub(r"\b(\d+)\b", r'<span class="cv-n">\1</span>', e)
            out.append(e)
    res = "".join(out)
    if com:
        res += f'<span class="cv-c">{_esc(com)}</span>'
    return res


def _snap(v):
    if isinstance(v, list):
        return [_snap(x) for x in v]
    if isinstance(v, (int, float, str, bool)) or v is None:
        return v
    return repr(v)


def _short(locals_):
    for name in ("entries", "a"):
        if name in locals_ and isinstance(locals_[name], list):
            return f"{locals_[name]}"
    return ""


def trace_run(func_name, data, N):
    fn = getattr(bs, func_name)
    target_file = bs.__file__
    steps, stack = [], []

    class Stop(Exception):
        pass

    def tracer(frame, event, arg):
        code = frame.f_code
        if code.co_name not in TARGETS or code.co_filename != target_file:
            return None
        if event == "call":
            stack.append(f"{code.co_name}({_short(frame.f_locals)})")
        fl = frame.f_locals
        loc = {k: _snap(v) for k, v in fl.items() if k not in ("key",) and not k.startswith(".")}
        if "B" in fl and "bucket" in fl:
            loc["_read"] = next((ix for ix, b in enumerate(fl["B"]) if b is fl["bucket"]), None)
        if event in ("line", "return"):
            steps.append(dict(func=code.co_name, line=frame.f_lineno, locals=loc, stack=list(stack), event=event,
                              ret=_snap(arg) if event == "return" else None))
            if len(steps) > MAX_STEPS:
                raise Stop()
        if event == "return" and stack:
            stack.pop()
        return tracer

    arr = list(data)
    truncated = False
    sys.settrace(tracer)
    try:
        if func_name == "bucket_sort":
            result = fn(arr, N, key=lambda x: x)
        else:
            result = fn(arr)
    except Stop:
        truncated, result = True, None
    finally:
        sys.settrace(None)
    return steps, result, truncated


def _array(name, values, mark=None, cls=""):
    cells = []
    for idx, v in enumerate(values):
        hot = " hot" if mark is not None and idx == mark else ""
        cells.append(f'<div class="cv-cell{hot}"><span class="cv-v">{html.escape(str(v))}</span><span class="cv-i">{idx}</span></div>')
    body = "".join(cells) if cells else '<span class="cv-empty">empty list</span>'
    return f'<div class="cv-var {cls}"><div class="cv-name">{name}</div><div class="cv-arr">{body}</div></div>'


def _buckets(B, hot=None, read=None):
    cols = []
    for k, b in enumerate(B):
        c = " hot" if hot == k else (" read" if read == k else "")
        items = "".join(f'<span class="cv-bi">{html.escape(str(x))}</span>' for x in b)
        cols.append(f'<div class="cv-bk{c}"><div class="cv-bl">B[{k}]</div>{items}</div>')
    return f'<div class="cv-var"><div class="cv-name">B · buckets</div><div class="cv-bks">{"".join(cols)}</div></div>'


def _vars_html(step):
    loc = step["locals"]
    func = step["func"]
    parts, scal = [], []
    if func == "bucket_sort":
        if "entries" in loc:
            mark = loc.get("i") if isinstance(loc.get("i"), int) and "bucket" in loc else None
            parts.append(_array("entries", loc["entries"], mark))
        if "B" in loc:
            line_txt = step.get("code", "")
            hot = loc.get("k") if "B[k]" in line_txt else None
            parts.append(_buckets(loc["B"], hot, loc.get("_read")))
        for n in ("N", "e", "k", "i"):
            if n in loc:
                scal.append((n, loc[n]))
        if loc.get("_read") is not None:
            scal.append(("bucket", f"B[{loc['_read']}]"))
    else:
        main = "a"
        if main in loc:
            mark = None
            if func == "insertion_sort" and isinstance(loc.get("i"), int):
                mark = loc["i"]
            parts.append(_array("a", loc[main], mark))
        for n in ("left", "right", "out", "smaller", "equal", "bigger"):
            if n in loc and isinstance(loc[n], list):
                m = None
                if func == "merge_sort" and n == "left" and isinstance(loc.get("i"), int):
                    m = loc["i"]
                if func == "merge_sort" and n == "right" and isinstance(loc.get("j"), int):
                    m = loc["j"]
                parts.append(_array(n, loc[n], m, "cv-sm"))
        for n in ("j", "cur", "i", "mid", "pivot"):
            if n in loc and not isinstance(loc[n], list):
                scal.append((n, loc[n]))
    chips = "".join(f'<span class="cv-chip"><b>{n}</b> = {html.escape(str(v))}</span>' for n, v in scal)
    if chips:
        parts.insert(0, f'<div class="cv-chips">{chips}</div>')
    if step["event"] == "return":
        parts.append(f'<div class="cv-ret">returns <code>{html.escape(str(step["ret"]))}</code></div>')
    return "".join(parts)


CSS = """
<style>
.cv-wrap { display:grid; grid-template-columns: minmax(0, 1.05fr) minmax(0, 1fr); gap: 18px; align-items: start; }
@media (max-width: 900px) { .cv-wrap { grid-template-columns: minmax(0,1fr); } }
.cv-code { background: #0E1A2B; border-radius: 18px; padding: 16px 0; overflow-x: auto; box-shadow: 0 18px 40px rgba(14,26,43,.18); }
.cv-ln { display:flex; font-family: 'JetBrains Mono', Consolas, monospace; font-size: .82rem; line-height: 1.75; color: #D6DEEA; white-space: pre; padding: 0 16px 0 0; border-left: 4px solid transparent; }
.cv-ln .no { width: 44px; text-align: right; color: #56657D; padding-right: 14px; flex-shrink: 0; user-select: none; }
.cv-ln.cur { background: rgba(200,150,43,.20); border-left-color: #E4BF6A; }
.cv-ln.cur .no { color: #E4BF6A; }
.cv-ln.prev { background: rgba(255,255,255,.04); }
.cv-k { color: #E4BF6A; } .cv-s { color: #8FD3A8; } .cv-n { color: #8AB4FF; } .cv-c { color: #5F6F88; font-style: italic; }
.cv-side { display:flex; flex-direction:column; gap: 12px; min-width: 0; }
.cv-explain { background:#fff; border:1px solid #E3E8F0; border-left: 4px solid #C8962B; border-radius: 14px; padding: 14px 16px; color:#0E1A2B; }
.cv-explain .t { font-size:.72rem; font-weight:800; letter-spacing:.14em; text-transform:uppercase; color:#C8962B; }
.cv-explain .d { margin-top: 4px; font-size: .98rem; }
.cv-panel { background:#fff; border:1px solid #E3E8F0; border-radius: 16px; padding: 14px 16px; color:#0E1A2B; min-width: 0; }
.cv-panel .h { font-size:.72rem; font-weight:800; letter-spacing:.14em; text-transform:uppercase; color:#5B6B82; margin-bottom: 8px; }
.cv-chips { display:flex; flex-wrap:wrap; gap:6px; margin-bottom: 10px; }
.cv-chip { font-family:'JetBrains Mono', monospace; font-size:.8rem; background:#F5F7FB; border:1px solid #E3E8F0; border-radius:8px; padding:3px 9px; color:#0E1A2B; }
.cv-chip b { color:#8A6414; }
.cv-var { margin-bottom: 10px; }
.cv-name { font-family:'JetBrains Mono', monospace; font-size:.78rem; color:#5B6B82; margin-bottom:4px; }
.cv-arr { display:flex; flex-wrap:wrap; gap:4px; }
.cv-cell { min-width: 34px; border:1.5px solid #CBD5E3; border-radius:8px; text-align:center; background:#fff; padding:3px 4px 1px; }
.cv-cell.hot { border-color:#C8962B; background:#FBF2DE; }
.cv-v { display:block; font-family:'JetBrains Mono', monospace; font-weight:700; font-size:.9rem; color:#0E1A2B; }
.cv-i { display:block; font-size:.62rem; color:#8A97AB; }
.cv-sm .cv-cell { min-width: 28px; }
.cv-empty { color:#8A97AB; font-size:.85rem; }
.cv-bks { display:flex; flex-wrap:wrap; gap:6px; }
.cv-bk { min-width: 46px; min-height: 64px; border:1px solid #D5DDEA; border-top:3px solid #C9D3E3; border-radius: 4px 4px 12px 12px; background:#F7F9FC; text-align:center; padding:4px 3px; }
.cv-bk.hot { border-color:#C8962B; border-top-color:#C8962B; background:#FBF2DE; }
.cv-bk.read { border-color:#8CCBA9; border-top-color:#1F8A5B; background:#EAF6EF; }
.cv-bl { font-family:'JetBrains Mono', monospace; font-size:.66rem; color:#5B6B82; margin-bottom:3px; }
.cv-bi { display:block; margin:2px auto; font-family:'JetBrains Mono', monospace; font-size:.75rem; font-weight:700; background:#C8962B; color:#fff; border-radius:5px; width: 26px; }
.cv-stack { display:flex; flex-direction:column; gap:4px; }
.cv-fr { font-family:'JetBrains Mono', monospace; font-size:.78rem; background:#F5F7FB; border:1px solid #E3E8F0; border-radius:8px; padding:4px 8px; color:#0E1A2B; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
.cv-fr.top { border-color:#C8962B; background:#FBF2DE; }
.cv-ret { font-size:.9rem; color:#1F8A5B; } .cv-ret code { font-family:'JetBrains Mono', monospace; }
</style>
"""


def render(page_header, stat, footer):
    page_header("Step 2b · Trace", "Code visualizer",
                "Run the real code from bucket_sort.py one line at a time. See which line runs, what each variable holds, and why.")
    st.markdown(CSS, unsafe_allow_html=True)

    items, N_cur = st.session_state.data_items, st.session_state.N
    default = " ".join(str(k) for k, _ in items) if len(items) <= 10 and N_cur <= 12 else "3 0 3 1 2 0"
    c1, c2 = st.columns([1.2, 2], gap="medium")
    algo = c1.selectbox("Algorithm", list(ALGOS), format_func=lambda k: ALGOS[k])
    txt = c2.text_input("Numbers to sort (up to 10 whole numbers, 0 to 11)", default)
    try:
        data = [int(x) for x in txt.replace(",", " ").split()]
    except ValueError:
        st.error("Type whole numbers only, for example 3 0 3 1 2 0.")
        return
    if not data or len(data) > 10 or min(data) < 0 or max(data) > 11:
        st.error("Use 1 to 10 numbers, each between 0 and 11, so every step fits on screen.")
        return
    N = max(max(data) + 1, 2)

    sig = (algo, tuple(data))
    if st.session_state.get("cv_sig") != sig:
        steps, result, truncated = trace_run(algo, data, N)
        src_lines, start = inspect.getsourcelines(getattr(bs, algo))
        for s in steps:
            s["code"] = _strip(src_lines[s["line"] - start]) if 0 <= s["line"] - start < len(src_lines) else ""
        st.session_state.cv_sig = sig
        st.session_state.cv = (steps, result, truncated, src_lines, start)
        st.session_state.cv_step = 0
    steps, result, truncated, src_lines, start = st.session_state.cv

    a, b, c = st.columns(3, gap="medium")
    stat(a, "Steps traced", f"{len(steps)}")
    stat(b, "Lines in function", f"{len(src_lines)}")
    stat(c, "Result", "sorted ✓" if result == sorted(data) else "—")
    st.write("")
    if truncated:
        st.caption(f"Only the first {MAX_STEPS} steps are shown.")

    b1, b2, b3, b4 = st.columns([1, 1, 1.2, 3], gap="small")
    if b1.button("◀ Back", width="stretch"):
        st.session_state.cv_step = max(0, st.session_state.cv_step - 1)
    if b2.button("Next ▶", width="stretch"):
        st.session_state.cv_step = min(len(steps) - 1, st.session_state.cv_step + 1)
    play = b3.button("▶ Play", type="primary", width="stretch")
    speed = b4.select_slider("Speed", ["Slow", "Normal", "Fast"], value="Normal", label_visibility="collapsed", key="cv_speed")
    delay = {"Slow": 0.9, "Normal": 0.45, "Fast": 0.15}[speed]
    st.session_state.cv_step = min(st.session_state.cv_step, len(steps) - 1)
    k = st.slider("Step", 0, len(steps) - 1, st.session_state.cv_step, key=f"cv_slider_{st.session_state.cv_step}")
    st.session_state.cv_step = k
    box = st.empty()

    def draw(i):
        s = steps[i]
        prev_line = steps[i - 1]["line"] if i > 0 else None
        code_html = []
        for off, line in enumerate(src_lines):
            no = start + off
            cls = " cur" if no == s["line"] else (" prev" if no == prev_line else "")
            code_html.append(f'<div class="cv-ln{cls}"><span class="no">{no}</span>{_hl(line.rstrip())}</div>')
        title = "Function returns" if s["event"] == "return" else f"Line {s['line']} · about to run"
        expl = EXPLAIN.get(s["code"], "")
        if s["event"] == "return":
            expl = f"<b>{s['func']}</b> finishes and hands back its result."
        stack = "".join(f'<div class="cv-fr{" top" if j == len(s["stack"]) - 1 else ""}">{html.escape(f)}</div>'
                        for j, f in enumerate(s["stack"]))
        side = (f'<div class="cv-explain"><div class="t">{title} · step {i} of {len(steps) - 1}</div>'
                f'<div class="d">{expl}</div></div>'
                f'<div class="cv-panel"><div class="h">Variables</div>{_vars_html(s)}</div>'
                f'<div class="cv-panel"><div class="h">Call stack</div><div class="cv-stack">{stack}</div></div>')
        box.markdown(f'<div class="cv-wrap"><div class="cv-code">{"".join(code_html)}</div><div class="cv-side">{side}</div></div>',
                     unsafe_allow_html=True)

    if play:
        for i in range(k, len(steps)):
            draw(i)
            time.sleep(delay)
        st.session_state.cv_step = len(steps) - 1
    else:
        draw(k)

    st.write("")
    with st.expander("How does this work?"):
        st.markdown("The page runs the real function from `bucket_sort.py` with Python's built-in tracer (`sys.settrace`). "
                    "Before each line runs, it saves the line number and a copy of every variable. The slider lets you move "
                    "through those saved moments. The gold line is the next line to run, and the faint line is the one that just ran.")
    footer()
