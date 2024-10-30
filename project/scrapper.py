import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

# Set up WebDriver
driver = webdriver.Chrome()  # Ensure you have ChromeDriver set up in PATH
wait = WebDriverWait(driver, 10)

# Base URL for the first page
base_url = "https://www.eu-startups.com/directory/wpbdp_category/danish-startups/page/"
results = []

# Loop through the pages (1 to 5 as an example)
for page_num in range(1, 62):  # Change 6 to however many pages you want to scrape
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
            # Extract fields from each listing
            name = listing.select_one("div.listing-title h3 a").text.strip()
            category = listing.select_one("div.wpbdp-field-display span:contains('Category:') + div.value").text.strip()
            based_in = listing.select_one("div.wpbdp-field-display span:contains('Based in:') + div.value").text.strip()
            tags = listing.select_one("div.wpbdp-field-display span:contains('Tags:') + div.value").text.strip()
            founded = listing.select_one("div.wpbdp-field-display span:contains('Founded:') + div.value").text.strip()
            
            # Extract image URL
            image_url = listing.select_one("div.listing-thumbnail img")["src"]
            
            # Append data to results
            results.append({
                'Name': name,
                'Category': category,
                'Based in': based_in,
                'Tags': tags,
                'Founded': founded,
                'Image URL': image_url
            })
        except Exception as e:
            print(f"Error processing listing: {e}")
            continue

    # Optional sleep between pages to avoid overwhelming the server
    time.sleep(0.5)

# Close the browser
driver.quit()

# Save data to a DataFrame and CSV
df = pd.DataFrame(results)
df.to_csv("danish_startups.csv", index=False)
print(df.to_string(index=False))
