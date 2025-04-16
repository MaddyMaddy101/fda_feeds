import requests
from bs4 import BeautifulSoup
import feedparser
import json
import re
import pandas as pd
from urllib.parse import urljoin
from datetime import datetime

# Initial page URLs to scrape for RSS feeds
PAGE_URLS = [
    "https://www.genomeweb.com/rss-feeds",
    "https://www.360dx.com/?_ga=2.75407509.662637671.1738042591-1931528450.1736367524",
    "https://www.biocentury.com/home",
    "https://www.biopharmadive.com/",
    "https://www.fiercebiotech.com/fiercebiotechcom/rss-feeds",
    "https://www.sciencedaily.com/",
    "https://endpts.com/channel/news-briefing/",
    "https://seekingalpha.com/",
    "https://clinicaltrials.gov/"
]

# Keywords to filter
KEYWORDS = ["CDx", "companion diagnostics", "companion diagnostic"]

# Output files
OUTPUT_JSON = "filtered_feeds.json"
OUTPUT_MARKDOWN = "Filtered-Feeds.md"
OUTPUT_EXCEL = "filtered_feeds.xlsx"

# Set maximum scraping depth
MAX_DEPTH = 2

def load_existing_entries():
    """Loads existing RSS feed entries from JSON file."""
    try:
        with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_entries(entries):
    """Saves the combined RSS entries back to JSON file."""
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=4)

def save_to_excel(entries):
    """Saves filtered feeds to an Excel file including Title, Link, and Keywords."""
    if not entries:
        print("No data to save in Excel.")
        return

    df = pd.DataFrame(entries)
    df = df[["link", "keywords", "title"]]  # Keep URL, Keywords, and Title
    df["keywords"] = df["keywords"].apply(lambda x: ", ".join(x))  # Convert list to string

    with pd.ExcelWriter(OUTPUT_EXCEL, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Filtered Feeds")
        worksheet = writer.sheets["Filtered Feeds"]

        # Adjust column widths
        worksheet.set_column("A:A", 60)  # Link
        worksheet.set_column("B:B", 30)  # Keywords
        worksheet.set_column("C:C", 50)  # Title

    print(f"✅ RSS feeds saved to {OUTPUT_EXCEL}")

def update_markdown(entries):
    """Saves the filtered RSS feeds to a Markdown file for the Wiki."""
    with open(OUTPUT_MARKDOWN, "w", encoding="utf-8") as f:
        f.write("# Filtered RSS Feeds\n\n")
        f.write(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        if entries:
            f.write("## Filtered Entries\n\n")
            for entry in entries:
                f.write(f"### [{entry['title']}]({entry['link']})\n")
                f.write(f"**Published:** {entry['published']}\n\n")
                f.write(f"**Summary:** {entry['summary']}\n\n")
                f.write(f"**Matched Keywords:** {', '.join(entry['keywords'])}\n\n")
                f.write("---\n\n")
        else:
            f.write("## No new articles matched the specified keywords.\n\n")

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
            if "rss" in href.lower():
                full_url = urljoin(page_url, href)
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
    existing_entries = load_existing_entries()
    existing_links = {entry["link"] for entry in existing_entries}  # Use a set for fast lookup

    new_entries = []
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

                # Only add if it matches criteria and is NOT a duplicate
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

    # Save the updated list
    save_entries(updated_entries)
    save_to_excel(updated_entries)  # Save to Excel
    update_markdown(updated_entries)  # Save to Markdown

    print(f"✅ Added {len(new_entries)} new entries. Total entries: {len(updated_entries)}")

if __name__ == "__main__":
    all_rss_urls = []
    for page_url in PAGE_URLS:
        rss_links = extract_rss_links(page_url)
        all_rss_urls.extend(rss_links)

    fetch_and_filter_feeds(all_rss_urls)
