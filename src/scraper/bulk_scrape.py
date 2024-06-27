from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import yaml
from src.database.db_operations import create_tables, store_in_database
from src.scraper.utils import extract_file_details, print_legislation_details

# configure webscraping driver to run headless
def create_driver():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=options)
    return driver

# scrape URLs for all legislation of {type} introduced during {year}
def scrape_legislation_urls(start_year, end_year, legislation_type):
    # Set up the Selenium WebDriver
    driver = create_driver()

    try:
        # Open the target webpage
        driver.get('https://sfgov.legistar.com/Legislation.aspx')

        # Wait for the dropdown menus to be available
        wait = WebDriverWait(driver, 10)

        # Navigate to Advanced search
        advanced_search_button = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//input[@value='Advanced search >>>']"))
        )
        advanced_search_button.click()
        wait.until(EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_lstMax_Arrow")))

        ############################
        ### CONFIG SEARCH PARAMS ###
        ############################

        ### PARAM: Number of results = All ###
        results_dropdown_arrow = wait.until(
            EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_lstMax_Arrow"))
        )
        results_dropdown_arrow.click()
        all_option = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//li[text()='All']"))
        )
        all_option.click()

        ### PARAM: Date = All Years ###
        date_dropdown_arrow = wait.until(
            EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_lstYearsAdvanced_Arrow"))
        )
        date_dropdown_arrow.click()
        year_option = wait.until(
            EC.element_to_be_clickable((By.XPATH, "//li[text()='All Years']"))
        )
        year_option.click()

        ### PARAM: Introduced = between 01/01/{year} and 12/31/{year} ###
        # Note: specify id because multiple "between" buttons on page
        radio_button_first_set = driver.find_element(By.XPATH, '//span[@id="ctl00_ContentPlaceHolder1_radFileCreated"]//input[@value="between"]')
        radio_button_first_set.click()

        # start date for {year}
        date_input = driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_txtFileCreated1_dateInput')
        date_input.clear()
        date_input.send_keys(f'01/01/{start_year}')

        # end date for {year}
        date_input = driver.find_element(By.ID, 'ctl00_ContentPlaceHolder1_txtFileCreated2_dateInput')
        date_input.clear()
        date_input.send_keys(f'12/31/{end_year}')

        ### PARAM: Type = {type} ###
        type_dropdown_arrow = wait.until(
            EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_lstType_Input"))
        )
        type_dropdown_arrow.click()
        type_option = wait.until(
            EC.visibility_of_element_located((By.XPATH, f"//li[text()='{legislation_type}']"))
        )
        type_option.click()

        # Search
        search_button = wait.until(EC.element_to_be_clickable((By.ID, "visibleSearchButton")))
        search_button.click()

        ################################
        ### EXTRACT LEGISLATION URLS ###
        ################################
        wait.until(EC.presence_of_all_elements_located((By.ID, 'ctl00_ContentPlaceHolder1_menuMain')))

        # Helper function to extract URLs from the current page
        def extract_urls():
            rows = driver.find_elements(By.XPATH, "//tr[@class='rgRow' or @class='rgAltRow']")
            urls = []
            for row in rows:
                link = row.find_element(By.TAG_NAME, "a")
                if link:
                    urls.append(link.get_attribute("href"))
            return urls

        # Initialize list to hold all URLs
        all_urls = []

        # Extract URLs from the first page
        all_urls.extend(extract_urls())

        # Find the pager links
        # same thing is on bottom of page so only find first instance of these classes
        pager_links = driver.find_elements(By.XPATH, "(//td[@class='rgPagerCell NumericPages'])[1]//a")

        # Loop through each page link and extract URLs
        for i in range(1, len(pager_links)):
            pager_links[i].click()
            time.sleep(2)  # Wait for the page to load
            all_urls.extend(extract_urls())
            pager_links = driver.find_elements(By.XPATH, "(//td[@class='rgPagerCell NumericPages'])[1]//a") # Re-find pager links

        print(f"Number of {legislation_type}s introduced from 01/01/{start_year} to 12/31/{end_year}: {len(all_urls)}")

        return all_urls

    finally:
        driver.quit()

def bulk_scrape(start_year, end_year, legislation_type):
    # STEP 0: Create db tables
    create_tables()

    # STEP 1: Scrape all legislation file URLs in date range
    legislation_urls = scrape_legislation_urls(start_year, end_year, legislation_type)

    # init scrape counter and timers
    scraped = 0
    start_time = time.time()
    scrape_times = []

    # STEP 2: process URLS and extract info from each file
    driver = create_driver()

    try:
        for url in legislation_urls:
            # init file scrape timer
            file_start_time = time.time()
            
            # scrape file and store in db
            driver.get(url)
            driver.implicitly_wait(10)
            details = extract_file_details(driver)
            details['url'] = url
            store_in_database(details)

            # capture script telemetry
            scraped += 1
            file_end_time = time.time()
            scrape_times.append(file_end_time - file_start_time)
            print(f" | file srape time: {(file_end_time - file_start_time):.2f} | files scraped: {scraped}", end="\r")

            time.sleep(2)

            # print one file to test
            #print_legislation_details(details['file_number'])
            #break
    finally:
        driver.quit()

    # STEP 3: Print script telemetry and summary
    end_time = time.time()
    total_time = end_time - start_time
    min_time = min(scrape_times) if scrape_times else 0
    max_time = max(scrape_times) if scrape_times else 0
    avg_time = sum(scrape_times) / len(scrape_times) if scrape_times else 0

    print(f'Scraped {scraped} {legislation_type}s introduced between 01/01/{start_year} and 12/31/{end_year}')
    print(f'Total time taken: {total_time:.2f} seconds')
    print(f'Min time per scrape: {min_time:.2f} seconds')
    print(f'Max time per scrape: {max_time:.2f} seconds')
    print(f'Average time per scrape: {avg_time:.2f} seconds')

if __name__ == "__main__":
    with open('config/config.yaml', 'r') as f:
        config = yaml.safe_load(f)
    
    scrape_config = config['bulk_scrape']
    bulk_scrape(scrape_config['start_year'], scrape_config['end_year'], scrape_config['legislation_type'])