# P-12.61: Bucket-sort for integer keys in the range [0, N-1], O(n + N) time
# Data Structures Lab Project

import random   # random test data and random lists for the experiments
import time     # time.perf_counter() is used as a stopwatch


# ---------------------------------------------------------------
# Data structure: one entry = (key, value)
# ---------------------------------------------------------------
class Entry:
    __slots__ = ("key", "value")   # only these two fields, saves memory

    def __init__(self, key, value=None):
        self.key = key
        self.value = value

    # how an entry looks when printed, e.g. (3, 'c1')
    def __repr__(self):
        return f"({self.key}, {self.value!r})"


# ---------------------------------------------------------------
# Main algorithm: bucket-sort
# entries : list to sort (sorted in place)
# N       : keys are in the range 0 .. N-1
# key     : how to get the key from an item (default: e.key)
# ---------------------------------------------------------------
def bucket_sort(entries, N, key=lambda e: e.key):
    if N < 2:
        raise ValueError("N must be at least 2")

    # create N empty buckets, B[k] holds all entries with key k   -> O(N)
    B = [[] for _ in range(N)]

    # scatter: put every entry at the end of its bucket           -> O(n)
    for e in entries:
        k = key(e)
        if not (0 <= k < N):
            raise ValueError(f"key {k} is outside the range [0, {N - 1}]")
        B[k].append(e)

    # gather: read buckets 0 .. N-1 in order back into the list   -> O(n + N)
    i = 0
    for bucket in B:
        for e in bucket:
            entries[i] = e
            i += 1

    return entries


# ---------------------------------------------------------------
# Comparison sorts, used only to compare running times
# ---------------------------------------------------------------

# insertion sort: shift bigger items right, put cur in the gap   O(n^2)
def insertion_sort(a):
    for j in range(1, len(a)):
        cur = a[j]
        i = j
        while i > 0 and a[i - 1] > cur:
            a[i] = a[i - 1]
            i -= 1
        a[i] = cur
    return a


# merge sort: split in halves, sort each half, merge them        O(n log n)
def merge_sort(a):
    if len(a) <= 1:
        return a[:]
    mid = len(a) // 2
    left, right = merge_sort(a[:mid]), merge_sort(a[mid:])
    # merge two sorted lists, i and j point to the front items
    out, i, j = [], 0, 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    out.extend(left[i:]); out.extend(right[j:])
    return out


