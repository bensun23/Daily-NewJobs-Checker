import smtplib
import requests
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup

SENT_JOBS_FILE = "sent_jobs.txt"

# --------------------------
# Email Notification
# --------------------------
def send_email(subject, body):
    email_user = os.getenv("GMAIL_EMAIL")
    email_pass = os.getenv("GMAIL_PASSWORD")
    email_to = os.getenv("DESTINATION_EMAIL")

    msg = MIMEMultipart()
    msg["From"] = email_user
    msg["To"] = email_to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(email_user, email_pass)
    server.sendmail(email_user, email_to, msg.as_string())
    server.quit()

    print("✅ Email sent")

# --------------------------
# Telegram Notification
# --------------------------
def send_telegram_message(message):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, data={"chat_id": chat_id, "text": message})

    print("✅ Telegram sent")

# --------------------------
# Sent Jobs Tracking
# --------------------------
def load_sent_jobs():
    if not os.path.exists(SENT_JOBS_FILE):
        return set()
    with open(SENT_JOBS_FILE, "r") as f:
        return set(f.read().splitlines())

def save_sent_jobs(jobs):
    with open(SENT_JOBS_FILE, "a") as f:
        for job in jobs:
            f.write(job + "\n")

# --------------------------
# Job Sources (RSS)
# --------------------------
def fetch_jobs():
    sources = [
        ("Indeed", "https://in.indeed.com/rss?q=data+science+fresher"),
        ("Google Jobs", "https://www.google.com/search?q=AI+ML+fresher+jobs+India&output=rss"),
        ("Startup Jobs", "https://www.google.com/search?q=startup+ai+ml+jobs+India&output=rss"),
    ]

    jobs = []

    for source, url in sources:
        response = requests.get(url, timeout=20)
        soup = BeautifulSoup(response.text, "xml")

        for item in soup.find_all("item")[:10]:
            title = item.title.text.strip()
            link = item.link.text.strip()
            jobs.append(f"[{source}] {title}\n{link}")

    print(f"🔍 Total jobs fetched: {len(jobs)}")
    return jobs

# --------------------------
# Main Logic
# --------------------------
def check_jobs():
    sent_jobs = load_sent_jobs()
    all_jobs = fetch_jobs()

    new_jobs = [job for job in all_jobs if job not in sent_jobs]

    if new_jobs:
        message = "🔥 NEW JOBS FOUND 🔥\n\n" + "\n\n".join(new_jobs)
        send_email("Daily Job Alerts 🚀", message)
        send_telegram_message(message)
        save_sent_jobs(new_jobs)
        print(f"✅ Sent {len(new_jobs)} new jobs")
    else:
        msg = "ℹ️ No new jobs found today. Bot is working correctly."
        send_email("Job Alert – No New Jobs", msg)
        send_telegram_message(msg)
        print(msg)

if __name__ == "__main__":
    check_jobs()
