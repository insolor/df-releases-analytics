import json
from pathlib import Path
import re
from typing import Any
import requests
from datetime import datetime

# Docs: https://developer.valvesoftware.com/wiki/Steam_Web_API#GetNewsForApp_(v0002)
news_request_url = "https://api.steampowered.com/ISteamNews/GetNewsForApp/v0002/"
df_app_id = 975370


root_dir = Path(__file__).parent
betas_json = root_dir / "betas.json"


def get_last_posts(*, count) -> list[dict[str, Any]]:
    response = requests.get(
        news_request_url,
        params=dict(appid=df_app_id, count=count, maxlength=1, format="json"),
    )
    response.raise_for_status()
    return response.json()["appnews"]["newsitems"]


def parse_beta(title: str) -> str | None:
    """
    Check title, if it's a beta, return the beta number, or else returns None
    """
    result = re.search(r"beta\s*(\d+)", title, re.IGNORECASE)
    if result:
        return result.group(1)

    title = title.lower()

    if "beta branch" in title or "adventur mode beta" in title:
        return "unknown"

    return None


def main() -> None:
    if betas_json.exists():
        betas = json.loads(betas_json.read_text())
        known_betas = {(item["release_date"], item["version_number"]) for item in betas}
    else:
        betas = []
        known_betas = set()

    posts = get_last_posts(count=10)

    for post in posts:
        if "steam_community_announcements" not in post["url"]:
            continue

        beta_number = parse_beta(post["title"])

        if beta_number:
            version = f"beta {beta_number}"
            date = datetime.fromtimestamp(post["date"]).date()
            item = {"name": version, "version_number": version, "release_date": date.isoformat()}
            key = (item["release_date"], item["version_number"])

            if key not in known_betas:
                known_betas.add(key)
                betas.append(item)

    betas_json.write_text(json.dumps(betas, indent=2))


if __name__ == "__main__":
    main()
