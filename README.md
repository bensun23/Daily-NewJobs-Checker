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

# 📌 **Features**
✔ Runs automatically every **6 hours**  
✔ Scrapes job websites (customizable)  
✔ Sends **Email** alerts  
✔ Sends **Telegram** alerts  
✔ Works even when your PC is OFF  
✔ Fully serverless using GitHub Actions  

---

# 🗂️ **Project Structure**

```
job-checker/
│
├── job_checker.py
└── .github/
    └── workflows/
        └── job-checker.yml
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

# 🧠 **How It Works (Simple Explanation)**

1. GitHub Actions runs your script **every 6 hours**  
2. The script checks new job postings  
3. If new results are found →  
   - Sends **email**
   - Sends **telegram message**  
4. Results are logged in GitHub Actions  

This works even if your laptop is off — GitHub servers run it.

---

# 🧪 **Full Python Code → `job_checker.py`**

```python
import smtplib
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

# --------------------------
#  Email Notification
# --------------------------
def send_email(subject, body):
    email_user = os.getenv("EMAIL_USER")
    email_pass = os.getenv("EMAIL_PASS")
    email_to = os.getenv("EMAIL_TO")

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
#  Telegram Notification
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
# Simulated Job Check Function
# --------------------------
def check_jobs():
    # YOU CAN REPLACE THIS WITH REAL SCRAPING / API LOGIC
    new_jobs = [
        "🚀 Software Engineer - Google",
        "🧠 AI/ML Engineer - Meta",
        "🐍 Python Developer - Netflix"
    ]

    if new_jobs:
        body = "New Jobs Found:\n\n" + "\n".join(new_jobs)
        send_email("New Job Alerts", body)
        send_telegram_message(body)
    else:
        print("No new jobs today.")


if __name__ == "__main__":
    check_jobs()
```

---

# ⚙️ **GitHub Actions File → `.github/workflows/job-checker.yml`**

```yaml
name: Job Checker Bot

on:
  schedule:
    - cron: "0 */6 * * *"   # Every 6 hours
  workflow_dispatch:

jobs:
  run-job-checker:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repo
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.10"

      - name: Install dependencies
        run: pip install requests

      - name: Run job checker
        env:
          EMAIL_USER: ${{ secrets.EMAIL_USER }}
          EMAIL_PASS: ${{ secrets.EMAIL_PASS }}
          EMAIL_TO:   ${{ secrets.EMAIL_TO }}
          TELEGRAM_BOT_TOKEN: ${{ secrets.TELEGRAM_BOT_TOKEN }}
          TELEGRAM_CHAT_ID:   ${{ secrets.TELEGRAM_CHAT_ID }}
        run: python job_checker.py
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


