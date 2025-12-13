import smtplib
import requests
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from bs4 import BeautifulSoup
import openpyxl
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

SENT_JOBS_FILE = "sent_jobs.txt"

TARGET_COMPANIES = ["Google", "Amazon", "Zoho"]
STARTUP_KEYWORDS = ["startup", "early stage", "seed", "series"]

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


# --------------------------
# Telegram
# --------------------------
def send_telegram_message(message):
    url = f"https://api.telegram.org/bot{os.getenv('TELEGRAM_BOT_TOKEN')}/sendMessage"
    requests.post(url, data={"chat_id": os.getenv("TELEGRAM_CHAT_ID"), "text": message})


# --------------------------
# Sent Jobs Tracker
# --------------------------
def load_sent_jobs():
    if not os.path.exists(SENT_JOBS_FILE):
        return set()
    return set(open(SENT_JOBS_FILE).read().splitlines())


def save_sent_jobs(jobs):
    with open(SENT_JOBS_FILE, "a") as f:
        for j in jobs:
            f.write(j + "\n")


# --------------------------
# Job Sources (RSS)
# --------------------------
def fetch_jobs():
    sources = [
        ("Indeed", "https://in.indeed.com/rss?q=data+science+fresher"),
        ("Google Jobs", "https://www.google.com/search?q=AI+ML+fresher+jobs&output=rss"),
        ("Startup Jobs", "https://www.google.com/search?q=startup+AI+jobs+India&output=rss")
    ]

    jobs = []

    for source, url in sources:
        soup = BeautifulSoup(requests.get(url).text, "xml")
        for item in soup.find_all("item")[:10]:
            title = item.title.text
            link = item.link.text
            jobs.append(f"[{source}] {title} | {link}")

    return jobs


# --------------------------
# Filters
# --------------------------
def filter_jobs(jobs):
    filtered = []

    for job in jobs:
        if any(company.lower() in job.lower() for company in TARGET_COMPANIES):
            filtered.append("🏢 COMPANY JOB\n" + job)
        elif any(word in job.lower() for word in STARTUP_KEYWORDS):
            filtered.append("🚀 STARTUP JOB\n" + job)

    return filtered


# --------------------------
# AI-STYLE SUMMARY
# --------------------------
def ai_summary(job):
    return (
        "🔍 Role requires strong fundamentals in Python, ML basics, "
        "data handling, and problem-solving. Good fit for freshers."
    )


# --------------------------
# Excel Export
# --------------------------
def create_excel(jobs):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.append(["Job Info", "AI Summary"])

    for job in jobs:
        ws.append([job, ai_summary(job)])

    wb.save("jobs_today.xlsx")


# --------------------------
# PDF Export
# --------------------------
def create_pdf(jobs):
    pdf = canvas.Canvas("jobs_today.pdf", pagesize=A4)
    y = 800

    for job in jobs:
        pdf.drawString(40, y, job[:100])
        y -= 20
        pdf.drawString(40, y, ai_summary(job))
        y -= 40
        if y < 100:
            pdf.showPage()
            y = 800

    pdf.save()


# --------------------------
# MAIN
# --------------------------
def check_jobs():
    sent = load_sent_jobs()
    jobs = fetch_jobs()
    jobs = filter_jobs(jobs)

    new_jobs = [j for j in jobs if j not in sent]

    if new_jobs:
        create_excel(new_jobs)
        create_pdf(new_jobs)

        body = "🔥 NEW JOBS FOUND 🔥\n\n" + "\n\n".join(new_jobs)
        send_email("Daily Job Alerts 🚀", body)
        send_telegram_message(body)
        save_sent_jobs(new_jobs)
    else:
        msg = "ℹ️ No new jobs today (checked startups & top companies)"
        send_email("Job Alert – No New Jobs", msg)
        send_telegram_message(msg)


if __name__ == "__main__":
    check_jobs()
