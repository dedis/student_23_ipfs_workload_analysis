import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, unquote
from typing import Set

def get_links_recursive(url: str, depth: int, max_depth: int, visited: Set[str], output_file: str, original_domain: str) -> None:
    """
    Recursively scrapes all links on a webpage and saves them to a file.
    
    Parameters:
    - url: The URL of the webpage to scrape.
    - depth: The current depth of the recursion.
    - max_depth: The maximum depth of recursion.
    - visited: A set of URLs that have already been visited.
    - output_file: The filename of the file to save the links to.
    - original_domain: The domain of the original webpage.
    """
    if depth > max_depth or url in visited:
        return

    visited.add(url)

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
    except Exception as e:
        print(f"Error while fetching the URL '{url}': {e}", file=sys.stderr)
        return

    links = set()

    # Look for the div with id="mw-content-text"
    content_text_div = soup.select_one('#mw-content-text')

    if content_text_div is not None:
        for link in content_text_div.find_all('a'):
            href = link.get('href')
            if href is not None and ('../' in href or '%' in href or '/wiki/' in href):
                href = href.replace('../A/', '/wiki/', 1)
                href = href.replace('../', '/wiki/', 1)
                if '/wiki/#' in href:
                    continue
                if '#' in href:
                    href = href[:href.index('#')]
                full_url = urljoin(url, href)
                link_domain = urlparse(full_url).netloc
                if link_domain == original_domain:
                    links.add(unquote(full_url.replace('https://', '', 1)))

    with open(output_file, 'a') as f:
        for link in links:
            f.write(link + '\n')

    for link in links:
        get_links_recursive(f'https://{link}', depth + 1, max_depth, visited, output_file, original_domain)

if __name__ == "__main__":
    # Get website URL and recursion depth from command line arguments
    url: str = sys.argv[1]
    recursion_depth: int = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    # Extract domain name from URL
    domain: str = urlparse(url).netloc
    filename: str = f"{domain}_links_{recursion_depth}.txt"

    # Clear or create the output file
    with open(filename, 'w') as file:
        pass

    # Perform recursive link scraping
    visited: Set[str] = set()
    get_links_recursive(url, 0, recursion_depth, visited, filename, domain)

    print(f"All unique links on {url} have been saved to {filename}.")
