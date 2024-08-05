from datetime import datetime, timedelta
import re

# UTILS
# -------------------------------------------------------------------
def parse_relative_date(relative_date_str):
        match = re.search(r"il y a (\d+) (\w+)", relative_date_str)
        if not match:
            return None
        quantity = int(match.group(1))
        unit = match.group(2)
        if unit in ['ans', 'an']:
            return datetime.now() - timedelta(days=quantity * 365)
        elif unit == 'mois':
            return datetime.now() - timedelta(days=quantity * 30)
        elif unit in ['semaines', 'semaine']:
            return datetime.now() - timedelta(weeks=quantity)
        elif unit in ['jours', 'jour']:
            return datetime.now() - timedelta(days=quantity)
        elif unit in ['heures', 'heure']:
            return datetime.now() - timedelta(hours=quantity)
        elif unit in ['minutes', 'minute']:
            return datetime.now() - timedelta(minutes=quantity)
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


