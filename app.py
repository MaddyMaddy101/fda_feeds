import streamlit as st
import json
import os
import subprocess
from datetime import datetime

# File paths
FILTERED_JSON_FILE = os.path.join(os.getcwd(), "filtered_feeds.json")
IMPORTANT_ENTRIES_FILE = os.path.join(os.getcwd(), "important_entries.json")
KEYWORDS_FILE = os.path.join(os.getcwd(), "keywords.json")

# Default keywords
DEFAULT_KEYWORDS = [
    "CDx", "companion diagnostics", "FDA approval", "biomarker selection",
    "predictive biomarker", "KRAS", "PD-L1", "PIK3CA", "NFL", "ctDNA", "digital pathology"
]

# Load filtered entries
def load_filtered_entries():
    try:
        with open(FILTERED_JSON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        st.warning(f"No filtered feed file found: {FILTERED_JSON_FILE}")
        return []

# Load important entries
def load_important_entries():
    try:
        with open(IMPORTANT_ENTRIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []

# Save important entries
def save_important_entries(entries):
    with open(IMPORTANT_ENTRIES_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=4)

# Save keywords
def save_keywords(keywords):
    with open(KEYWORDS_FILE, "w", encoding="utf-8") as f:
        json.dump(keywords, f, indent=4)

# Fetch feeds by running fetch_feeds.py
def fetch_feeds():
    try:
        result = subprocess.run(["python", "fetch_feeds.py"], capture_output=True, text=True, check=True)
        st.success("Feeds successfully updated!")
        st.write(result.stdout)
    except subprocess.CalledProcessError as e:
        st.error("An error occurred while fetching feeds.")
        st.write(e.stdout)
        st.write(e.stderr)

# Load keywords
def load_keywords():
    try:
        with open(KEYWORDS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return DEFAULT_KEYWORDS

# Streamlit App
def main():
    # Use full-page layout
    st.set_page_config(layout="wide")

    # Set up layout: two columns (left for filtered entries, right for important entries)
    col1, col2 = st.columns([2, 1])  # Wider left column

    with col1:
        st.title("Filtered RSS Feeds")
        st.write("This app allows you to review and mark important RSS feed entries.")

        # Section to update keywords
        st.subheader("Update Keywords")
        current_keywords = load_keywords()
        keywords_input = st.text_area(
            "Enter keywords (comma-separated):",
            value=", ".join(current_keywords),
            placeholder="e.g., biomarker, FDA approval, KRAS",
        )
        if st.button("Update and Fetch Feeds"):
            new_keywords = [kw.strip() for kw in keywords_input.split(",") if kw.strip()]
            save_keywords(new_keywords)  # Save updated keywords to file
            fetch_feeds()  # Trigger fetch_feeds.py
            st.experimental_rerun()  # Reload Streamlit page

        # Load filtered entries
        filtered_entries = load_filtered_entries()
        important_entries = load_important_entries()

        # Section to display filtered entries
        st.subheader("Filtered Entries")
        if not filtered_entries:
            st.info("No filtered entries to display.")
        else:
            for idx, entry in enumerate(filtered_entries):  # Add index for unique keys
                st.markdown(f"### [{entry['title']}]({entry['link']})")
                st.markdown(f"**Published:** {entry['published']}")
                st.markdown(f"**Summary:** {entry['summary']}")
                st.markdown(f"**Matched Keywords:** {', '.join(entry.get('keywords', []))}")

                # Checkbox to mark/unmark the entry as important
                if st.checkbox("Mark as important", key=f"{entry['link']}_{idx}"):  # Unique key
                    if entry not in important_entries:
                        important_entries.append(entry)
                else:
                    if entry in important_entries:
                        important_entries.remove(entry)

                st.write("---")

        # Save the important entries persistently
        save_important_entries(important_entries)

    with col2:
        # Section to display important entries
        st.subheader("Important Entries")
        if not important_entries:
            st.info("No important entries marked yet.")
        else:
            for entry in important_entries:
                st.markdown(f"### [{entry['title']}]({entry['link']})")
                st.markdown(f"**Published:** {entry['published']}")
                st.markdown(f"**Summary:** {entry['summary']}")
                st.markdown(f"**Matched Keywords:** {', '.join(entry.get('keywords', []))}")
                st.write("---")

if __name__ == "__main__":
    main()
