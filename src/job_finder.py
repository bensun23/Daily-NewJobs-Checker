import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from bs4 import BeautifulSoup

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
    print("Scraping Naukri jobs...")

    url = "https://www.naukri.com/software-developer-jobs"
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

    print(f"Total jobs scraped: {len(jobs)}")
    return jobs


# --------------------------
# Main Job Checker
# --------------------------
def check_jobs():
    jobs = fetch_naukri_jobs()

    if jobs:
        body = "Daily Job Report:\n\n" + "\n\n".join(jobs)
        send_email("Daily Job Report", body)
        send_telegram_message(body)
        print("Sent all jobs.")
    else:
        msg = "No new jobs found today. Bot is working correctly."
        send_email("Daily Job Report - No Jobs", msg)
        send_telegram_message(msg)
        print(msg)


if __name__ == "__main__":
    check_jobs()
