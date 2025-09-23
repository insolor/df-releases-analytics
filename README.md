# Dwarf Fortress releases analytics

[![Open the app](https://img.shields.io/badge/Open%20the%20app-forestgreen?style=for-the-badge)](https://df-releases-analytics.streamlit.app)

Based on data from [bay12games.com/dwarves/older_versions](https://bay12games.com/dwarves/older_versions.html) and
information about betas from [steam](https://store.steampowered.com/news/app/975370?updates=true).

## Marimo

Run marimo locally:

```shell
marimo run main_marimo.py
```

Build marimo static site:

```shell
marimo export html-wasm main_marimo.py -o output --mode run --include-cloudflare
```

Serve locally:

```shell
python -m http.server --directory output 8889
```
