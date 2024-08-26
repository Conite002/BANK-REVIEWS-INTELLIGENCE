## BRI 
BankReviewIntelligence :  Insightful analytics and decision-making support based on customer reviews of banks.
This project aims to provide in-depth analysis and visualizations of customer reviews of banks. Data is extracted, transformed and loaded into a business intelligence database, then used to create interactive and informative visualizations.



## Architecture
<img src="./architecture.jpg" alt="project architecture draft" style="width: 100%"/>


# Plan Outline

## 01 Data Collection:

* Load Cities: Load city data from a JSON file.
* Scrape Reviews: Use Selenium to scrape reviews from Google Maps.
* Save Data: Save the scraped data into Parquet files.

## 02. Data Concatenation:

* Build Macro Table: Concatenate Parquet files into a single dataframe.

## 03.Data Preprocessing:

* Preprocess Data: Clean and preprocess the data.
* Generate Topics and Sentiments: Integrate topic and sentiment data.

## 04. Database Initialization:

* Database Creation: Create the PostgreSQL database and user.
    * The following tables are created in the PostgreSQL database:
        
        countries: Stores information about different countries.
        towns: Stores information about towns and their associated countries.
        banks: Stores information about banks, including name, phone number, address, website, and associated town.
        reviewers: Stores information about reviewers, including name and profile link.
        reviews: Stores information about reviews, including reviewer ID, bank ID, publish date, star rating, review text, like reaction, owner reply, owner reply date, topic ID, sentiment ID, and sub-topic ID.
        topics: Stores information about topics.
        sentiments: Stores information about sentiments.
        sub_topics: Stores information about sub-topics.


## 05. Recording
* Data Insertion: Insert data into the database.
* Data Retrieval: Retrieve data from the database.

* Schema Definition: Decisional database
* Data Migration: Transactional to Decisional
## Decision-Support Database Structure

### Fact Table

- **FactReviews**
  - `review_id` (Integer, Primary Key)
  - `reviewer_id` (Integer, Foreign Key)
  - `bank_id` (Integer, Foreign Key)
  - `publish_date` (Date, Not Null)
  - `star_rating` (Integer, Not Null)
  - `like_reaction` (Integer)
  - `topic_sub_topic_id` (Integer, Foreign Key)
  - `sentiment_id` (Integer, Foreign Key)

### Dimension Tables

- **DimCountries**
  - `country_id` (Integer, Primary Key)
  - `country_name` (String, Unique, Not Null)

- **DimTowns**
  - `town_id` (Integer, Primary Key)
  - `town_name` (String, Unique, Not Null)
  - `country_id` (Integer, Foreign Key)

- **DimBanks**
  - `bank_id` (Integer, Primary Key)
  - `bank_name` (String, Not Null)
  - `phone_number` (String)
  - `address` (String)
  - `website` (String)
  - `town_id` (Integer, Foreign Key)

- **DimReviewers**
  - `reviewer_id` (Integer, Primary Key)
  - `reviewer_name` (String)
  - `profile_link` (String)

- **DimTopicsSubTopics**
  - `topic_sub_topic_id` (Integer, Primary Key)
  - `topic_name` (String, Not Null)
  - `sub_topic_name` (String, Not Null)

- **DimSentiments**
  - `sentiment_id` (Integer, Primary Key)
  - `sentiment_name` (String, Unique, Not Null)

* Visualization

## Installation and Launch Superset

Make it executable:

bash
Copy code
chmod +x install_and_launch_superset.sh
Run the script:

bash
Copy code
sudo ./install_and_launch_superset.sh

## Directory Structure 

      BRI/
      │
      ├── data/
      │   ├── raw/                 # Données brutes collectées
      │   ├── processed/           # Données après prétraitement
      │   ├── temp/                # Fichiers temporaires
      │   └── parquet/             # Fichiers Parquet
      │
      ├── src/
      │   ├── __init__.py
      │   ├── config.py            # Configuration et paramètres
      │   ├── data_collection/
      │   │   ├── __init__.py
      │   │   ├── scraper.py       # Logique de collecte de données
      │   │   └── utils.py         # Fonctions utilitaires pour la collecte
      │   │
      │   ├── data_concatenation/
      │   │   ├── __init__.py
      │   │   └── concatenate.py   # Logique de concaténation des données
      │   │
      │   ├── data_preprocessing/
      │   │   ├── __init__.py
      │   │   ├── preprocessing.py # Prétraitement des données
      │   │   └── utils.py         # Fonctions utilitaires pour le prétraitement
      │   │
      │   ├── database_management/
      │   │   ├── __init__.py
      │   │   ├── db_models.py     # Définition des modèles de la base de données
      │   │   └── database_initializer.py # Création et gestion de la base de données
      │   │
      │   ├── visualization/
      │   │   ├── __init__.py
      │   │   └── visualization.py # Logique de visualisation (optionnel)
      │   │
      │   └── main.py              # Point d'entrée principal
      │
      ├── Dockerfile
      ├── docker-compose.yml       # Fichier de configuration Docker Compose
      ├── requirements.txt         # Dépendances Python
      ├── .dockerignore            # Fichiers et répertoires à ignorer par Docker
      ├── .gitignore               # Fichiers et répertoires à ignorer par Git
      ├── README.md                # Documentation du projet
      ├── entrypoint.sh            # 
      ├── install_and_launch_superset.sh            # 
      ├── Dockerfile.ollama
      └── superset_config.py

## Installation and Launch Superset
Make it executable:
chmod +x install_and_launch_superset.sh
./install_and_launch_superset.sh

```I used LLaMA 3.1 with Docker before. However, for performance reasons, I removed it from Docker and ran it on my local machine.```

## Run postgreSQL
docker compose build
docker compose up

<!-- SQLALCHEMY_DATABASE_URI = "postgresql://conite:conite_password@localhost:5432/bank_reviews" -->
