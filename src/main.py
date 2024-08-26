import os, sys
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, '..'))
sys.path.append(project_root)
import psycopg2
import subprocess
from sqlalchemy.exc import IntegrityError
from src.data_collection.utils import is_website_url, is_phone_number,create_directory, load_from_config, save_to_config


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
from tqdm import tqdm
from loguru import logger
from src.data_collection.utils import load_cities, throw_error
from src.data_collection.scraper import primary_search, extract
from src.data_concatenation.concatenate import build_macro_table
from src.data_preprocessing.preprocessing import preprocess_dataframe
import pandas as pd
import sys
from src.database_management.database_initializer import DatabaseInitializer, wait_for_postgresql
from src.database_management.dataframe_to_transactionalDB import insert_data_from_dataframe
from src.database_management.db_models import Base
from src.database_management.migrate_to_decisionalDB import migration_to_decisionalDB
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, Column, Integer, String, Text, Date, ForeignKey, insert
import os
# from dotenv import load_dotenv


# Charger les variables d'environnement à partir du fichier .env
# load_dotenv()



    # ADMIN_USER = 'postgres'
    # ADMIN_PASSWORD = 'postgres'
    # HOST = 'postgres_db'
    # PORT = '5432'
    # DB_USER = 'conite'
    # DB_PASSWORD = 'conite_password'
    # DB_NAME = 'bank_reviews'
    # DECISIONALDB = 'decisional_db'

# ----------------------------------------------------------

# CURRENT_DATE = datetime.now().strftime("%Y-%m-%d")
CURRENT_DATE = '2024-08-11'
DATA_PATH = os.path.join(project_root, 'data')
CITIES_PATH = os.path.join(project_root, 'data', 'utils', 'countries_cities-full.json')
RAW_SAVE_PATH = os.path.join(project_root, 'data', 'temp')
PARCKET_PATH = os.path.join(project_root, 'data', 'parquet', CURRENT_DATE)
PROCESSED_DATA_PATH = os.path.join(project_root, 'data', 'processed', CURRENT_DATE)
# sys.path.append('/')



