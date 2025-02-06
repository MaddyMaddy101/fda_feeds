import requests
from bs4 import BeautifulSoup
import feedparser
import json
import re
from urllib.parse import urljoin
from datetime import datetime

# Initial page URLs to scrape for RSS feeds
PAGE_URLS = [
    "https://www.fda.gov/about-fda/contact-fda/subscribe-podcasts-and-news-feeds",
    "https://www.genomeweb.com/rss-feeds",
    "https://www.360dx.com/?_ga=2.75407509.662637671.1738042591-1931528450.1736367524",
    "https://www.biocentury.com/home",
    "https://www.biopharmadive.com/",
    "https://www.fiercebiotech.com/fiercebiotechcom/rss-feeds",
    "https://www.sciencedaily.com/",
    "https://endpts.com/channel/news-briefing/",
    "https://seekingalpha.com/"
]

# Keywords to filter
KEYWORDS = ["CDx", "companion diagnostics", "biomarker selection", 
            "predictive biomarker", "KRAS", "PD-L1", "PIK3CA", "NFL", "ctDNA", "digital pathology",
            "CCR8", "Veracyte", "Lymphmark"]

# Output file
OUTPUT_JSON = "filtered_feeds.json"

# Set maximum scraping depth
MAX_DEPTH = 2

def load_existing_entries():
    """Loads existing entries from the JSON file."""
    try:
        with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_entries(entries):
    """Saves the entries to the JSON file."""
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=4)

def extract_rss_links(page_url, depth=1):
    """Recursively extracts RSS feed links up to MAX_DEPTH levels."""
    if depth > MAX_DEPTH:
        return []

    try:
        response = requests.get(page_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        # Find RSS links
        rss_links = []
        for tag in soup.find_all(["link", "a"], href=True):
            href = tag["href"]
            if "rss" in href.lower():  # Filter links containing "rss"
                full_url = urljoin(page_url, href)  # Resolve relative URLs
                if full_url not in rss_links:
                    rss_links.append(full_url)

        # Recursively scrape linked pages for deeper layers
        next_links = [urljoin(page_url, a["href"]) for a in soup.find_all("a", href=True)]
        for link in next_links:
            rss_links.extend(extract_rss_links(link, depth + 1))

        return list(set(rss_links))  # Remove duplicates

    except Exception as e:
        print(f"Error fetching {page_url}: {e}")
        return []

def fetch_and_filter_feeds(rss_urls):
    """Fetches and filters RSS feeds based on specified keywords."""
    existing_entries = load_existing_entries()  # Load previous data
    existing_links = {entry["link"] for entry in existing_entries}  # Set for fast lookup

    new_entries = []  # Stores new valid entries
    keyword_patterns = [re.compile(rf'\b{re.escape(keyword)}\b', re.IGNORECASE) for keyword in KEYWORDS]

    for url in rss_urls:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                title = entry.get("title", "")
                summary = entry.get("summary", "")
                link = entry.get("link", "")
                published = entry.get("published", "Unknown Date")

                # Find matching keywords
                matching_keywords = [
                    keyword for keyword, pattern in zip(KEYWORDS, keyword_patterns)
                    if pattern.search(title) or pattern.search(summary)
                ]

                # Only add if it matches the criteria and is not a duplicate
                if matching_keywords and link not in existing_links:
                    new_entries.append({
                        "title": title,
                        "summary": summary,
                        "link": link,
                        "published": published,
                        "keywords": matching_keywords
                    })
                    existing_links.add(link)  # Add to set to avoid duplicates

        except Exception as e:
            print(f"Error fetching {url}: {e}")

    # Combine old and new entries
    updated_entries = existing_entries + new_entries

    # Save updated data
    save_entries(updated_entries)

    print(f"Added {len(new_entries)} new entries. Total entries: {len(updated_entries)}")

if __name__ == "__main__":
    # Step 1: Extract RSS feed links from the provided URLs
    all_rss_urls = []
    for page_url in PAGE_URLS:
        rss_links = extract_rss_links(page_url)
        print(f"RSS links found on {page_url}: {rss_links}")
        all_rss_urls.extend(rss_links)

    # Step 2: Fetch and filter RSS feeds
    fetch_and_filter_feeds(all_rss_urls)
