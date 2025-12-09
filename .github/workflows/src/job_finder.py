import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import json
from bs4 import BeautifulSoup

# --------------------------
# File to track sent jobs
# --------------------------
SENT_FILE = "sent_jobs.json"

def load_sent_jobs():
    if os.path.exists(SENT_FILE):
        with open(SENT_FILE, "r") as f:
            return json.load(f)
    return []

def save_sent_jobs(sent_jobs):
    with open(SENT_FILE, "w") as f:
        json.dump(sent_jobs, f)

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

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email_user, email_pass)
        server.sendmail(email_user, email_to, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print("Email failed:", e)

# --------------------------
# Telegram Notification
# --------------------------
def send_telegram_message(message):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = {"chat_id": chat_id, "text": message}

    try:
        r = requests.post(url, data=data)
        print("Telegram sent:", r.text)
    except Exception as e:
        print("Telegram failed:", e)

# --------------------------
# Naukri Job Scraper
# --------------------------
def fetch_naukri_jobs():
    url = "https://www.naukri.com/software-developer-jobs"  # Change query as needed
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    jobs = []
    for job_card in soup.find_all("article", class_="jobTuple"):
        title_tag = job_card.find("a", class_="title")
        company_tag = job_card.find("a", class_="subTitle")
        if title_tag and company_tag:
            title = title_tag.text.strip()
            company = company_tag.text.strip()
            link = title_tag["href"]
            jobs.append(f"{title} - {company}\n{link}")
    return jobs

# --------------------------
# Job Check Function
# --------------------------
def check_jobs():
    scraped_jobs = fetch_naukri_jobs()
    sent_jobs = load_sent_jobs()
    new_jobs = [job for job in scraped_jobs if job not in sent_jobs]

    if new_jobs:
        body = "New Jobs Found:\n\n" + "\n\n".join(new_jobs)
        send_email("New Job Alerts", body)
        send_telegram_message(body)

        # Update sent jobs file
        sent_jobs.extend(new_jobs)
        save_sent_jobs(sent_jobs)
        print(f"Sent {len(new_jobs)} new jobs.")
    else:
        print("No new jobs today.")

if __name__ == "__main__":
    check_jobs()