def main():
    chrome_options = Options()
    chrome_options.add_argument("--lang=fr")
    # chrome_options.add_argument("--headless")
    countries_cities = load_cities(CITIES_PATH)
    # temp_csv_path = os.path.join(RAW_SAVE_PATH, f"pull-{city}-{country}-{CURRENT_DATE}.csv")

    # for country, cities in countries_cities.items():
    #     print("PULLING: ", country)
    #     for city in tqdm(cities):
    #         browser = webdriver.Chrome(options=chrome_options)
    #         search_query = f"Banque {city}, {country}"
    #         browser.get(f"https://www.google.com/maps/search/{search_query}")
    #         time.sleep(20)

    #         retry_attempts = 3
    #         while retry_attempts > 0:
    #             try:
    #                 sites, action = primary_search(browser)
    #                 extract(browser, sites, action, country, city, chrome_options, verbose=True)
    #                 break  # Break if no exception
    #             except StaleElementReferenceException:
    #                 retry_attempts -= 1
    #                 print(f"Retrying... ({3 - retry_attempts}/3)")
    #                 time.sleep(2)  # Brief wait before retrying
    #             except Exception as e:
    #                 throw_error(e, location='main loop')
    #                 break  # Break on other exceptions

    #         browser.quit()
    # save_to_config(name='state', value='recurrente')
    # save_to_config(name='last_pull_date', value=datetime.now().strftime('%Y-%m-%d %H:%M:%S'))
    # --------------------------------------------------------
    # 0.1 Build macro table
    # --------------------------------------------------------
    
    #concatenate_parquets = build_macro_table(DATA_PATH)

    # --------------------------------------------------------
    # 0.3 Preprocessing of concatenate parquets
    # --------------------------------------------------------
    #bank_reviews = preprocess_dataframe(concatenate_parquets)

    output_file = os.path.join(PROCESSED_DATA_PATH, 'macro_llamma.csv')

    # Vérifier si le fichier existe et le lire, sinon créer un DataFrame vide
    if os.path.exists(output_file):
        bank_reviews = pd.read_csv(output_file)
    else:
        print(f"File doesn't existe")
    
    # --------------------------------------------------------
    # 0.4 Remove some columns
    # --------------------------------------------------------
    # bank_reviews = bank_reviews.fillna({
    #     'Country': 'Unknown',
    #     'Town': 'Unknown',
    #     'Bank_Name': 'Unknown',
    #     'Bank_Phone_number': '',
    #     'Bank_Address': '',
    #     'Bank_Website': '',
    #     'Reviewer_Name': 'Anonymous',
    #     'Reviewer_Star': 0,
    #     'Reviewer_Text': '',
    #     'Reviewer_Publish_Date': pd.Timestamp('1970-01-01'),
    #     'Reviewer_Like_Reaction': 0,
    #     'Reviewer_Profile_Link': '',
    #     'Reviewer_Owner_Reply': '',
    #     'Reviewer_Owner_Reply_Date': pd.Timestamp('1970-01-01'),
    #     'Topics': 'General',
    #     'Sentiments': 'Neutral',
    #     'Sub_Topics': 'Miscellaneous'
    # })
    

    # --------------------------------------------------------
    # 0.4 Remove some columns
    # --------------------------------------------------------
    # bank_reviews = remove_some_cols(['date','country','city'], bank_reviews)
    # Remplace les valeurs NaN par None
    # bank_reviews = bank_reviews.applymap(lambda x: None if pd.isna(x) else x)


    # # Replace NaT values with a default date
    # default_date = pd.Timestamp('1970-01-01')
    # bank_reviews['Reviewer_Publish_Date'] = bank_reviews['Reviewer_Publish_Date'].fillna(default_date)
    # bank_reviews['Reviewer_Owner_Reply_Date'] = bank_reviews['Reviewer_Owner_Reply_Date'].fillna(default_date)

    # # Ensure conversion to datetime
    # bank_reviews['Reviewer_Publish_Date'] = pd.to_datetime(bank_reviews['Reviewer_Publish_Date'], errors='coerce').fillna(default_date)
    # bank_reviews['Reviewer_Owner_Reply_Date'] = pd.to_datetime(bank_reviews['Reviewer_Owner_Reply_Date'], errors='coerce').fillna(default_date)

    # print(bank_reviews.head())
    # print(f"Invalid publish dates: {bank_reviews['Reviewer_Publish_Date'].isna().sum()}")
    # print(f"Invalid owner reply dates: {bank_reviews['Reviewer_Owner_Reply_Date'].isna().sum()}")

    
    # # Replace NaN values with appropriate defaults
    # bank_reviews['Reviewer_Star'] = bank_reviews['Reviewer_Star'].fillna(0)
    # bank_reviews['Reviewer_Like_Reaction'] = bank_reviews['Reviewer_Like_Reaction'].fillna(0)
    # bank_reviews['Reviewer_Name'] = bank_reviews['Reviewer_Name'].fillna('Anonymous')
    # bank_reviews['Reviewer_Text'] = bank_reviews['Reviewer_Text'].fillna('')
    # bank_reviews['Reviewer_Profile_Link'] = bank_reviews['Reviewer_Profile_Link'].fillna('')
    # bank_reviews['Reviewer_Owner_Reply'] = bank_reviews['Reviewer_Owner_Reply'].fillna('')




    # --------------------------------------------------------
    # 0.4 Topification
    # --------------------------------------------------------
    # TEMP_REVIEWS_PATH = os.path.join(project_root, 'data', 'processed', 'topics', 'bank_reviews.csv')
    # bank_reviews_topics = pd.read_csv(TEMP_REVIEWS_PATH)
    # # completer le dataframe bank_reviews existant  avec les autres colonnes du bank_reviews_topics tout en comparant la colonne Reviewer_Text 
    # if 'Reviewer_Text' in bank_reviews.columns and 'Reviewer_Text' in bank_reviews_topics:
    #     bank_reviews = bank_reviews.merge(bank_reviews_topics, on='Reviewer_Text', how='right')
    # else:
    #     print("Reviewer_Text not found in the dataframes")


    # --------------------------------------------------------
    # 0.5 Initialization of database
    # --------------------------------------------------------
    # Utilisation de la DatabaseInitializer
    ADMIN_USER = 'postgres'
    ADMIN_PASSWORD = 'postgres'
    HOST = 'postgres_db'
    PORT = '5432'
    DB_USER = 'conite'
    DB_PASSWORD = 'conite_password'
    DB_NAME = 'bank_reviews'
    DECISIONALDB = 'decisional_db'

    # --------------------------------------------------------------------------
    # Database Initialization
    # --------------------------------------------------------------------------
    db_initializer = DatabaseInitializer(ADMIN_USER, ADMIN_PASSWORD, HOST, PORT)

    db_initializer.create_database_and_user(DB_USER, DB_PASSWORD, DB_NAME)
    db_initializer.create_database_and_user(DB_USER, DB_PASSWORD, DECISIONALDB)

    
    # ------------------------------------------------------------------------------
    # Configuration de la base de donnees
    # ------------------------------------------------------------------------------
    DB_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{HOST}:5432/{DB_NAME}'

    engine = create_engine(DB_URI)
    Session = sessionmaker(bind=engine)
    session = Session()
    wait_for_postgresql(host=HOST, port=PORT, user=DB_USER, password=DB_PASSWORD, dbname=DB_NAME)
    Base.metadata.create_all(engine)

    conn_params = {
        'dbname': DB_NAME,
        'user': DB_USER,
        'password': DB_PASSWORD,
        'host': HOST,
        'port': PORT
    }
    with psycopg2.connect(**conn_params) as conn:
        with conn.cursor() as cur:
            query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            """
            cur.execute(query)
            existing_tables = cur.fetchall()
            existing_tables = [table[0] for table in existing_tables]
            print("\033[1;92mTABLES CREATED SUCCESSFULLY.\033[0m \033[1;94m" + str(existing_tables) + "\033[0m")

    # --------------------------------------------------------
    # 0.6 Insertion of data in database
    # --------------------------------------------------------
    try:

        bank_reviews.duplicated(subset=['Reviewer_Name', 'Reviewer_Star', 'Reviewer_Text', 'Reviewer_Publish_Date']).sum()
        bank_reviews.drop_duplicates(subset=['Reviewer_Name', 'Reviewer_Star', 'Reviewer_Text', 'Reviewer_Publish_Date'], inplace=True)
        
        insert_data_from_dataframe(bank_reviews, session)
        migration_to_decisionalDB(DB_USER=DB_USER,DB_HOST=HOST, DB_PASSWORD=DB_PASSWORD, trans_engine=engine)
        session.commit()
    except IntegrityError as e:
        print("Erreur d'intégrité : ", e)
    session.rollback()

    
if __name__ == "__main__":
    main()
    