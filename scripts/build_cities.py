"""Собирает data/cities.json из справочника городов HFLabs.

Источник: https://github.com/hflabs/city (city.csv).
Запуск: python3 scripts/build_cities.py path/to/city.csv data/cities.json

Результат — список групп регионов, отсортированный по населению центра:
[{"t": "Название региона", "fd": "Федеральный округ",
  "c": [[название, широта, долгота, население], ...]}]
Первым в "c" идёт центр региона, дальше города по убыванию населения.
Москва объединена с Московской областью, Петербург — с Ленинградской,
Севастополь — с Крымом.
"""
import csv
import json
import re
import sys


def label(region_type, name):
    if region_type == "обл":
        return name + " область"
    if region_type == "край":
        return name + " край"
    if region_type == "АО":
        return name if "округ" in name.lower() else name + " автономный округ"
    if region_type == "Аобл":
        return name + " автономная область"
    if region_type == "Респ":
        return (name + " Республика") if name.endswith(("ская", "ая")) else "Республика " + name
    return name


FIX = {
    "Кемеровская область - Кузбасс область": "Кемеровская область — Кузбасс",
    "Ханты-Мансийский Автономный округ - Югра": "Ханты-Мансийский АО — Югра",
    "Республика Саха /Якутия/": "Республика Саха (Якутия)",
    "Республика Северная Осетия - Алания": "Северная Осетия — Алания",
}
MERGE = {
    ("г", "Москва"): ("обл", "Московская"),
    ("г", "Санкт-Петербург"): ("обл", "Ленинградская"),
    ("г", "Севастополь"): ("Респ", "Крым"),
}


def main(src, dst):
    rows = list(csv.DictReader(open(src, encoding="utf-8")))
    groups = {}
    for x in rows:
        key = (x["region_type"], x["region"])
        name = re.sub(r"\s+", " ", (x["city"] or x["area"] or x["region"]).replace("\xa0", " ")).strip()
        hub = x["capital_marker"] == "2" or name == "Симферополь"
        if key in MERGE:
            hub = name in ("Москва", "Санкт-Петербург")
            key = MERGE[key]
        g = groups.setdefault(key, {"t": label(*key), "fd": x["federal_district"], "c": [], "hub": None})
        if hub:
            g["hub"] = name
        g["c"].append([name, round(float(x["geo_lat"]), 3), round(float(x["geo_lon"]), 3), int(x["population"] or 0)])

    out = []
    for g in groups.values():
        g["c"].sort(key=lambda c: -c[3])
        names = [c[0] for c in g["c"]]
        hi = names.index(g["hub"]) if g["hub"] else 0
        g["c"].insert(0, g["c"].pop(hi))
        out.append({"t": FIX.get(g["t"], g["t"]).replace(" - ", " — "), "fd": g["fd"], "c": g["c"]})
    out.sort(key=lambda g: -g["c"][0][3])
    json.dump(out, open(dst, "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
    print(f"{len(out)} групп регионов, {sum(len(g['c']) for g in out)} городов → {dst}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
