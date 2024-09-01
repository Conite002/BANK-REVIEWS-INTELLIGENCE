import requests
from bs4 import BeautifulSoup
import json
import os
from loguru import logger

# Set up loguru to log to a file and to the console
logger.add("data/utils/script.log", format="{time} {level} {message}", level="INFO", rotation="1 MB", compression="zip")

# Fetch the webpage content
url = "https://www.bceao.int/fr/content/paysage-bancaire"
logger.info(f"Fetching content from URL: {url}")
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# Locate the <ul> containing the country names
logger.info("Locating the <ul> containing country names.")
country_tabs = soup.find('ul', class_='nav nav-tabs')

# Dictionary to store country names and corresponding banks
country_banks = {}

# Extract country names and their corresponding tab content
logger.info("Extracting country names and corresponding bank information.")
for li in country_tabs.find_all('li'):
    # Extract country name
    country_name = li.find('a').text.strip()
    logger.info(f"Processing country: {country_name}")

    # Extract the ID of the corresponding content tab
    tab_id = li.find('a')['aria-controls']

    # Locate the tab content using the extracted ID
    tab_content = soup.find('div', id=tab_id)

    # Extract bank names listed under the country tab
    bank_names = []
    if tab_content:
        # Find all <li> elements inside <ul> within the tab content
        for bank in tab_content.find_all('li'):
            bank_name = bank.text.strip()
            bank_names.append(bank_name)
        logger.info(f"Found {len(bank_names)} banks for {country_name}.")
    else:
        logger.warning(f"No content found for tab ID: {tab_id}")

    country_banks[country_name] = bank_names

directory = '../data/utils'
os.makedirs(directory, exist_ok=True)  # Create the directory if it doesn't exist
file_path = os.path.join(directory, 'country_banks.json')

logger.info(f"Saving the data to {file_path}.")
with open(file_path, 'w', encoding='utf-8') as json_file:
    json.dump(country_banks, json_file, ensure_ascii=False, indent=4)

logger.info("Country and bank data successfully saved.")
