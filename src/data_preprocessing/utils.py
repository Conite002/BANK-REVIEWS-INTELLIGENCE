from datetime import datetime, timedelta
import re

# UTILS
# -------------------------------------------------------------------


def parse_relative_date(relative_date_str):
    relative_date_str = relative_date_str.replace('&nbsp;', ' ')
    
    # Remove extra words like "un" and handle possible variations
    relative_date_str = re.sub(r'\bun\b', '', relative_date_str).strip()
    
    # Regular expression to match the date format
    match = re.search(r"il y a (\d+)?\s*(\w+)", relative_date_str)
    
    if not match:
        return None

    quantity_str = match.group(1)
    unit = match.group(2)
    
    # Default quantity to 1 if not specified
    quantity = int(quantity_str) if quantity_str else 1
    
    unit_mapping = {
        'ans': 'years',
        'an': 'years',
        'mois': 'months',
        'semaines': 'weeks',
        'semaine': 'weeks',
        'jours': 'days',
        'jour': 'days',
        'heures': 'hours',
        'heure': 'hours',
        'minutes': 'minutes',
        'minute': 'minutes'
    }
    
    if unit not in unit_mapping:
        return None

    now = datetime.now()

    if unit_mapping[unit] == 'years':
        return now - timedelta(days=quantity * 365)
    elif unit_mapping[unit] == 'months':
        return now - timedelta(days=quantity * 30)  # Approximation: 30 days per month
    elif unit_mapping[unit] == 'weeks':
        return now - timedelta(weeks=quantity)
    elif unit_mapping[unit] == 'days':
        return now - timedelta(days=quantity)
    elif unit_mapping[unit] == 'hours':
        return now - timedelta(hours=quantity)
    elif unit_mapping[unit] == 'minutes':
        return now - timedelta(minutes=quantity)
    else:
        return None

def remove_some_cols(cols, df):
    return df.drop(columns=cols, axis=1)

def generate_static_topics_and_sentiments(stars):
    if stars == 1:
        return ('Expérience' ,"Très mauvaise", [])
    elif stars == 2:
        return ("Expérience", "Mauvaise", [])
    elif stars == 3:
        return ("Expérience", "Neutre", [])
    elif stars == 4:
        return ("Expérience", "Bonne", [])
    elif stars == 5:
        return ("Expérience", "Très bonne")
    else:
        return ("Expérience", "Neutre", [])


def generate_static_reviews_form_stars(stars):
    if stars == 1:
        return "Très mauvaise expérience"
    elif stars == 2:
        return "Mauvaise expérience",
    elif stars == 3:
        return "Expérience neutre"
    elif stars == 4:
        return "Bonne expérience"
    elif stars == 5:
        return "Très bonne expérience"
    else:
        return "Expérience neutre"


