import feedparser
import json
from datetime import datetime

# RSS Feeds List
RSS_FEEDS = [
    "https://www.fda.gov/about-fda/contact-fda/subscribe-podcasts-and-news-feeds",
    "https://www.genomeweb.com/rss-feeds",
    "https://www.genomeweb.com/section/rss/news"
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

def fetch_and_filter_feeds():
    filtered_entries = []
    
    for url in RSS_FEEDS:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries:
                title = entry.get("title", "")
                summary = entry.get("summary", "")
                link = entry.get("link", "")
                published = entry.get("published", "Unknown Date")

                # Check if any keyword is in the title or summary
                if any(keyword.lower() in title.lower() or keyword.lower() in summary.lower() for keyword in KEYWORDS):
                    filtered_entries.append({
                        "title": title,
                        "summary": summary,
                        "link": link,
                        "published": published
                    })

        except Exception as e:
            print(f"Error fetching {url}: {e}")

    # Save filtered feeds to a JSON file
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(filtered_entries, f, indent=4)

    # Save filtered feeds to a Markdown file
    with open(OUTPUT_MARKDOWN, "w", encoding="utf-8") as f:
        f.write("# Filtered RSS Feeds\n\n")
        f.write(f"**Last Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        
        if filtered_entries:
            for entry in filtered_entries:
                f.write(f"### [{entry['title']}]({entry['link']})\n")
                f.write(f"**Published:** {entry['published']}\n\n")
                f.write(f"**Summary:** {entry['summary']}\n\n")
                f.write("---\n\n")
        else:
            f.write("No articles matched the specified keywords.\n")

    print(f"Filtered feeds saved to {OUTPUT_JSON} and {OUTPUT_MARKDOWN}")

if __name__ == "__main__":
    fetch_and_filter_feeds()
