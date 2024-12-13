from __future__ import annotations

from datetime import date, datetime
import re
from typing import NamedTuple

import requests
from bs4 import BeautifulSoup

import pandas as pd


class ReleaseInfo(NamedTuple):
    name: str
    version_number: str
    release_date: date


def parse_version(version_text: str) -> ReleaseInfo:
    result = re.search(r"DF (.*?) \(([A-Za-z]+) (\d+), (\d{4})\)", version_text)
    if not result:
        raise ValueError(f"Could not parse version text: {version_text}")

    date_text = f"{result.group(2)[:3]} {result.group(3)}, {result.group(4)}"
    release_date = datetime.strptime(date_text, "%b %d, %Y")

    return ReleaseInfo(
        name=f"DF {result.group(1)}",
        version_number=result.group(1),
        release_date=release_date.date(),
    )


def get_release_info() -> pd.DataFrame:
    url = "http://www.bay12games.com/dwarves/older_versions.html"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    page_content = response.content

    soup = BeautifulSoup(page_content, "html.parser")
    body = soup.body

    tables = body.select("table")
    release_table = tables[1]

    result = []

    release_paragraphs = release_table.select("p")
    for paragraph in release_paragraphs:
        if str(paragraph.contents[0]).startswith("<a href="):
            version_text = paragraph.select("a")[0].contents[0]

        else:
            version_text = paragraph.contents[0]

        result.append(parse_version(version_text))

    return pd.DataFrame(reversed(result))


def main():
    df = get_release_info()
    print(df)
    df.to_csv("releases.csv", index=False)


if __name__ == "__main__":
    main()
