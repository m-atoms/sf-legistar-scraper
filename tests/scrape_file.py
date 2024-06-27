import sys
from selenium import webdriver
from selenium.webdriver.common.by import By
from src.scraper.utils import extract_file_details

def scrape_file(file_url):
    # setup scraper
    driver = webdriver.Chrome()
    driver.get(file_url)
    driver.implicitly_wait(10)
    
    # scrape file
    details = extract_file_details(driver)

    return details

def print_file_details(details):
    # print results
    print("\nLegislation Details:")
    print("-" * 20)
    print(f"File Number:      {details['file_number']}")
    print(f"Type:             {details['type']}")
    print(f"Introduced:       {details['introduced']}")
    print(f"On Agenda:        {details['on_agenda']}")
    print(f"Enactment Date:   {details['enactment_date']}")
    print(f"Name:             {details['name']}")
    print(f"Status:           {details['status']}")
    print(f"In Control:       {details['in_control']}")
    print(f"Final Action:     {details['final_action']}")
    print(f"Enactment Number: {details['enactment_number']}")
    print(f"Title:            {details['title']}")
    print(f"Sponsors:         {details['sponsors']}")
    print(f"Related Files:    {details['related_files']}")
    print(f"URL:              {file_url}")

    # Print legislation history
    print("\nLegislation History:")
    print("-" * 20)
    for record in details['history']:
        print(f"Date: {record['date']}, Version: {record['ver']}, Action By: {record['action_by']}, Action: {record['action']}, Result: {record['result']}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <file_url>")
        sys.exit(1)

    file_url = sys.argv[1]

    # scrape file using URL
    details = {}
    details = scrape_file(file_url)

    # print file details
    print_file_details(details)