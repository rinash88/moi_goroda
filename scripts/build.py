"""Собирает index.html из шаблона, контента городов и данных карты.

Запуск из корня репозитория: python3 scripts/build.py
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
template = (ROOT / "src/template.html").read_text(encoding="utf-8")
content = (ROOT / "src/content.js").read_text(encoding="utf-8")
data = (ROOT / "data/map-data.json").read_text(encoding="utf-8")

page = template.replace("__CONTENT__", content).replace("__DATA__", data)
html = (
    '<!doctype html><html lang="ru"><head><meta charset="utf-8">'
    '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">'
    "<style>html{color-scheme:light}body{margin:0}img{max-width:100%}[hidden]{display:none!important}</style>"
    "</head><body>" + page + "</body></html>"
)
(ROOT / "index.html").write_text(html, encoding="utf-8")
print("index.html:", len(html.encode()), "bytes")
