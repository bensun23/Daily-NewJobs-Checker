import smtplib
import requests
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup

SENT_JOBS_FILE = "sent_jobs.txt"

# --------------------------
# Filter keywords
# --------------------------
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

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(msg["From"], os.getenv("GMAIL_PASSWORD"))
        server.sendmail(msg["From"], msg["To"], msg.as_string())
        server.quit()
        print("✅ Email sent")
    except Exception as e:
        print("❌ Email failed:", e)

# --------------------------
# Telegram
# --------------------------
def send_telegram_message(message):
    try:
        url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage"
        requests.post(url, data={"chat_id": os.getenv("TELEGRAM_CHAT_ID"), "text": message})
        print("✅ Telegram sent")
    except Exception as e:
        print("❌ Telegram failed:", e)

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
# Fetch jobs from multiple sources
# --------------------------
def fetch_jobs():
    sources = [
        ("Indeed", "https://in.indeed.com/rss?q=software+developer+fresher"),
        ("Naukri", "https://www.naukri.com/software-developer-jobs/rss"),
        ("AngelList", "https://angel.co/jobs?keywords=ai&remote=true"),
        ("Freshersworld", "https://www.freshersworld.com/rss/jobs/software-developer"),
        ("LinkedIn", "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=AI+ML+Fresher")
    ]

    jobs = []

    for source, url in sources:
        try:
            response = requests.get(url, timeout=20)
            soup = BeautifulSoup(response.text, "html.parser")
            for item in soup.find_all("item")[:10]:
                title = item.find("title")
                link = item.find("link")
                if not title or not link:
                    continue
                jobs.append(f"[{source}] {title.text.strip()}\n{link.text.strip()}")
        except Exception as e:
            print(f"⚠️ Failed to fetch jobs from {source}: {e}")

    print(f"🔍 Total jobs fetched: {len(jobs)}")
    return jobs

# --------------------------
# Filter jobs
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

    if new_jobs:
        message = "🔥 NEW JOB ALERTS 🔥\n\n" + "\n\n".join(new_jobs)
        send_email("Daily Job Alerts 🚀", message)
        send_telegram_message(message)
        save_sent_jobs(new_jobs)
        print(f"✅ Sent {len(new_jobs)} new jobs")
    else:
        msg = "ℹ️ No new jobs found today. Bot ran successfully, but no jobs matched your criteria."
        send_email("Daily Job Alert – No Jobs", msg)
        send_telegram_message(msg)
        print(msg)
    if not new_jobs:
        msg = "ℹ️ No new jobs found. Bot ran successfully, but no jobs matched today."
        send_email("Job Update – No Jobs Found", msg)
        send_telegram_message(msg)
        print("📭 No jobs found notification sent")
        return


if __name__ == "__main__":
    check_jobs()
