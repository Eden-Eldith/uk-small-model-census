"""Read public GitHub identity evidence explicitly linked from Hub profiles.

Authentication is optional (GH_TOKEN/GITHUB_TOKEN); --git-credential permits an
existing git credential to avoid the public API's small unauthenticated quota.
Only public profile fields are retained. No identity is guessed from usernames.
"""
import argparse
import base64
import json
import os
import subprocess
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlparse

import requests
from collect import ROOT, dump, now


def token_from_git():
    proc = subprocess.run(["git", "credential", "fill"], input="protocol=https\nhost=github.com\n\n", text=True, capture_output=True, timeout=25, env=dict(os.environ, GIT_TERMINAL_PROMPT="0", GCM_INTERACTIVE="Never"))
    fields = dict(line.split("=", 1) for line in proc.stdout.splitlines() if "=" in line)
    return fields.get("password")


def run(wait, git_credential):
    token = os.getenv("GH_TOKEN") or os.getenv("GITHUB_TOKEN") or (token_from_git() if git_credential else None)
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "uk-small-model-census/0.1"}
    if token:
        headers["Authorization"] = "Bearer " + token
    accounts = json.loads((ROOT / "data/raw/accounts.json").read_text(encoding="utf-8"))
    dest = ROOT / "work/github_profiles"
    dest.mkdir(parents=True, exist_ok=True)

    def fetch(account):
        source = json.loads((ROOT / "work/profiles" / (account + ".json")).read_text(encoding="utf-8"))
        links = []
        for link in source.get("links", []):
            u = urlparse(link)
            parts = u.path.strip("/").split("/")
            if u.hostname in ["github.com", "www.github.com"] and len(parts) == 1 and parts[0] and parts[0] not in ["topics", "features", "about", "huggingface"]:
                links.append((parts[0], link))
        rows = []
        for login, link in sorted(set(links)):
            url = "https://api.github.com/users/" + login
            r = requests.get(url, headers=headers, timeout=45)
            row = {"linked_from": source["profile_url"], "linked_url": link, "api_url": url, "retrieved_at": now(), "http_status": r.status_code}
            if r.status_code == 200:
                d = r.json()
                row["profile"] = {k: d.get(k) for k in ["login", "type", "name", "company", "blog", "location", "bio", "html_url", "created_at", "updated_at"]}
                rr = requests.get(f"https://api.github.com/repos/{login}/{login}/readme", headers=headers, timeout=45)
                row["readme_status"] = rr.status_code
                if rr.status_code == 200:
                    rd = rr.json()
                    row["readme_url"] = rd.get("html_url")
                    row["readme_text"] = base64.b64decode(rd["content"]).decode("utf-8", errors="replace")
            rows.append(row)
        result = {"account": account, "retrieved_at": now(), "github_links_checked": rows}
        dump(dest / (account + ".json"), result)
        return account

    deadline = time.monotonic() + (1800 if wait else 0)
    while True:
        missing = [account for account in accounts if not (dest / (account + ".json")).exists()]
        ready = [account for account in missing if (ROOT / "work/profiles" / (account + ".json")).exists()]
        if ready:
            with ThreadPoolExecutor(max_workers=5) as pool:
                for account in pool.map(fetch, ready):
                    pass
            print(f"GitHub identity checks completed for {len(accounts) - len(missing) + len(ready)}/{len(accounts)} Hub profiles", flush=True)
        if not missing or not wait or time.monotonic() > deadline:
            break
        time.sleep(8)


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--wait-for-profiles", action="store_true")
    p.add_argument("--git-credential", action="store_true")
    args = p.parse_args()
    run(args.wait_for_profiles, args.git_credential)
