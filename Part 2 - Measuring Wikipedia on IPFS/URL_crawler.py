import sys
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, urljoin, unquote

def get_links_recursive(url, depth, max_depth, visited, output_file, original_domain):
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
            # print(href)
            if href is not None and ('../' in href or '%' in href or '/wiki/' in href):
                # if depth == 1:
                    # print(href)
                href = href.replace('../A/', '/wiki/', 1)
                href = href.replace('../', '/wiki/', 1)
                if '/wiki/#' in href:
                    continue
                if '#' in href:
                    href = href[:href.index('#')]
                full_url = urljoin(url, href)
                # if depth == 1:
                    # print(href)
                # if depth == 1:
                    # print(full_url)
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
    url = sys.argv[1]
    recursion_depth = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    # Extract domain name from URL
    domain = urlparse(url).netloc
    filename = f"{domain}_links_{recursion_depth}.txt"

    # Clear or create the output file
    with open(filename, 'w') as file:
        pass


    # Perform recursive link scraping
    visited = set()
    get_links_recursive(url, 0, recursion_depth, visited, filename, domain)

    print(f"All unique links on {url} have been saved to {filename}.")
