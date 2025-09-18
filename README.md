# eZamowienia Scraper & Notifier

## Project Context
This script was developed while I was working at **ORBITECH** to automate the monitoring of IT-related public tenders.  

## Photos
<img width="1524" height="829" alt="image" src="https://github.com/user-attachments/assets/db18bd88-3789-4e4f-98a9-3108d16a1bd7" />
<img width="993" height="430" alt="image" src="https://github.com/user-attachments/assets/659c85e6-be3b-45c1-90fa-45d967bc79ca" />

## **Overview**

The **eZamowienia Scraper & Notifier** is an automated Python script designed to:

1. **Scrape new tenders** from [eZamowienia.gov.pl](https://ezamowienia.gov.pl/mp-client/search/list) based on specific keywords related to IT and networking (search_phrases = ['Mikrotik', 'mtcna','mtcre','unifi','ubiquity','Linux','proxmox']).
2. **Track and store unique tender IDs** to avoid duplicates in future runs.
3. **Convert results into structured JSON data**, including links for easy access.
4. **Send automated email notifications** with the new tender data attached.
5. **Maintain a detailed log** of the script’s activity, errors, and warnings.
6. **Keep a status record** of the last successful run and encountered issues.

---

## **Key Features**

* **Automated Web Scraping:**
  Uses `Selenium` to search for predefined phrases (`Mikrotik`, `mtcna`, `unifi`, etc.) on the eZamowienia portal and collect tender data dynamically.

* **Duplicate Detection:**
  Maintains a text file (`existing_ids.txt`) of previously collected tender IDs to ensure no duplicate notifications.

* **Structured JSON Output:**
  Results are stored in a JSON file (`results-e-zam.json`) with clear fields:

  * `Nazwa Zamówienia` (Tender Name)
  * `Identyfikator Postępowania` (Tender ID)
  * `Tryb Postępowania` (Procedure Type)
  * `Link` (Direct URL to the tender)

* **Automated Email Notifications:**
  Sends emails through **Gmail SMTP** using secure environment variables. Includes the JSON data as both the email body and attachment.

* **Robust Logging:**
  Logs all activity, including:

  * Script start/end timestamps
  * Number of results found
  * Errors and warnings
  * Skipped duplicates
    Log file: `eZamowieniaLog.log`

* **Status Tracking:**
  Maintains a status file (`status_ezamowienia.json`) to track:

  * Success or failure
  * Last run timestamp
  * Last message summary

* **Error Handling & Retry Safety:**
  Gracefully handles:

  * Missing elements or website issues
  * Selenium failures
  * Email sending errors
  * JSON file writing errors

* **Headless Browser Operation:**
  Uses Selenium Chrome in headless mode for **fast, invisible automation**, suitable for scheduled tasks (cron jobs or Windows Task Scheduler).

---

## **Getting Started**

### **1. Prerequisites**

* Python 3.10+ installed
* Google Chrome installed
* Chromedriver compatible with your Chrome version
* Gmail account with **2FA enabled** and an **App Password** for SMTP

---

### **2. Install Required Python Packages**

```bash
pip install selenium python-dotenv
```

Optional: for better logging and debugging:

```bash
pip install rich
```

---

### **3. Setup Environment Variables**

Create a `.env` file in the project root:

```env
GMAIL_USER=your_email@gmail.com
APP_PASSWORD=your_gmail_app_password
MAIL_TO=recipient_email@example.com
```

---

### **4. Configuration**

* `search_phrases`: Modify the list in the script to scrape tenders of interest.
* `existing_ids.txt`: Keeps track of already scraped tender IDs.
* `results-e-zam.json`: Output JSON file with newly scraped tenders.
* `status_ezamowienia.json`: Contains last run info and error status.

---

### **5. Run the Script**

```bash
python eZamowieniaScraper.py
```

* The script will:

  1. Open the eZamowienia portal in headless Chrome
  2. Search for each phrase
  3. Collect results, skipping duplicates
  4. Save results to JSON
  5. Send email with results attached
  6. Log all activity
  7. Update status JSON

---

## **Project Structure**

```
eZamowieniaScraper/
│
├── eZamowieniaScraper.py      # Main Python script
├── existing_ids.txt           # Stores previously collected tender IDs
├── results-e-zam.json         # Output JSON file with new tenders
├── status_ezamowienia.json    # Last run status and summary
├── eZamowieniaLog.log         # Detailed logging of the script's activity
└── .env                       # Environment variables for Gmail credentials
```

---

## **Logging & Error Handling**

* All events are logged in `eZamowieniaLog.log`.
* If errors or warnings occur, the script:

  * Does not overwrite existing data
  * Logs the issue with timestamp
  * Updates `status_ezamowienia.json` with `status: 0` and a descriptive message
* Successful runs have `status: 1`.

---

## **Email Notifications**

* Emails are sent automatically through Gmail SMTP.
* Features:

  * Subject includes current date: `"NEW eZamowienia Found - YYYY-MM-DD"`
  * JSON file is attached
  * JSON content is also included in the email body
* Uses **secure App Passwords** instead of raw Gmail passwords.

---

## **License**

This project is licensed under the **MIT License** – see `LICENSE` for details.
