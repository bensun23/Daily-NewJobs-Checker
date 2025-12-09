import os
import smtplib
import feedparser
import requests
from email.message import EmailMessage
from bs4 import BeautifulSoup
from datetime import datetime

MY_NAME = "Bensun"

RSS_SOURCES = {
    "WeWorkRemotely": "https://weworkremotely.com/categories/remote-data-science-jobs.rss",
    "RemoteOK": "https://remoteok.com/remote-jobs.rss"
}

def clean_text(html, limit=250):
    soup = BeautifulSoup(html, "html.parser")
    text = " ".join(soup.get_text().split())
    return text[:limit] + ("..." if len(text) > limit else "")

def generate_outreach(title, company=""):
    company_line = f"Hi {company} hiring team," if company else "Hi there,"
    return f"""{company_line}

I'm {MY_NAME}. I found the role '{title}' and I'm really interested. 
I have beginner-level experience in Data Science + Machine Learning and would love to contribute.

Could we connect? Thank you!

Best,
{MY_NAME}
"""

def fetch_jobs():
    all_jobs = []
    for site, rss in RSS_SOURCES.items():
        feed = feedparser.parse(rss)
        for entry in feed.entries[:5]:
            all_jobs.append({
                "title": entry.title,
                "link": entry.link,
                "summary": clean_text(entry.get("summary", "")),
                "source": site
            })
    return all_jobs

def create_email(jobs):
    body = f"Daily Job Digest – {datetime.now().strftime('%Y-%m-%d')}\n\n"
    for i, job in enumerate(jobs, 1):
        body += f"{i}. {job['title']} ({job['source']})\n"
        body += f"Link: {job['link']}\n"
        body += f"Description: {job['summary']}\n\n"
        body += "LinkedIn Outreach Message:\n"
        outreach_msg = generate_outreach(job['title'])
        body += outreach_msg
        body += "\n" + ("-" * 50) + "\n\n"

        print(f"Job {i}: {job['title']}")
        print(f"LinkedIn Message:\n{outreach_msg}")
        print("-"*40)
    return body

def send_email(body):
    sender = os.getenv("GMAIL_EMAIL")
    password = os.getenv("GMAIL_PASSWORD")
    receiver = os.getenv("DESTINATION_EMAIL")

    print("Sender:", sender)
    print("Receiver:", receiver)
    print("Password length:", len(password) if password else 0)

    if not sender or not password or not receiver:
        with open("job_digest.txt", "w", encoding="utf-8") as f:
            f.write(body)
        print("Missing SMTP secrets — saved job_digest.txt in workspace.")
        return

    msg = EmailMessage()
    msg["Subject"] = "Daily DS & AIML Job Digest"
    msg["From"] = sender
    msg["To"] = receiver
    msg.set_content(body)

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(sender, password)
        server.send_message(msg)
    print("Email sent successfully!")

# -------------------------------------------
# 🚀 TELEGRAM FUNCTION (SAFE — does not affect email)
# -------------------------------------------

def send_telegram_message(message):
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")

    if not bot_token or not chat_id:
        print("Telegram secrets missing.")
        return

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message
    }

    resp = requests.post(url, data=payload)
    print("Telegram status:", resp.status_code)

# -------------------------------------------
# MAIN EXECUTION
# -------------------------------------------

if __name__ == "__main__":
    jobs = fetch_jobs()
    email_body = create_email(jobs)
    send_email(email_body)

    # Send Telegram notification (SAFE)
    send_telegram_message("Your Daily Job Digest is ready! Check your email 📩")
