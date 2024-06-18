from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time

##############
### CONFIG ###
SF_LEGISTAR_URL = "https://sfgov.legistar.com/Legislation.aspx"
type = "Ordinance"
year = 2023

#############
### SETUP ###
# Set up the Selenium WebDriver (assuming Chrome)
driver = webdriver.Chrome()

# Open the target webpage
driver.get(SF_LEGISTAR_URL)

# Wait for the dropdown menus to be available
wait = WebDriverWait(driver, 10)

###########################
### USE ADVANCED SEARCH ###
advanced_search_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//input[@value='Advanced search >>>']"))
)
advanced_search_button.click()
WebDriverWait(driver, 10).until(
    EC.presence_of_element_located((By.ID, "ctl00_ContentPlaceHolder1_lstMax_Arrow"))  # Adjust this selector
)

#############################
### SET ADV SEARCH PARAMS ###

### PARAM: Number of results ###
results_dropdown_arrow = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_lstMax_Arrow"))
)
results_dropdown_arrow.click()
all_option = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//li[text()='All']"))
)
all_option.click()

### PARAM: Date ###
# Wait for the "Date" dropdown to be clickable and click it
date_dropdown_arrow = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_lstYearsAdvanced_Arrow"))
)
date_dropdown_arrow.click()

# Wait for the dropdown options to be visible and select All Years
year_option = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//li[text()='All Years']"))
)
year_option.click()

#########################
### PARAM: Introduced ###
# Use XPath to select the "between" radio button in for date introduced
# Note: specify id because multiple "between" buttons on page
radio_button_first_set = driver.find_element(By.XPATH, "//span[@id='ctl00_ContentPlaceHolder1_radFileCreated']//input[@value='between']")
radio_button_first_set.click()

# start date for year
date_input = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_txtFileCreated1_dateInput")
# Clear the text box (optional)
date_input.clear()
# Enter the date in mm/dd/yyyy format
date_input.send_keys(f"01/01/{year}")

# end date for year
date_input = driver.find_element(By.ID, "ctl00_ContentPlaceHolder1_txtFileCreated2_dateInput")
# Clear the text box (optional)
date_input.clear()
# Enter the date in mm/dd/yyyy format
date_input.send_keys(f"12/31/{year}")

###################
### PARAM: Type ###
type_dropdown_arrow = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.ID, "ctl00_ContentPlaceHolder1_lstType_Input"))
)
type_dropdown_arrow.click()

# Wait for the dropdown options to be visible and select the type
type_option = WebDriverWait(driver, 10).until(
    #EC.element_to_be_clickable((By.XPATH, f"//li[text()='{type}']"))
    EC.visibility_of_element_located((By.XPATH, f"//li[text()='{type}']"))

)
type_option.click()

##############
### SEARCH ###
# Trigger the search (if there is a search button)
search_button = wait.until(EC.element_to_be_clickable((By.ID, "visibleSearchButton")))
search_button.click()

##################################
### EXTRACT URLS FOR ALL FILES ###
# Wait for the results to load (adjust the selector to the actual results container)
results = wait.until(EC.presence_of_all_elements_located((By.ID, "ctl00_ContentPlaceHolder1_menuMain")))

# Find all rows in the table
rows = driver.find_elements(By.XPATH, "//tr[@class='rgRow' or @class='rgAltRow']")

# Function to extract URLs from the current page
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
    pager_links = driver.find_elements(By.XPATH, "(//td[@class='rgPagerCell NumericPages'])[1]//a")  # Re-find pager links

print(f"Number of {type}s in {year}: {len(all_urls)}")

# save urls to file
url_filename = f"{year}_{type}_urls.txt"

# Open the file in write mode and write each URL on a new line
with open(url_filename, 'w') as file:
    for url in all_urls:
        file.write(url + '\n')

# Close the WebDriver
driver.quit()