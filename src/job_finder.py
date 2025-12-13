import smtplib
import requests
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup

SENT_JOBS_FILE = "sent_jobs.txt"

# Companies you care about
TARGET_COMPANIES = ["google", "amazon", "zoho"]
STARTUP_KEYWORDS = ["startup", "early", "seed", "series"]

# --------------------------
# Email
# --------------------------
def send_email(subject, body):
    msg = MIMEMultipart()
    msg["From"] = os.getenv("GMAIL_EMAIL")
    msg["To"] = os.getenv("DESTINATION_EMAIL")
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(msg["From"], os.getenv("GMAIL_PASSWORD"))
    server.sendmail(msg["From"], msg["To"], msg.as_string())
    server.quit()

    print("✅ Email sent")

# --------------------------
# Telegram
# --------------------------
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage"
    requests.post(
        url,
        data={"chat_id": os.getenv("TELEGRAM_CHAT_ID"), "text": message}
    )
    print("✅ Telegram sent")
    send_telegram_message("✅ Telegram test message from GitHub Actions")

# --------------------------
# Sent Jobs Tracker
# --------------------------
def load_sent_jobs():
    if not os.path.exists(SENT_JOBS_FILE):
        return set()
    return set(open(SENT_JOBS_FILE).read().splitlines())

def save_sent_jobs(jobs):
    with open(SENT_JOBS_FILE, "a") as f:
        for job in jobs:
            f.write(job + "\n")

# --------------------------
# Fetch Jobs (RSS)
# --------------------------
def fetch_jobs():
    sources = [
        ("Indeed", "https://in.indeed.com/rss?q=data+science+fresher"),
        ("Google Jobs", "https://www.google.com/search?q=ai+ml+fresher+jobs+india&output=rss"),
        ("Startup Jobs", "https://www.google.com/search?q=startup+ai+ml+jobs+india&output=rss"),
    ]

    jobs = []

    for source, url in sources:
        response = requests.get(url, timeout=20)
        soup = BeautifulSoup(response.text, "html.parser")  # ✅ FIXED

        for item in soup.find_all("item"):
            title = item.find("title")
            link = item.find("link")

            if not title or not link:
                continue

            jobs.append(f"[{source}] {title.text.strip()}\n{link.text.strip()}")

    return jobs


# --------------------------
# Filter Jobs
# --------------------------
def filter_jobs(jobs):
    filtered = []

    for job in jobs:
        text = job.lower()

        if any(c in text for c in TARGET_COMPANIES):
            filtered.append("🏢 COMPANY JOB\n" + job)

        elif any(k in text for k in STARTUP_KEYWORDS):
            filtered.append("🚀 STARTUP JOB\n" + job)

    return filtered

# --------------------------
# Main
# --------------------------
def check_jobs():
    print("🚀 Job checker started")

    all_jobs = fetch_jobs()
    print(f"🧪 Jobs fetched: {len(all_jobs)}")

    if all_jobs:
        body = "🔥 NEW JOB ALERTS 🔥\n\n" + "\n\n".join(all_jobs[:10])
        send_email("Daily Job Alerts", body)
        send_telegram_message(body)
        print("✅ Notifications sent")
    else:
        print("⚠️ No jobs found — skipping notifications")

if __name__ == "__main__":
    send_email(
        "TEST EMAIL FROM GITHUB ACTIONS",
        "If you received this, Gmail config is working."
    )
