# Q3: splitting small vs large CSV

**Small file (100k rows, 17MB)**
- just `pd.read_csv()` the whole thing into memory
- memory used ≈ 100MB, takes ~3 seconds
- easy: I can sort, group, join, do multiple passes, anything

**Large file (2M rows, 350MB)**
- loading it fully needs ~1GB+ RAM (pandas DataFrame was 1.4GB) -> risk of out-of-memory
- so I read it in chunks (100k rows at a time) and only keep running counters
- memory stays ~constant (one chunk) no matter how big the file is
- downside: it's one pass only. things that need the whole dataset at once
  (sort, exact median, dedupe across the file) need extra work:
  keep a set of ids, use approximate algorithms, or use a tool like DuckDB/Polars
  that spills to disk

**Measured on the real files**
| | rows | time | peak memory |
|---|---|---|---|
| small, full load | 100k | 3s | 109 MB |
| large, full load (bad) | 2M | 16s | 975 MB |
| large, chunked | 2M | 26s | ~200 MB |
| large, csv module | 2M | 42s | ~90 MB |

So: small file -> load it all, simpler. Large file -> stream it, slower but safe.
