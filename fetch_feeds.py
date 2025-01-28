import requests
from bs4 import BeautifulSoup
import feedparser
import json
import re
from datetime import datetime

# List of page URLs to scrape for RSS feeds
PAGE_URLS = [
    "https://www.fda.gov/about-fda/contact-fda/subscribe-podcasts-and-news-feeds",
    "https://www.genomeweb.com/rss-feeds",
    "https://www.360dx.com/?_ga=2.75407509.662637671.1738042591-1931528450.1736367524",
    "https://www.biocentury.com/home",
    "https://www.biopharmadive.com/",
    "https://www.fiercebiotech.com/fiercebiotechcom/rss-feeds",
    "https://www.sciencedaily.com/",
    "https://endpts.com/channel/news-briefing/"
]

# Keywords to filter
KEYWORDS = ["CDx", "companion diagnostics", "FDA approval", "biomarker selection", 
            "predictive biomarker", "KRAS", "PD-L1", "PIK3CA", "NFL", "ctDNA", "digital pathology"]

# Output files
OUTPUT_JSON = "filtered_feeds.json"
OUTPUT_MARKDOWN = "Filtered-Feeds.md"

def extract_rss_links(page_url):
    """Extracts RSS feed links from a given webpage URL, filtering only links containing 'rss'."""
    try:
        response = requests.get(page_url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        rss_links = []
        for tag in soup.find_all(["link", "a"], href=True):
            href = tag["href"]
            if "rss" in href.lower():  # Check if the link contains 'rss' (case-insensitive)
                if href.startswith("/"):  # Handle relative URLs
                    href = page_url + href
                rss_links.append(href)
        
        return rss_links

    except Exception as e:
        print(f"Error fetching {page_url}: {e}")
        return []

def fetch_and_filter_feeds(rss_urls):
    """Fetches and filters RSS feeds based on specified keywords."""
    filtered_entries = []
    all_extracted_rss = rss_urls  # Keep track of all RSS links
    
    # Compile regular expressions for whole-word matching of each keyword
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

                if matching_keywords:
                    filtered_entries.append({
                        "title": title,
                        "summary": summary,
                        "link": link,
                        "published": published,
                        "keywords": matching_keywords  # Add matching keywords
                    })

        except Exception as e:
            print(f"Error fetching {url}: {e}")

    # Save filtered feeds to a JSON file
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(filtered_entries, f, indent=4)

    # Save filtered feeds and RSS links to a Markdown file
    with open(OUTPUT_MARKDOWN, "w", encoding="utf-8") as f:
        f.write("# Filtered RSS Feeds\n\n")
        f.write(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        # Section for filtered entries
        if filtered_entries:
            f.write("## Filtered Entries\n\n")
            for entry in filtered_entries:
                f.write(f"### [{entry['title']}]({entry['link']})\n")
                f.write(f"**Published:** {entry['published']}\n\n")
                f.write(f"**Summary:** {entry['summary']}\n\n")
                f.write(f"**Matched Keywords:** {', '.join(entry['keywords'])}\n\n")
                f.write("---\n\n")
        else:
            f.write("## Filtered Entries\n\nNo articles matched the specified keywords.\n\n")
        
        # Section for all extracted RSS links
        f.write("## All Extracted RSS Links\n\n")
        for rss_link in all_extracted_rss:
            f.write(f"- {rss_link}\n")

    print(f"Filtered feeds and RSS links saved to {OUTPUT_JSON} and {OUTPUT_MARKDOWN}")

if __name__ == "__main__":
    # Step 1: Extract RSS feed links from the provided URLs
    all_rss_urls = []
    for page_url in PAGE_URLS:
        rss_links = extract_rss_links(page_url)
        print(f"RSS links found on {page_url}: {rss_links}")
        all_rss_urls.extend(rss_links)

    # Step 2: Fetch and filter RSS feeds
    fetch_and_filter_feeds(all_rss_urls)
