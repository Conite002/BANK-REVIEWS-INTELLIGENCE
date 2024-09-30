import requests
from bs4 import BeautifulSoup
import json

url = "https://www.sgfg.ma/fr/garantie-des-depots/liste-des-banques-membres"

response = requests.get(url)
response.raise_for_status() 
soup = BeautifulSoup(response.content, 'html.parser')
bank_cards = soup.find_all('div', class_='card')
banks = []

for card in bank_cards:
    h1_tag = card.find('h1')
    if h1_tag:
        bank_name = h1_tag.get_text(strip=True)
        banks.append(bank_name)

with open('../data/utils/banks_maroc.json', 'w') as f:
    json.dump(banks, f, indent=4, ensure_ascii=False)

print("Les noms des banques ont été récupérés et enregistrés dans 'banks_maroc.json'.")
