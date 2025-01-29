import streamlit as st
import json
import os
import pandas as pd
from io import BytesIO
from datetime import datetime

# File paths
FILTERED_JSON_FILE = os.path.join(os.getcwd(), "filtered_feeds.json")
IMPORTANT_ENTRIES_FILE = os.path.join(os.getcwd(), "important_entries.json")

# Load filtered entries
def load_filtered_entries():
    try:
        with open(FILTERED_JSON_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
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

# Convert important entries to an Excel file
def generate_excel(important_entries):
    if not important_entries:
        return None

    df = pd.DataFrame(important_entries)
    df = df[["title", "published", "summary", "link", "keywords"]]  # Reorder columns
    df["keywords"] = df["keywords"].apply(lambda x: ", ".join(x))  # Convert list to string

    output = BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Important Entries")
        workbook = writer.book
        worksheet = writer.sheets["Important Entries"]

        # Adjust column widths
        worksheet.set_column("A:A", 40)  # Title
        worksheet.set_column("B:B", 20)  # Published Date
        worksheet.set_column("C:C", 50)  # Summary
        worksheet.set_column("D:D", 30)  # Link
        worksheet.set_column("E:E", 30)  # Keywords

    output.seek(0)
    return output

# Streamlit App
def main():
    # Use full-page layout
    st.set_page_config(layout="wide")

    # Load filtered and important entries
    filtered_entries = load_filtered_entries()
    important_entries = load_important_entries()

    # Set up layout: two columns (left for filtered entries, right for important entries)
    col1, col2 = st.columns([2, 1])  # Wider left column

    with col1:
        st.title("Filtered RSS Feeds")
        st.write("This app allows you to review and mark important RSS feed entries.")

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

        # 📥 Download Excel Button
        if important_entries:
            excel_data = generate_excel(important_entries)
            if excel_data:
                st.download_button(
                    label="📥 Download Important Entries as Excel",
                    data=excel_data,
                    file_name="important_entries.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

        # Display important entries
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