# quick sort: smaller / equal / bigger than the pivot            O(n log n) average
def quick_sort(a):
    if len(a) <= 1:
        return a[:]
    pivot = a[len(a) // 2]
    smaller = [x for x in a if x < pivot]
    equal = [x for x in a if x == pivot]
    bigger = [x for x in a if x > pivot]
    return quick_sort(smaller) + equal + quick_sort(bigger)


# ---------------------------------------------------------------
# Correctness tests (assert stops the program if an answer is wrong)
# ---------------------------------------------------------------
def run_tests():
    print("=" * 64)
    print("CORRECTNESS TESTS")
    print("=" * 64)

    # Test 1: small example, also checks stability (c1, c2, c3 keep order)
    data = [Entry(3, "c1"), Entry(0, "a"), Entry(3, "c2"), Entry(1, "b"),
            Entry(2, "x"), Entry(0, "a2"), Entry(3, "c3")]
    print("Before :", data)
    bucket_sort(data, 4)
    print("After  :", data)
    assert [e.key for e in data] == [0, 0, 1, 2, 3, 3, 3]
    assert [e.value for e in data if e.key == 3] == ["c1", "c2", "c3"]
    print("Test 1 passed - sorted and STABLE (c1, c2, c3 kept their order)\n")

    # Test 2: 200 random lists compared with Python's sorted()
    for trial in range(200):
        N = random.randint(2, 50)
        n = random.randint(0, 100)
        nums = [random.randrange(N) for _ in range(n)]
        assert bucket_sort(nums[:], N, key=lambda x: x) == sorted(nums)
    print("Test 2 passed - 200 random lists match Python's sorted()")

    # Test 3: edge cases
    assert bucket_sort([], 5, key=lambda x: x) == []
    assert bucket_sort([4], 5, key=lambda x: x) == [4]
    assert bucket_sort([1, 1, 1], 2, key=lambda x: x) == [1, 1, 1]
    assert bucket_sort([4, 3, 2, 1, 0], 5, key=lambda x: x) == [0, 1, 2, 3, 4]
    assert bucket_sort([0, 1, 2, 3], 4, key=lambda x: x) == [0, 1, 2, 3]
    print("Test 3 passed - empty, single, duplicates, reversed, sorted")

    # Test 4: wrong input must raise ValueError
    for bad_call in (lambda: bucket_sort([5], 5, key=lambda x: x),
                     lambda: bucket_sort([-1], 5, key=lambda x: x),
                     lambda: bucket_sort([0], 1, key=lambda x: x)):
        try:
            bad_call()
            raise AssertionError("should have raised ValueError")
        except ValueError:
            pass
    print("Test 4 passed - out-of-range keys and N < 2 raise ValueError\n")


# ---------------------------------------------------------------
# Performance analysis
# ---------------------------------------------------------------

# run func 3 times on a fresh copy of data and return the best time (seconds)
def time_it(func, data, repeats=3):
    best = float("inf")
    for _ in range(repeats):
        copy = data[:]
        start = time.perf_counter()
        func(copy)
        best = min(best, time.perf_counter() - start)
    return best


def benchmark():
    random.seed(42)   # same random data on every run
    results = {}

    # Experiment A: N fixed at 1000, number of entries n grows
    print("=" * 64)
    print("EXPERIMENT A: vary n (N = 1000 fixed) - times in milliseconds")
    print("=" * 64)
    N = 1000
    sizes = [1000, 2000, 5000, 10000, 20000, 50000, 100000]
    print(f"{'n':>8} {'Bucket':>10} {'Merge':>10} {'Quick':>10} {'Insertion':>10} {'sorted()':>10}")
    rows_a = []
    for n in sizes:
        data = [random.randrange(N) for _ in range(n)]   # n random keys in 0..N-1
        tb = time_it(lambda a: bucket_sort(a, N, key=lambda x: x), data)
        tm = time_it(merge_sort, data)
        tq = time_it(quick_sort, data)
        # insertion sort is O(n^2), so it is only run for small n
        ti = time_it(insertion_sort, data, repeats=1) if n <= 5000 else None
        ts = time_it(sorted, data)
        rows_a.append((n, tb, tm, tq, ti, ts))
        ins = f"{ti*1000:10.2f}" if ti is not None else f"{'(skip)':>10}"
        print(f"{n:>8} {tb*1000:10.2f} {tm*1000:10.2f} {tq*1000:10.2f} {ins} {ts*1000:10.2f}")
    results["A"] = rows_a

    # Experiment B: n fixed at 10000, key range N grows
    print()
    print("=" * 64)
    print("EXPERIMENT B: vary N (n = 10000 fixed) - bucket sort, ms")
    print("=" * 64)
    n = 10000
    print(f"{'N':>10} {'Bucket (ms)':>12} {'Merge (ms)':>12}")
    rows_b = []
    for N in [10, 100, 1000, 10000, 100000, 1000000]:
        data = [random.randrange(N) for _ in range(n)]
        tb = time_it(lambda a: bucket_sort(a, N, key=lambda x: x), data)
        tm = time_it(merge_sort, data)
        rows_b.append((N, tb, tm))
        print(f"{N:>10} {tb*1000:12.2f} {tm*1000:12.2f}")
    results["B"] = rows_b
    print()
    return results


# draw the two graphs with matplotlib, save them as PNG and show them
def make_charts(results):
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        print("matplotlib not installed - charts skipped (pip install matplotlib)")
        return

    # Graph 1: Experiment A (time vs n)
    rows = results["A"]
    n = [r[0] for r in rows]
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.plot(n, [r[1] * 1000 for r in rows], "o-", label="Bucket sort  O(n+N)", lw=2.5)
    ax.plot(n, [r[2] * 1000 for r in rows], "s-", label="Merge sort  O(n log n)")
    ax.plot(n, [r[3] * 1000 for r in rows], "^-", label="Quick sort  O(n log n)")
    # insertion sort only has times for small n, skip the None values
    ins = [(r[0], r[4] * 1000) for r in rows if r[4] is not None]
    ax.plot([x for x, _ in ins], [y for _, y in ins], "x--", label="Insertion sort  O(n²)")
    ax.set_xlabel("Number of entries n")
    ax.set_ylabel("Time (ms)")
    ax.set_title("Experiment A: running time vs n  (N = 1000)")
    # limit the y-axis so insertion sort does not squeeze the other lines
    ax.set_ylim(0, max(r[2] for r in rows) * 1000 * 1.15)
    ax.grid(alpha=0.3); ax.legend()
    fig.tight_layout(); fig.savefig("chart_experiment_A.png", dpi=150)

    # Graph 2: Experiment B (time vs N), x-axis on log scale
    rows = results["B"]
    fig, ax = plt.subplots(figsize=(7, 4.2))
    ax.semilogx([r[0] for r in rows], [r[1] * 1000 for r in rows], "o-", lw=2.5, label="Bucket sort")
    ax.semilogx([r[0] for r in rows], [r[2] * 1000 for r in rows], "s-", label="Merge sort")
    ax.set_xlabel("Key range N (log scale)")
    ax.set_ylabel("Time (ms)")
    ax.set_title("Experiment B: running time vs N  (n = 10,000)")
    ax.grid(alpha=0.3, which="both"); ax.legend()
    fig.tight_layout(); fig.savefig("chart_experiment_B.png", dpi=150)
    print("Charts saved: chart_experiment_A.png, chart_experiment_B.png")
    plt.show()


# program starts here: tests, then experiments, then graphs
if __name__ == "__main__":
    run_tests()
    res = benchmark()
    make_charts(res)
