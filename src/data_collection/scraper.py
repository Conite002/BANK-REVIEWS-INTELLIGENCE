import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
import configparser

import time
from datetime import datetime
from selenium.webdriver.chrome.options import Options
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.actions.wheel_input import ScrollOrigin
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from tqdm import tqdm
import json, re
from json.decoder import JSONDecodeError
import stat
from loguru import logger
from src.data_collection.utils import is_website_url, is_phone_number,create_directory, load_from_config, save_to_config
from src.data_preprocessing.utils import parse_relative_date
import pandas as pd


# ----------------------------------------------------------

BASIC_PROD = '.'
CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
CITIES_PATH = os.path.join(BASIC_PROD, 'data', 'utils', 'countries_cities-full.json')
RAW_SAVE_PATH = os.path.join(BASIC_PROD, 'data', 'temp')
PARCKET_PATH = os.path.join(BASIC_PROD, 'data', 'parcket', CURRENT_DATE)
sys.path.append('/')

def save_data_to_parquet(country, city, data):
    output_dir = f"data/parquet/{time.strftime('%Y-%m-%d')}/{country}"
    os.makedirs(output_dir, exist_ok=True)
    
    df = pd.DataFrame(data)
    
    # Sauvegarder le DataFrame en fichier Parquet
    output_file = os.path.join(output_dir, f"{city}.parquet")
    df.to_parquet(output_file, index=False)
    print(f"Data saved to {output_file}")


# Function to perform primary search
def primary_search(browser):
    a = WebDriverWait(browser, 10).until(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'a.hfpxzc'))
    )
    action = webdriver.common.action_chains.ActionChains(browser)
    if not a:
        return a, action
    
    last_len = len(a)
    same_len_count = 0
    scroll_attempts = 0

    while True:
        try:
            if not a:
                break
            scroll_origin = ScrollOrigin.from_element(a[-1])
            action.scroll_from_origin(scroll_origin, 0, 1000).perform()
            time.sleep(2)
            a = browser.find_elements(By.CLASS_NAME, 'hfpxzc')
            if len(a) == last_len:
                same_len_count += 1
                if same_len_count > 5:
                    break
            else:
                last_len = len(a)
                same_len_count = 0
            scroll_attempts += 1
            if scroll_attempts > 50:  # Maximum scroll attempts to avoid infinite loop
                break
        except StaleElementReferenceException:
            logger.warning("Scroll down to the last element")
            logger.warning("StaleElementReferenceException occurred. Retrying...")
            time.sleep(2)
            continue
    return a, action


def extract_review(browser, action, verbose=False):
    try:
        tab_action = browser.find_elements(By.CLASS_NAME, 'hh2c6')
        if not tab_action or len(tab_action) < 2:
            return []
        advice_btn = tab_action[1]
        action.move_to_element(advice_btn).click().perform()
        time.sleep(2)
    except Exception as e:
        logger.error(f"An error occurred: {e}")

    reviews_blocs = browser.find_elements(By.CLASS_NAME, "jJc9Ad")
    last_reviews_count = len(reviews_blocs)
    if verbose:
        logger.info(f"Number of reviews found: {last_reviews_count}")
    _same = 0
    while True:
        scroll_origin = ScrollOrigin.from_element(reviews_blocs[-1])
        action.scroll_from_origin(scroll_origin, 0, 1000).perform()
        time.sleep(2)
        reviews_blocs = browser.find_elements(By.CLASS_NAME, "jJc9Ad")

        if len(reviews_blocs) == last_reviews_count:
            _same += 1
            if _same > 3:
                break
        else:
            last_reviews_count = len(reviews_blocs)
            _same = 0

    reviews = []
    
    state = load_from_config(name='state')
    if state == 'initial':
        reviews = initial_puller(reviews_blocs, reviews)
        # save_to_config(name='state', value='recurrente')
        # save_to_config(name='last_pull_date', value=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    elif state == 'recurrente':
        reviews = recurrente_puller(reviews_blocs=reviews_blocs, reviews=reviews)
        # save_to_config(name='last_pull_date', value=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    else:
        logger.error(f"Etat inconnu: {state}")
    return reviews


