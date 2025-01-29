import streamlit as st
import json
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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

# Send email with important entries
def send_email(receiver_email, important_entries):
    sender_email = "your_email@example.com"  # Replace with your email
    sender_password = "your_password"  # Replace with your email password or app password
    smtp_server = "smtp.gmail.com"  # Change if using a different email provider
    smtp_port = 587  # Usually 587 for TLS

    if not important_entries:
        return "No important entries to send."

    # Create the email content
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = "Your Important RSS Feeds"

    email_body = "Here are your saved important RSS feed entries:\n\n"
    for entry in important_entries:
        email_body += f"🔹 **{entry['title']}**\n"
        email_body += f"📅 Published: {entry['published']}\n"
        email_body += f"🔗 [Read More]({entry['link']})\n"
        email_body += f"📝 Summary: {entry['summary']}\n"
        email_body += f"🔍 Matched Keywords: {', '.join(entry.get('keywords', []))}\n\n"
        email_body += "---\n\n"

    msg.attach(MIMEText(email_body, "plain"))

    # Send the email
    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        return "Email sent successfully!"
    except Exception as e:
        return f"Error sending email: {e}"

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
        
        # 📩 Email input box
        email_input = st.text_input("Enter your email to receive important feeds:", "")

        # 📤 Send Email Button
        if st.button("Send Important Entries via Email"):
            if email_input:
                result = send_email(email_input, important_entries)
                st.success(result)
            else:
                st.warning("Please enter a valid email address.")

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
