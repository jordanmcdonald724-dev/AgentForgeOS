import requests
from bs4 import BeautifulSoup

def perform_web_search(query, num_results=10):
    """Perform a web search and return the top results."""
    search_url = f"https://www.google.com/search?q={query}&num={num_results}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(search_url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch search results: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    results = []

    for g in soup.find_all('div', class_='tF2Cxc'):
        title = g.find('h3').text if g.find('h3') else "No title"
        link = g.find('a')['href'] if g.find('a') else "No link"
        results.append({"title": title, "link": link})

    return results

def fetch_webpage_content(url):
    """Fetch the main content of a webpage."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch webpage: {response.status_code}")

    soup = BeautifulSoup(response.text, "html.parser")
    return soup.get_text()