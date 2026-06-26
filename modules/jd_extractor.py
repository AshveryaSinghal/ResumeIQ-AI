"""
jd_extractor.py
Given a job posting URL, fetch the page and pull out the visible text.
We don't try to be a universal scraper for every careers site (LinkedIn /
Workday pages are often behind JS or login walls) — instead we grab the
readable text and let the LLM do structured extraction of title/company/
skills/responsibilities/qualifications from that raw text. If the fetch
fails (blocked, JS-only page, etc.) we tell the caller so the UI can fall
back to "paste the JD text instead".
"""

import re
import requests
from bs4 import BeautifulSoup


HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    )
}


class JDFetchError(Exception):
    pass


def fetch_jd_text_from_url(url: str, timeout: int = 12) -> str:
    """Fetch a job posting URL and return cleaned visible text."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=timeout)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise JDFetchError(f"Could not fetch the job link ({e}). "
                            f"Paste the job description text instead.")

    soup = BeautifulSoup(resp.text, "html.parser")

    # Strip script/style/nav/footer noise
    for tag in soup(["script", "style", "noscript", "header", "footer", "nav", "svg"]):
        tag.decompose()

    text = soup.get_text(separator="\n")
    # Collapse excessive blank lines
    lines = [l.strip() for l in text.split("\n")]
    lines = [l for l in lines if l]
    cleaned = "\n".join(lines)

    if len(cleaned) < 200:
        raise JDFetchError(
            "The page returned almost no readable text (it may require "
            "JavaScript or a login). Paste the job description text instead."
        )

    # Cap length so we don't blow up the LLM prompt with page chrome/junk
    return cleaned[:15000]
