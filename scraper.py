import requests
from bs4 import BeautifulSoup
import certifi


def fetch_website_contents(url: str) -> str:
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(
        url,
        headers=headers,
        timeout=10,
        verify=False
    )
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove scripts & styles
    for script in soup(["script", "style", "nav", "footer", "header"]):
        script.decompose()

    text = soup.get_text(separator=" ")

    # Clean extra spaces
    cleaned_text = " ".join(text.split())

    # Optional: limit size (important for LLM tokens)
    return cleaned_text[:15000]