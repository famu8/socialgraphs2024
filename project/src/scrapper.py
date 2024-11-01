import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import os

# Set up WebDriver
driver = webdriver.Chrome()  # Ensure you have ChromeDriver set up in PATH
wait = WebDriverWait(driver, 10)

# Base URL
base_url = "https://www.eu-startups.com/directory/wpbdp_category/danish-startups/page/"
csv_filename = "DANISH_STARTUPS.csv"
results = []

# Create the CSV with headers if it doesn't already exist
if not os.path.isfile(csv_filename):
    pd.DataFrame(columns=[
        'Name', 'Category', 'Business Description', 'Based in', 'Tags', 
        'Total Funding', 'Founded', 'Website', 'Company Status'
    ]).to_csv(csv_filename, index=False)

# Loop through the pages
for page_num in range(1, 60):  # Adjust range as needed
    url = f"{base_url}{page_num}/"
    print(f"Scraping page {page_num}")

    driver.get(url)

    # Wait until the listings are loaded
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div.wpbdp-listing")))

    # Get the page source and parse it with BeautifulSoup
    soup = BeautifulSoup(driver.page_source, 'html.parser')

    # Find all listings on the current page
    listings = soup.select('div.wpbdp-listing')

    # Loop through each listing
    for listing in listings:
        try:
            # Find the link to the detailed page for each company
            company_link = listing.select_one("div.listing-title h3 a")
            company_name = company_link.text.strip()
            company_url = company_link['href']

            # Open the company's detailed page
            driver.get(company_url)
            time.sleep(1)  # Add a slight delay to allow page load

            # Parse the company's detailed page
            detailed_soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Extract fields from the detailed page
            category = detailed_soup.select_one("div.wpbdp-field-display span:contains('Category:') + div.value").text.strip() if detailed_soup.select_one("div.wpbdp-field-display span:contains('Category:') + div.value") else ''
            description = detailed_soup.select_one("div.wpbdp-field-display span:contains('Business Description:') + div.value").text.strip() if detailed_soup.select_one("div.wpbdp-field-display span:contains('Business Description:') + div.value") else ''
            based_in = detailed_soup.select_one("div.wpbdp-field-display span:contains('Based in:') + div.value").text.strip() if detailed_soup.select_one("div.wpbdp-field-display span:contains('Based in:') + div.value") else ''
            tags = detailed_soup.select_one("div.wpbdp-field-display span:contains('Tags:') + div.value").text.strip() if detailed_soup.select_one("div.wpbdp-field-display span:contains('Tags:') + div.value") else ''
            total_funding = detailed_soup.select_one("div.wpbdp-field-display span:contains('Total Funding:') + div.value").text.strip() if detailed_soup.select_one("div.wpbdp-field-display span:contains('Total Funding:') + div.value") else ''
            founded = detailed_soup.select_one("div.wpbdp-field-display span:contains('Founded:') + div.value").text.strip() if detailed_soup.select_one("div.wpbdp-field-display span:contains('Founded:') + div.value") else ''
            website = detailed_soup.select_one("div.wpbdp-field-display span:contains('Website:') + div.value").text.strip() if detailed_soup.select_one("div.wpbdp-field-display span:contains('Website:') + div.value") else ''
            company_status = detailed_soup.select_one("div.wpbdp-field-display span:contains('Company Status:') + div.value").text.strip() if detailed_soup.select_one("div.wpbdp-field-display span:contains('Company Status:') + div.value") else ''

            # Create a DataFrame for the single company
            company_data = pd.DataFrame([{
                'Name': company_name,
                'Category': category,
                'Business Description': description,
                'Based in': based_in,
                'Tags': tags,
                'Total Funding': total_funding,
                'Founded': founded,
                'Website': website,
                'Company Status': company_status
            }])

            # Append the data to CSV file immediately
            company_data.to_csv(csv_filename, mode="a", header=False, index=False)
            print(f"Saved {company_name} to CSV.")

            # Return to the listings page
            driver.back()
            time.sleep(1)  # Slight delay to allow page reload

        except Exception as e:
            print(f"Error processing listing: {e}")
            continue

    # Optional sleep between pages to avoid overwhelming the server
    time.sleep(0.5)

# Close the browser
driver.quit()

print("Scraping complete.")