def initial_puller(reviews_blocs, reviews):
    for bloc in reviews_blocs:
        html_content = bloc.get_attribute('outerHTML')
        html_content = BeautifulSoup(html_content, 'html.parser')

        try:
            reviewer_name = html_content.find('div', {"class": "d4r55"}).text
            reviewer_star = len(html_content.findAll('span', {"class": "hCCjke google-symbols NhBTye elGi1d"}))
            reviewer_text = html_content.find('span', {"class": "wiI7pd"}).text if html_content.find('span', {"class": "wiI7pd"}) else "NAN"
            reviewer_publish_data = html_content.find('span', {"class": "rsqaWe"}).text
            reviewer_like_reaction = html_content.find('span', {"class": "pkWtMe"}).text if html_content.find('span', {"class": "pkWtMe"}) else 0
            reviewer_profil_link = html_content.find('button', {"class": "WEBjve"}).attrs.get('data-href')

            soup = html_content.findAll('div', {"class": "wiI7pd"})
            if soup:
                chat = [msg.text for msg in soup]
                reviewer_owner_reply = "**".join(chat)
            else:
                reviewer_owner_reply = "NAN"

            soup = html_content.find('span', {"class": "DZSIDd"})
            reviewer_owner_reply_date = soup.text if soup else "NAN"

            reviews.append((reviewer_name, reviewer_star, reviewer_text, reviewer_publish_data, reviewer_like_reaction, reviewer_profil_link, reviewer_owner_reply, reviewer_owner_reply_date))
        except Exception as e:
            logger.error(f"An error occurred in extract_review: {e}")
            continue
    return reviews


def recurrente_puller(reviews_blocs, reviews):
    LAST_PULL_DATE = load_from_config(name='last_pull_date')
    
    if isinstance(LAST_PULL_DATE, str):
        try:
            LAST_PULL_DATE = datetime.fromisoformat(LAST_PULL_DATE)
        except ValueError:
            logger.error("Invalid datetime string for last_pull_date")
            LAST_PULL_DATE = None
    for bloc in reviews_blocs:
        html_content = bloc.get_attribute('outerHTML')
        html_content = BeautifulSoup(html_content, 'html.parser')
        try:
            reviewer_publish_data = html_content.find('span', {"class": "rsqaWe"}).text
            print(f"reviewer_publish_data {reviewer_publish_data}")

            print(f"Raw reviewer_publish_data: {reviewer_publish_data}")
            publish_date = parse_relative_date(reviewer_publish_data)
            print(f"Parsed publish_date: {publish_date}")

            logger.debug(f"LAST_PULL_DATE: {LAST_PULL_DATE}, publish_date: {publish_date}")
            if publish_date is None:
                logger.warning(f"Could not parse publish date from '{reviewer_publish_data}'")
                continue

            if LAST_PULL_DATE and publish_date <= LAST_PULL_DATE:
                continue

            if LAST_PULL_DATE and publish_date <= LAST_PULL_DATE:
                continue

            reviewer_name = html_content.find('div', {"class": "d4r55"}).text
            reviewer_star = len(html_content.findAll('span', {"class": "hCCjke google-symbols NhBTye elGi1d"}))
            reviewer_text = html_content.find('span', {"class": "wiI7pd"}).text if html_content.find('span', {"class": "wiI7pd"}) else "NAN"
            reviewer_like_reaction = html_content.find('span', {"class": "pkWtMe"}).text if html_content.find('span', {"class": "pkWtMe"}) else 0
            reviewer_profil_link = html_content.find('button', {"class": "WEBjve"}).attrs.get('data-href')

            soup = html_content.findAll('div', {"class": "wiI7pd"})
            if soup:
                chat = [msg.text for msg in soup]
                reviewer_owner_reply = "**".join(chat)
            else:
                reviewer_owner_reply = "NAN"

            soup = html_content.find('span', {"class": "DZSIDd"})
            reviewer_owner_reply_date = soup.text if soup else "NAN"

            reviews.append((reviewer_name, reviewer_star, reviewer_text, reviewer_publish_data, reviewer_like_reaction, reviewer_profil_link, reviewer_owner_reply, reviewer_owner_reply_date))
        except Exception as e:
            logger.error(f"An error occurred in extract_review: {e}")
            continue
    return reviews



