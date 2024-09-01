import requests
from bs4 import BeautifulSoup
import json

# URL de la page contenant la liste des banques
url = "https://www.sgfg.ma/fr/garantie-des-depots/liste-des-banques-membres"

# Faire une requête GET pour obtenir le contenu de la page
response = requests.get(url)
response.raise_for_status()  # Assure que la requête a réussi

# Parse le contenu HTML de la page
soup = BeautifulSoup(response.content, 'html.parser')

# Trouver tous les éléments contenant les noms des banques
bank_cards = soup.find_all('div', class_='card')

# Liste pour stocker les noms des banques
banks = []

# Extraire les noms des banques
for card in bank_cards:
    h1_tag = card.find('h1')
    if h1_tag:
        bank_name = h1_tag.get_text(strip=True)
        banks.append(bank_name)

# Enregistrer les noms des banques dans un fichier JSON
with open('../data/utils/banks_maroc.json', 'w') as f:
    json.dump(banks, f, indent=4, ensure_ascii=False)

print("Les noms des banques ont été récupérés et enregistrés dans 'banks_maroc.json'.")
