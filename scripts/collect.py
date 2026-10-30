"""Collect the exact public Hub cohort, then public researcher evidence.

API approach follows HfApi.list_models and the Hub's additional UI query fields.
No authentication, weight downloads, or remote repository code execution.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

ROOT = Path(__file__).resolve().parents[1]
HEADERS = {"User-Agent": "uk-small-model-census/0.1 (public research metadata)"}


def now():
    return datetime.now(timezone.utc).isoformat()


def dump(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def get(url, params=None):
    for attempt in range(6):
        try:
            r = requests.get(url, params=params, headers=HEADERS, timeout=60)
            if r.status_code == 429 or r.status_code >= 500:
                # Respect the service's actual quota reset instead of repeatedly
                # consuming retries inside a multi-minute fixed window.
                delay = float(r.headers.get("Retry-After", 2 ** (attempt + 1)))
                deadline = time.monotonic() + delay + 1
                while time.monotonic() < deadline:
                    time.sleep(min(30, max(0, deadline - time.monotonic())))
                continue
            return r
        except requests.RequestException:
            if attempt == 5:
                raise
            time.sleep(min(2 ** attempt, 20))
    raise RuntimeError(f"Request failed after retries: {url}")


def write_csv(path, records, fields=None):
    path.parent.mkdir(parents=True, exist_ok=True)
    fields = fields or list(records[0])
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        for record in records:
            writer.writerow({k: json.dumps(v, ensure_ascii=False) if isinstance(v, (list, dict)) else v for k, v in record.items() if k in fields})


def page_values(response):
    response.raise_for_status()
    soup = BeautifulSoup(response.text, "html.parser")
    component = soup.find(attrs={"data-target": "ModelList"})
    if not component:
        raise ValueError("ModelList data absent; cannot establish complete website cohort")
    return json.loads(component["data-props"])["initialValues"]


def collect_listing():
    config = json.loads((ROOT / "config/filters.json").read_text())
    started = now()
    ui = {"pipeline_tag": config["task"], "language": config["language"], "library": config["library"], "num_parameters": config["num_parameters"], "base_model_relation": config["base_model_relation"], "sort": config["sort_ui"]}
    first = get("https://huggingface.co/models", ui)
    v0 = page_values(first)
    dump(ROOT / "data/raw/ui_page_000.json", v0)
    total, per_page = v0["numTotalItems"], v0["numItemsPerPage"]
    ui_pages = {0: v0}

    def fetch_ui(i):
        v = page_values(get("https://huggingface.co/models", {**ui, "p": i}))
        dump(ROOT / f"data/raw/ui_page_{i:03d}.json", v)
        return i, v

    with ThreadPoolExecutor(max_workers=4) as pool:
        for future in as_completed([pool.submit(fetch_ui, i) for i in range(1, (total + per_page - 1) // per_page)]):
            i, v = future.result()
            ui_pages[i] = v
    ui_models = [model for i in sorted(ui_pages) for model in ui_pages[i]["models"]]
    ui_by_id = {model["id"]: model for model in ui_models}
    print(f"Website: {len(ui_models)} rows, {len(ui_by_id)} unique; displayed count {total}", flush=True)

    params = {"pipeline_tag": config["task"], "filter": [config["library"], config["language"]], "num_parameters": config["num_parameters"], "base_model_relation": config["base_model_relation"], "sort": config["sort_api"], "direction": -1, "limit": 100, "full": "true", "cardData": "true", "config": "true"}
    url = "https://huggingface.co/api/models"
    raw_models, pages, seen_urls = [], [], set()
    while url:
        if url in seen_urls:
            raise ValueError("Pagination repeated a URL")
        seen_urls.add(url)
        r = get(url, params)
        r.raise_for_status()
        items = r.json()
        if not isinstance(items, list):
            raise ValueError("API did not return a model list")
        dump(ROOT / f"data/raw/api_page_{len(pages):03d}.json", items)
        pages.append({"url": r.url, "retrieved_at": now(), "rows": len(items), "next": r.links.get("next", {}).get("url")})
        raw_models.extend(items)
        print(f"API page {len(pages)}: {len(raw_models)} total rows", flush=True)
        url = r.links.get("next", {}).get("url")
        params = None
    api_by_id = {x["id"]: x for x in raw_models}
    report = {"started_at": started, "finished_at": now(), "filters": config, "ui_url": first.url, "ui_count": total, "ui_rows": len(ui_models), "ui_unique": len(ui_by_id), "api_rows": len(raw_models), "api_unique": len(api_by_id), "ui_missing_from_api": sorted(set(ui_by_id) - set(api_by_id)), "api_missing_from_ui": sorted(set(api_by_id) - set(ui_by_id)), "api_pages": pages}
    dump(ROOT / "data/collection.json", report)
    if len(ui_models) != len(ui_by_id) or len(raw_models) != len(api_by_id) or set(api_by_id) != set(ui_by_id) or total != len(api_by_id):
        raise ValueError("Cohort changed during collection or pagination differs; inspect data/collection.json")
    raw_file = ROOT / "data/raw/models.jsonl"
    with raw_file.open("w", encoding="utf-8") as f:
        for model in raw_models:
            f.write(json.dumps(model, ensure_ascii=False) + "\n")
    rows = []
    authors = {}
    for rank, model in enumerate(raw_models, 1):
        mid = model["id"]
        displayed = ui_by_id[mid]
        owner = model.get("author") or mid.split("/")[0]
        ad = displayed.get("authorData", {})
        card = model.get("cardData") or {}
        n = displayed.get("numParameters")
        rows.append({"model_id": mid, "model_url": f"https://huggingface.co/{mid}", "account": owner, "account_type": ad.get("type", "unknown"), "display_name": ad.get("fullname", ""), "parameters": n, "strictly_under_1b": isinstance(n, (int, float)) and n < 1_000_000_000, "pipeline_tag": model.get("pipeline_tag"), "library_name": model.get("library_name"), "language": card.get("language", []), "tags": model.get("tags", []), "base_model_declared": card.get("base_model", []), "base_model_relation_declared": card.get("base_model_relation", ""), "hub_base_filter_match": True, "created_at": model.get("createdAt"), "modified_at": model.get("lastModified"), "revision": model.get("sha"), "downloads": model.get("downloads"), "likes": model.get("likes"), "license": card.get("license", ""), "rank_recently_updated": rank, "retrieved_at": report["finished_at"]})
        authors.setdefault(owner, {"account": owner, "account_type": ad.get("type", "unknown"), "display_name": ad.get("fullname", ""), "profile_url": f"https://huggingface.co/{owner}", "model_ids": []})["model_ids"].append(mid)
    write_csv(ROOT / "data/models_all.csv", rows)
    write_csv(ROOT / "data/accounts.csv", sorted(authors.values(), key=lambda x: x["account"].lower()))
    dump(ROOT / "data/raw/accounts.json", authors)
    report["accounts"] = len(authors)
    report["strict_under_1b"] = sum(row["strictly_under_1b"] for row in rows)
    report["models_sha256"] = hashlib.sha256(raw_file.read_bytes()).hexdigest()
    dump(ROOT / "data/collection.json", report)
    print(json.dumps({k: report[k] for k in ["api_unique", "accounts", "strict_under_1b", "finished_at"]}), flush=True)


def collect_evidence(cards_only=False):
    models = [json.loads(line) for line in (ROOT / "data/raw/models.jsonl").read_text(encoding="utf-8").splitlines()]
    authors = json.loads((ROOT / "data/raw/accounts.json").read_text(encoding="utf-8"))
    # Local full-text working evidence remains separate from the released metadata.
    work = ROOT / "work"
    errors = []

    def readme(model):
        path = work / "model_cards" / (model["id"].replace("/", "--") + ".md")
        status = path.with_suffix(".status.json")
        if status.exists():
            return json.loads(status.read_text())
        url = f"https://huggingface.co/{model['id']}/raw/{model['sha']}/README.md"
        r = get(url)
        record = {"model_id": model["id"], "url": url, "status": r.status_code, "retrieved_at": now()}
        if r.status_code == 200:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(r.text, encoding="utf-8")
            record["sha256"] = hashlib.sha256(r.content).hexdigest()
        elif r.status_code not in [404, 401, 403]:
            errors.append(record)
        dump(status, record)
        return record

    def profile(item):
        owner, data = item
        folder = work / "profiles"
        path = folder / (owner + ".json")
        if path.exists():
            return json.loads(path.read_text(encoding="utf-8"))
        kind = "organizations" if data["account_type"] == "org" else "users"
        url = f"https://huggingface.co/api/{kind}/{quote(owner)}/overview"
        r = get(url)
        value = {"account": owner, "profile_url": data["profile_url"], "retrieved_at": now(), "api_status": r.status_code, "api_url": url}
        if r.status_code == 200:
            value["overview"] = r.json()
        h = get(data["profile_url"])
        value["html_status"] = h.status_code
        if h.status_code == 200:
            soup = BeautifulSoup(h.text, "html.parser")
            main = soup.find("main") or soup
            value["page_text"] = main.get_text(" ", strip=True)
            value["links"] = sorted(set(a.get("href") for a in main.find_all("a", href=True)))
            value["components"] = [{"component": e.get("data-target"), "props": json.loads(e["data-props"])} for e in main.find_all(attrs={"data-props": True}) if e.get("data-target") not in ["MainHeader", "ModelList", "DatasetList"]]
        dump(path, value)
        return value

    with ThreadPoolExecutor(max_workers=6) as pool:
        jobs = {} if cards_only else {pool.submit(profile, item): item[0] for item in authors.items()}
        for i, future in enumerate(as_completed(jobs), 1):
            try:
                future.result()
            except Exception as exc:
                errors.append({"profile": jobs[future], "error": str(exc)})
            if i % 40 == 0 or i == len(jobs):
                print(f"Profiles {i}/{len(jobs)}", flush=True)
    with ThreadPoolExecutor(max_workers=6) as pool:
        jobs = {pool.submit(readme, model): model["id"] for model in models}
        for i, future in enumerate(as_completed(jobs), 1):
            try:
                future.result()
            except Exception as exc:
                errors.append({"model": jobs[future], "error": str(exc)})
            if i % 80 == 0 or i == len(jobs):
                print(f"Model cards {i}/{len(jobs)}", flush=True)
    dump(work / "collection_errors.json", errors)
    print(f"Evidence retrieval finished; {len(errors)} errors", flush=True)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--stage", choices=["listing", "enrich", "cards", "all"], default="all")
    args = parser.parse_args()
    if args.stage in ["listing", "all"]:
        collect_listing()
    if args.stage in ["enrich", "cards", "all"]:
        collect_evidence(cards_only=args.stage == "cards")
