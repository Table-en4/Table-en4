#!/usr/bin/env python3
"""Fetch all GitHub repos (public + private) for profile README generation."""

import json
import os
import sys
import urllib.request

TOKEN = os.environ.get("GITHUB_TOKEN")
if not TOKEN:
    print("Error: set GITHUB_TOKEN first.")
    print("Example: GITHUB_TOKEN=ghp_xxx python3 fetch_repos.py")
    sys.exit(1)

API = "https://api.github.com"


def api_get(path: str):
    req = urllib.request.Request(
        f"{API}{path}",
        headers={
            "Authorization": f"Bearer {TOKEN}",
            "Accept": "application/vnd.github+json",
            "User-Agent": "Table-en4-profile-readme",
        },
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read().decode())


user = api_get("/user")
login = user["login"]
print(f"Fetching repos for: {login}")

all_repos = []
for page in range(1, 4):
    batch = api_get(
        f"/user/repos?affiliation=owner&per_page=100&page={page}&sort=updated"
    )
    if not batch:
        break
    all_repos.extend(batch)
    if len(batch) < 100:
        break

seen = set()
repos = []
for r in all_repos:
    if r["id"] in seen:
        continue
    seen.add(r["id"])
    repos.append(
        {
            "name": r.get("name"),
            "description": r.get("description"),
            "language": r.get("language"),
            "stars": r.get("stargazers_count", 0),
            "private": r.get("private", False),
            "updated": r.get("updated_at"),
            "url": r.get("html_url"),
            "topics": r.get("topics", []),
            "fork": r.get("fork", False),
        }
    )

repos.sort(key=lambda x: (x["stars"], x["updated"] or ""), reverse=True)

with open("repos_full.json", "w", encoding="utf-8") as f:
    json.dump(repos, f, indent=2, ensure_ascii=False)

public = sum(1 for r in repos if not r["private"])
private = sum(1 for r in repos if r["private"])
print(f"Saved {len(repos)} repos to repos_full.json ({public} public, {private} private)")
