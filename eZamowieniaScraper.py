from selenium import webdriver
from selenium.webdriver.common.by import By
from email.message import EmailMessage
from datetime import datetime
import smtplib
from dotenv import load_dotenv
import logging
import time
import json
import os

load_dotenv()

def email_send(mail_body, attach_filename):
    GMAIL_USER = os.getenv(GMAIL_USER)
    APP_PASSWORD = os.getenv(APP_PASSWORD)
    MAIL_TO = os.getenv(MAIL_TO)

    # Create the email
    msg = EmailMessage()
    msg['Subject'] = f"NEW eZamowienia Found - {datetime.now().strftime("%Y-%m-%d")}"
    msg['From'] = GMAIL_USER
    msg['To'] = MAIL_TO
    msg.set_content(mail_body)
    msg.add_attachment(attach_filename)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(GMAIL_USER, APP_PASSWORD)
        smtp.send_message(msg)

def load_existing_ids(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return set(file.read().splitlines())
    return set()

def save_new_ids(file_path, new_ids):
    with open(file_path, 'a', encoding='utf-8') as file:
        for new_id in new_ids:
            file.write(f"{new_id}\n")

def check_log_for_warnings_or_errors(log_file_path):
    warnings_or_errors_found = False
    today_date = datetime.now().strftime("%Y-%m-%d")

    with open(log_file_path, 'r') as file:
        for line in file:
            if line.startswith(today_date) and ('WARNING' in line or 'ERROR' in line):
                warnings_or_errors_found = True
                break

    if warnings_or_errors_found:
        return 0
    else:
        return 1

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    logFilePath = f"{script_dir}/eZamowieniaLog.log"
    search_phrases = ['Mikrotik', 'mtcna','mtcre','unifi','ubiquity','Linux','proxmox']
    url = "https://ezamowienia.gov.pl/mp-client/search/list"
    data = []
    result_filename = "results-e-zam.json"
    ids_filename = os.path.join(script_dir, "existing_ids.txt")
    status_filename = os.path.join(script_dir, "status_ezamowienia.json")
    current_timestamp = datetime.timestamp(datetime.now())

    logging.basicConfig(filename=logFilePath, level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    logging.info("---------------------------- Starting script ----------------------------")

    existing_ids = load_existing_ids(ids_filename)
    new_ids = set()

    try:
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-software-rasterizer')
        driver = webdriver.Chrome(options=options)
        driver.get(url)
        time.sleep(5)
        logging.info(f"Successfully loaded {url}")
    except Exception as e:
        logging.error(f"An error occured while trying to access {url}: {e}")
        return

    for phrase in search_phrases:
        phrase_data = {"phrase": phrase}
        results = []
        try:
            name_box = driver.find_element(by=By.ID, value='app-text-0') # search box
            submit_button = driver.find_element(by=By.XPATH, value="//button[@class='app-button btn btn-secondary btn-block']")

            name_box.clear() #making sure the box is empty
            name_box.send_keys(phrase)
            submit_button.click()
            time.sleep(5)

            tbody = driver.find_element(by=By.TAG_NAME, value='tbody')
            logging.info(f"Found {len(tbody.find_elements(by=By.TAG_NAME, value='tr'))} results for {phrase}")
        except Exception as e:
            logging.error(f"An error occured while trying to find elements: {e}")
            continue

        # Converting output to json format
        rows = tbody.find_elements(by=By.TAG_NAME, value='tr')

        for row in rows:
            try:
                cols = row.find_elements(by=By.TAG_NAME, value='td')[:3]
                cols = [ele.text.strip() for ele in cols]
                id_text = cols[1]  # Get the text of the second <td> for the ID
                if id_text in existing_ids:
                    logging.info(f"Skipping - {id_text} already exists in existing_ids.txt")
                if id_text not in existing_ids:
                    link = f"https://ezamowienia.gov.pl/mp-client/search/list/{id_text}"
                    logging.info(f"Creating link for ID: {id_text}")
                    results.append({
                        "Nazwa Zamówienia": cols[0],
                        "Identyfikator Postępowania": cols[1],
                        "Tryb Postępowania": cols[2],
                        "Link": link
                    })
                    new_ids.add(id_text)
            except Exception as e:
                logging.error(f"An error occurred while processing row data: {e}")
                continue

        if results:
            data.append(phrase_data)
            data.append({"results": results})
            logging.info(f"Added {len(results)} results for {phrase}")

    driver.quit()

    if not data:
        logging.info(f"No new entries for eZamowienia found.")

    if data:
        try:
            with open(result_filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logging.info(f"Data saved to {result_filename}")
        except Exception as e:
            logging.error(f"An error occurred while trying to save data to JSON: {e}")

        # Save new IDs to the text file
        save_new_ids(ids_filename, new_ids)

        # Send email
        try:
            mail_body = json.dumps(data, indent=4, ensure_ascii=False)
            attach_filename = result_filename
            email_send(mail_body, attach_filename)
            logging.info("Email sent successfully")
        except Exception as e:
            logging.error(f"An error occured while trying to send email: {e}")

    # Check if any errors occured
    if check_log_for_warnings_or_errors(logFilePath) == 0:
        logging.warning(f"An error/warning occured while trying to run the script!")
        status = 0
        last_run = int(current_timestamp)
        last_msg = "An error/warning occured while trying to run the script!"
    else:
        logging.info(f"No errors found while running the script.")
        status = 1
        last_run = int(current_timestamp)
        last_msg = "No errors found while running the script."

    #Create status file
    try:
        status_file = {
        'status': status,
        'last_run': last_run,
        'last_message': last_msg
        }
        with open(f'{status_filename}', 'w') as json_file:
            json.dump(status_file, json_file, indent=4)
        logging.info(f"Added status details to {status_filename}")
    except Exception as e:
        logging.error(f"An error occured while trying to save data to {status_filename}: {e}")


    logging.info("---------------------------- Script Finished ----------------------------")


if __name__ == '__main__':
    main()