def extract(browser, sites, action, country, city, chrome_options, verbose=False):
    if not sites:
        logger.info(f'No sites found for {city} in {country}')
        return []

    logger.info(f"Numbers of banks founded {len(sites)}")
    columns = ['Country', 'Town', 'Bank_Name', 'Bank_Phone_number', 'Bank_Address', 'Bank_Website', 'Reviewer_Name', 'Reviewer_Star', 'Reviewer_Text', 'Reviewer_Publish_Date', 'Reviewer_Like_Reaction', 'Reviewer_Profile_Link', 'Reviewer_Owner_Reply', 'Reviewer_Owner_Reply_Date']
    df = pd.DataFrame(columns=columns)
    
    temp_csv_path = os.path.join(RAW_SAVE_PATH, f"pull-{city}-{country}-{CURRENT_DATE}.csv")

    try:
        create_directory(RAW_SAVE_PATH)
        if not os.path.exists(temp_csv_path):
            df.to_csv(temp_csv_path, index=False, encoding='utf-8')
            logger.info(f"File created successfully at {temp_csv_path}")
        else:
            logger.info(f"File already exists at {temp_csv_path}")
            return 
    except PermissionError as e:
        logger.error(f"PermissionError: {e}")
    except Exception as e:
        logger.error(f"An error occurred: {e}")


    total_reviews = 0
    for i in tqdm(range(len(sites))):
        retries = 3
        while retries > 0:
            try:
                if i >= len(sites):
                    logger.info(f"No more sites to process for {city} in {country}")
                    break
                browser.quit()
                browser = webdriver.Chrome(options=chrome_options)
                search_query = f"Banque {city}, {country}"
                browser.get(f"https://www.google.com/maps/search/{search_query}")
                time.sleep(10)

                sites, action = primary_search(browser)

                if sites[i] is not None:
                    wait = WebDriverWait(browser, 20)
                    wait.until(EC.element_to_be_clickable(sites[i]))
                    scroll_origin = ScrollOrigin.from_element(sites[i])
                    
                    action.scroll_from_origin(scroll_origin, 0, 1000).perform()
                    action.move_to_element(sites[i]).perform()
                    browser.execute_script("arguments[0].scrollIntoView(true);", sites[i])
                    time.sleep(2)
                    sites[i].click()
                time.sleep(5)
                break
            except StaleElementReferenceException:
                logger.warning(f"Stale element reference: {sites[i]} for {city} in {country}")
                retries -= 1
                if retries > 0:
                    logger.info(f"Retrying... {retries} left")
                    sites, action = primary_search(browser)
                    continue
                else:
                    logger.error("Max retries reached. Moving to the next site.")
                    break
            except Exception as e:
                logger.error(f"Error occurred while clicking on site {i}: {e}")
                break

        source = browser.page_source
        soup = BeautifulSoup(source, 'html.parser')
        try:
            Name_Html = soup.findAll('h1', {"class": "DUwDvf lfPIob"})
            name = Name_Html[0].text if Name_Html else "Not available"
            infos = soup.findAll('div', {'class':'Io6YTe'})

            phone = 'Not available'
            button_phone = soup.find('button', {'aria-label': lambda x: x and 'Numéro de téléphone' in x})
            if button_phone:
                phone = button_phone.get('aria-label').split(":")[-1].strip()
            else:
                div_phone = soup.find('div', {'data-tooltip': 'Copier le numéro de téléphone'})
                if div_phone:
                    phone = div_phone.text.strip()
                else:
                    infos = soup.findAll('div', {'class': 'Io6YTe'})
                    for info in infos:
                        if is_phone_number(info.text):
                            phone = info.text

            address = infos[0].text if infos else "Not available"

            website = 'Not available'
            link_website = soup.find('a', {'aria-label': lambda x: x and 'Site Web' in x})
            if link_website:
                website = link_website.get('href')
            else:
                button_website = soup.find('button', {'aria-label': 'Copier le site Web'})
                if button_website:
                    website = button_website.get('aria-label').split(":")[-1].strip()
                else:
                    for info in infos:
                        if is_website_url(info.text):
                            website = info.text

            if verbose:
                logger.info(f"Name: {name}\nPhone: {phone}\nAddress: {address}\nWebsite: {website}")

            bank_details = (country, city, name, phone, address, website)
            reviews = extract_review(browser, action) or []
            logger.info(f"Number of reviews found: {len(reviews)}")

            total_reviews += len(reviews)
            for review in reviews:
                full_review = [*bank_details, *review]
                df = pd.DataFrame([full_review], columns=columns)
                df['Reviewer_Like_Reaction'] = df['Reviewer_Like_Reaction'].astype(int)
                df.to_csv(temp_csv_path, mode='a', header=False, index=False, encoding='utf-8')


        except JSONDecodeError as json_err:
            logger.error(f"JSONDecodeError: {json_err} while parsing bank info")
        except ValueError as val_err:
            logger.error(f"ValueError: {val_err} while processing review data")
        except Exception as e:
            logger.error(f"Error occurred while extracting bank info: {e}")
            continue

        logger.info(f"Total number of reviews extracted: {total_reviews}")
    save_data_to_parquet(country, city, pd.read_csv(temp_csv_path))
    return reviews



