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
# Fetch Jobs from Multiple Sources
# --------------------------
def fetch_jobs():
    sources = [
        # Indeed jobs RSS
        ("Indeed", "https://in.indeed.com/rss?q=software+developer+fresher"),
        # AngelList / Startup jobs RSS (example)
        ("AngelList", "https://angel.co/jobs?keywords=ai&remote=true"),
        # Freshersworld RSS (example)
        ("Freshersworld", "https://www.freshersworld.com/rss/jobs/software-developer")
    ]

    jobs = []

    for source, url in sources:
        try:
            response = requests.get(url, timeout=20)
            soup = BeautifulSoup(response.text, "html.parser")
            for item in soup.find_all("item")[:10]:  # fetch first 10 items
                title = item.find("title")
                link = item.find("link")
                if not title or not link:
                    continue
                jobs.append(f"[{source}] {title.text.strip()}\n{link.text.strip()}")
        except Exception as e:
            print(f"⚠️ Failed to fetch from {source}: {e}")

    print(f"🔍 Total jobs fetched: {len(jobs)}")
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
    sent_jobs = load_sent_jobs()
    all_jobs = fetch_jobs()
    filtered_jobs = filter_jobs(all_jobs)
    new_jobs = [j for j in filtered_jobs if j not in sent_jobs]

    if not new_jobs:
        print("ℹ️ Silent mode: no new jobs found")
        return  # silent mode, do not send notifications

    message = "🔥 NEW JOB ALERTS 🔥\n\n" + "\n\n".join(new_jobs)
    send_email("Daily Job Alerts 🚀", message)
    send_telegram_message(message)
    save_sent_jobs(new_jobs)
    print(f"✅ Sent {len(new_jobs)} new jobs")

if __name__ == "__main__":
    check_jobs()
