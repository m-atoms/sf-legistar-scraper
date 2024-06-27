from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
import sqlite3

def extract_file_details(driver):
    details = {}
    
    # Extract legislation file details
    details['file_number'] = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_lblFile2").text
    print(f"scraping file: {details['file_number']}", end="")
    details['type'] = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_lblType2").text
    details['introduced'] = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_lblIntroduced2").text
    details['on_agenda'] = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_lblOnAgenda2").text
    details['enactment_date'] = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_lblEnactmentDate2").text
    details['name'] = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_lblName2").text
    details['status'] = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_lblStatus2").text
    details['in_control'] = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_hypInControlOf2").text
    details['final_action'] = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_lblPassed2").text
    details['enactment_number'] = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_lblEnactmentNumber2").text
    details['title'] = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_lblTitle2").text

    # Note: many legislation files do not have sponsors and most do not have related files
    #       set wait time to be shorter so scraping is more efficient

    # Extract sponsors
    driver.implicitly_wait(5)
    try:
        sponsors = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_lblSponsors2")
        sponsors_text = sponsors.text
        sponsors = [sponsor.strip() for sponsor in sponsors_text.split(',')]
        details['sponsors'] = ', '.join(sponsors)
    except NoSuchElementException:
        details['sponsors'] = ''
    finally:
        driver.implicitly_wait(10)

    # Extract related_files - this works but waits for a 10 second time out on files without related files section
    #related_files = driver.find_elements(By.CSS_SELECTOR, "#ctl00_ContentPlaceHolder1_lblRelatedFiles2 a")
    #details['related_files'] = ', '.join([related_file.text for related_file in related_files])
    try:
        driver.implicitly_wait(5)
        related_files = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_lblRelatedFiles2")
        related_files_text = related_files.text
        related_files = [related_file.strip() for related_file in related_files_text.split(',')]
        details['related_files'] = ', '.join(related_files)
    except NoSuchElementException:
        details['related_files'] = ''
    finally:
        driver.implicitly_wait(10)
    
    # Extract history details
    details['history'] = extract_file_history(driver)
    
    return details

def extract_file_history(driver):
    history = []
    rows = driver.find_elements(By.XPATH, "//table[@class='rgMasterTable']//tbody//tr")

    for row in rows:
        history_record = {}
        history_record['date'] = row.find_element(By.XPATH, "./td[1]").text
        history_record['ver'] = row.find_element(By.XPATH, "./td[2]").text
        history_record['action_by'] = row.find_element(By.XPATH, "./td[3]").text
        history_record['action'] = row.find_element(By.XPATH, "./td[4]").text
        history_record['result'] = row.find_element(By.XPATH, "./td[5]").text
        history.append(history_record)

    return history

def print_legislation_details(file_number, db_name='data/legislation.db'):
    conn = sqlite3.connect(db_name)
    c = conn.cursor()

    # Query the legislation details
    c.execute('''SELECT * FROM legislation WHERE file_number = ?''', (file_number,))
    legislation = c.fetchone()

    if legislation is None:
        print(f"No legislation found with file number {file_number}")
        conn.close()
        return

    # Query the legislation history
    legislation_id = legislation[0]
    c.execute('''SELECT date, ver, action_by, action, result FROM history WHERE legislation_id = ?''', (legislation_id,))
    history = c.fetchall()

    conn.close()

    # Print legislation details
    print("\nLegislation Details:")
    print(f"ID: {legislation[0]}")
    print(f"File Number: {legislation[1]}")
    print(f"Type: {legislation[2]}")
    print(f"Introduced: {legislation[3]}")
    print(f"On Agenda: {legislation[4]}")
    print(f"Enactment Date: {legislation[5]}")
    print(f"Name: {legislation[6]}")
    print(f"Status: {legislation[7]}")
    print(f"In Control: {legislation[8]}")
    print(f"Final Action: {legislation[9]}")
    print(f"Enactment Number: {legislation[10]}")
    print(f"Title: {legislation[11]}")
    print(f"Sponsors: {legislation[12]}")
    print(f"Related Files: {legislation[13]}")
    print(f"URL: {legislation[14]}")

    # Print legislation history
    print("\nLegislation History:")
    for record in history:
        print(f"Date: {record[0]}, Version: {record[1]}, Action By: {record[2]}, Action: {record[3]}, Result: {record[4]}")