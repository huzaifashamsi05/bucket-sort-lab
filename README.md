# Bucket Sort Lab — P-12.61

Interactive Streamlit lab for bucket sort on integer keys in the range `[0, N-1]`, running in **O(n + N)** time. Built for a Data Structures Lab assignment at Dawood University of Engineering & Technology (DUET).

**Live app:** https://bucket-sort-p1261.streamlit.app/

## What it does

- **Visualizes the algorithm** — walks through the scatter step (each entry dropped into its bucket) and the gather step (buckets read back in order), so the O(n + N) bound is visible, not just stated.
- **Build your own data** — generate custom integer lists and key ranges and watch them get sorted.
- **Race the algorithms** — runs bucket sort head-to-head against merge sort, quick sort, insertion sort, and Python's built-in `sorted()` on the same data.
- **Experiments & graphs** — reproduces the two benchmark experiments from the project report (time vs. n, and time vs. key range N), live or from saved results, with Plotly charts.

## Tech stack

Python · Streamlit · Plotly · Pandas

## Run it locally

```bash
git clone https://github.com/huzaifashamsi05/bucket-sort-lab.git
cd bucket-sort-lab
pip install -r requirements.txt
streamlit run app.py
```

## Project report

The full write-up — algorithm explanation, correctness tests, and benchmark methodology — is included as `Bucket_Sort_Project_Report.pdf` / `.docx` in this repo.

## Author

**Muhammad Huzaifa Shamsi** — [Portfolio](https://portfolio-showcase-api-server-gilt.vercel.app/) · [LinkedIn](https://www.linkedin.com/in/muhammad-huzaifa-shamsi-932438328) · [GitHub](https://github.com/huzaifashamsi05)
