import streamlit as st
import json
from datetime import datetime

import os
# Use the current working directory
FILTERED_JSON_FILE = os.path.join(os.getcwd(), "filtered_feeds.json")
IMPORTANT_ENTRIES_FILE = os.path.join(os.getcwd(), "important_entries.json")

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

# Streamlit App
def main():
    st.title("Filtered RSS Feeds")
    st.write("This app allows you to review and mark important RSS feed entries.")

    # Load filtered and important entries
    filtered_entries = load_filtered_entries()
    important_entries = load_important_entries()

    # Section to display filtered entries
    st.subheader("Filtered Entries")
    if not filtered_entries:
        st.info("No filtered entries to display.")
    else:
        for entry in filtered_entries:
            st.markdown(f"### [{entry['title']}]({entry['link']})")
            st.markdown(f"**Published:** {entry['published']}")
            st.markdown(f"**Summary:** {entry['summary']}")
            st.markdown(f"**Matched Keywords:** {', '.join(entry.get('keywords', []))}")
            
            # Checkbox to mark the entry as important
            if st.checkbox(f"Mark as important", key=f"{entry['link']}"):
                if entry not in important_entries:
                    important_entries.append(entry)

            st.write("---")
    
    # Save the important entries persistently
    save_important_entries(important_entries)

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
