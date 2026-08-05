import requests
from bs4 import BeautifulSoup

from .vector_store import add_document


def ingest_url(url: str):
    """
    Fetch webpage, extract text, store in vector DB.
    """
    html = requests.get(
        url,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30
    ).text

    soup = BeautifulSoup(html, "lxml")
    text = soup.get_text(separator="\n")

    add_document(url, text)
    return True
