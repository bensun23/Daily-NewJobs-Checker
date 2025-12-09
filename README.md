<!-- Fancy Banner -->
```
██████╗  █████╗ ██╗██╗  ██╗   ██╗         ██╗ ██████╗ ██████╗      ██████╗██╗  ██╗███████╗ ██████╗██╗  ██╗███████╗██████╗ 
██╔══██╗██╔══██╗██║██║  ╚██╗ ██╔╝         ██║██╔═══██╗██╔══██╗    ██╔════╝██║  ██║██╔════╝██╔════╝██║ ██╔╝██╔════╝██╔══██╗
██║  ██║███████║██║██║   ╚████╔╝          ██║██║   ██║██████╔╝    ██║     ███████║█████╗  ██║     █████╔╝ █████╗  ██████╔╝
██║  ██║██╔══██║██║██║    ╚██╔╝      ██   ██║██║   ██║██╔══██╗    ██║     ██╔══██║██╔══╝  ██║     ██╔═██╗ ██╔══╝  ██╔══██╗
██████╔╝██║  ██║██║███████╗██║       ╚█████╔╝╚██████╔╝██████╔╝    ╚██████╗██║  ██║███████╗╚██████╗██║  ██╗███████╗██║  ██║
╚═════╝ ╚═╝  ╚═╝╚═╝╚══════╝╚═╝        ╚════╝  ╚═════╝ ╚═════╝      ╚═════╝╚═╝  ╚═╝╚══════╝ ╚═════╝╚═╝  ╚═╝╚══════╝╚═╝  ╚═╝
                                                                                                                          
```

<p align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/c/c3/Python-logo-notext.svg" width="100"/>
</p>

<h1 align="center">Automated Job Checker with Email + Telegram Alerts</h1>

<p align="center">
  A fully automated GitHub Actions bot that checks job postings every 6 hours and sends alerts to your Email and Telegram.
</p>

---

## 🚀 **Badges**
<p align="center">

<img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white"/>
<img src="https://img.shields.io/badge/GitHub%20Actions-Automation-success?logo=githubactions&logoColor=white"/>
<img src="https://img.shields.io/badge/Telegram-Bot-2CA5E0?logo=telegram&logoColor=white"/>

</p>

---

# 📌 **About this Bot**
✔ Runs automatically every **6 pm everyday**  

✔ Scrapes job websites (customizable)  

✔ Sends **Email** alerts  

✔ Sends **Telegram** alerts  

✔ Works even when your PC is OFF  

✔ Fully serverless using GitHub Actions  

✔ Searches Naukri.com daily at 6:00 PM IST 

✔ Finds AIML Fresher, Data Science Fresher, Entry Level Tech jobs 

✔ Sends job results to your Email 

✔ Also sends notifications to Telegram 

✔ Uses BeautifulSoup, Requests, GitHub Actions, Gmail App Password 

✔ Fully automated — free — no server required 


---

# 🗂️ **Project Structure**

```
📦 Daily-NewJobs-Checker
 ┣ 📜 job_finder.py
 ┣ 📜 requirements.txt
 ┣ 📜 README.md
 ┗ 📂 .github/workflows/
      ┗ 📜 main.yml

```

---

# 🛠️ **Setup Instructions**

## **1️⃣ Create Telegram Bot**
1. Go to **@BotFather** on Telegram  
2. Run: `/newbot`  
3. Save your **BOT TOKEN**

---

## **2️⃣ Get Your Telegram Chat ID**
Send a message to your new bot, then open:

```
https://api.telegram.org/bot<YOUR_TOKEN>/getUpdates
```

Your chat ID appears like:

```
"id": 123456789
```

---

## **3️⃣ Add GitHub Secrets**
Go to:

**GitHub Repository → Settings → Secrets → Actions → New repository secret**

Add these:

| Secret Name | Description |
|------------|-------------|
| `EMAIL_USER` | Your Gmail/Outlook/Yahoo email |
| `EMAIL_PASS` | App password (not your login password) |
| `EMAIL_TO` | Where alerts should go |
| `TELEGRAM_BOT_TOKEN` | Bot token from BotFather |
| `TELEGRAM_CHAT_ID` | Your Telegram ID |

---

# 🧠 **How the Bot Works **

1. Every day at 6 PM IST, GitHub Actions triggers the workflow.

2. The script scrapes Naukri for fresh ML/Data Science fresher jobs.

3. If jobs exist →

            ✔ Email is sent

            ✔ Telegram message is sent

5. If no jobs → no notification

6. Full logs appear in GitHub Actions run. 

This works even if your laptop is off — GitHub servers run it.

---

# 🧪 **Full Python Code → `job_checker.py`**

```python
import os
import requests
from bs4 import BeautifulSoup
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ------- EMAIL FUNCTION -------
def send_email(subject, body):
    sender = os.getenv("SENDER_EMAIL")
    password = os.getenv("GMAIL_PASSWORD")
    receiver = os.getenv("DEST_EMAIL")

    msg = MIMEMultipart()
    msg["From"] = sender
    msg["To"] = receiver
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender, password)
        server.sendmail(sender, receiver, msg.as_string())
        server.quit()
        print("Email sent successfully!")
    except Exception as e:
        print("Email failed:", e)

# ------- TELEGRAM SEND -------
def send_telegram_message(text):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    url = f"https://api.telegram.org/bot{token}/sendMessage"

    try:
        requests.post(url, json={"chat_id": chat_id, "text": text})
        print("Telegram sent!")
    except Exception as e:
        print("Telegram failed:", e)

# ------- NAUKRI SCRAPER -------
def search_naukri_jobs():
    url = "https://www.naukri.com/machine-learning-fresher-jobs"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    jobs = []
    for job in soup.select(".jobTuple"):
        title = job.select_one(".title").get_text(strip=True)
        company = job.select_one(".subTitle").get_text(strip=True)
        link = job.select_one("a")["href"]

        jobs.append(f"📌 {title}\n🏢 {company}\n🔗 {link}")

    return jobs

# ------- MAIN -------
if __name__ == "__main__":
    jobs = search_naukri_jobs()

    if jobs:
        body = "🔥 Daily Naukri Job Report\n\n" + "\n\n".join(jobs)
        send_email("Daily Job Report", body)
        send_telegram_message(body)
        print("Notifications sent.")
    else:
        print("No new jobs found today.")
```

---

# ⚙️ **GitHub Actions File → `.github/workflows/job-checker.yml`**

```yaml
name: Daily Job Finder Bot

on:
  schedule:
    - cron: "30 12 * * *"    # 6:00 PM IST
  workflow_dispatch:

jobs:
  run-bot:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout repo
      uses: actions/checkout@v3

    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: "3.10"

    - name: Install Requirements
      run: pip install -r requirements.txt

    - name: Run Script
      env:
        SENDER_EMAIL: ${{ secrets.SENDER_EMAIL }}
        GMAIL_PASSWORD: ${{ secrets.GMAIL_PASSWORD }}
        DEST_EMAIL: ${{ secrets.DEST_EMAIL }}
        TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
        TELEGRAM_CHAT_ID: ${{ secrets.TELEGRAM_CHAT_ID }}
      run: python job_finder.py
```

---

# 🎉 Done!


MIT License

Copyright (c) 2025 Bensun Gundabathina

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.


