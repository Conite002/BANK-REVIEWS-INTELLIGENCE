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
----------------------------------------------------------------------------------------------------
# Date Table
`Filtering and Slicing by Date`: A Date Table lets you easily filter and slice your data by year, month, day, quarter, or other time periods.

`Correct Sorting of Dates`: Without a Date Table, Power BI might not handle dates correctly for sorting, especially if you want to group data by months or quarters.

`Date Granularity`: To display data at various levels of time granularity (like daily, monthly, or yearly trends), you need a Date Table with columns such as Year, Month, Day, Week, and Quarter.

# KPI
* 1. Total Number of Reviews

    TotalReviews = COUNTROWS('macro_llamma_v3')

* 2. Average Star Rating

    AverageRating = AVERAGE('macro_llamma_v3'[Reviewer_Star])

* 3. Positive/Negative Review Count

    PositiveReviews = CALCULATE(COUNTROWS('macro_llamma_v3'), 'macro_llamma_v3'[Sentiment] = "positive")
    NegativeReviews = CALCULATE(COUNTROWS('macro_llamma_v3'), 'macro_llamma_v3'[Sentiment] = "negative")

* 4. Owner Response Rate

    OwnerResponseRate = DIVIDE(COUNTROWS(FILTER('macro_llamma_v3', 'macro_llamma_v3'[Reviewer_Owner_Reply] <> "Nothing")), [TotalReviews])

* 5. Percentage of Reviews by Sentiment

    PercentagePositive = DIVIDE([PositiveReviews], [TotalReviews], 0) * 100
    PercentageNegative = DIVIDE([NegativeReviews], [TotalReviews], 0) * 100

* 6. Total Reviews by Topic

    <!-- TotalReviewsByTopic = CALCULATE(COUNTROWS('ReviewData'), 'ReviewData'[Topic] = "YourTopicName") -->

* 7. Average Reviews per Bank

    AverageReviewsPerBank = AVERAGEX(VALUES('ReviewData'[Bank_Name]), [TotalReviews])


* 8. PercentageNegativePerTown = 
DIVIDE(
    CALCULATE(
        COUNTROWS('ReviewData'),
        'ReviewData'[Sentiment] = "negative"
    ),
    CALCULATE(
        COUNTROWS('ReviewData'),
        'ReviewData'[Sentiment] = "negative",
        REMOVEFILTERS('ReviewData'[Town]) -- Ignore le filtre par ville pour obtenir le total global
    ),
    0
)*100

* 9. PositiveRatio

    PositiveRatio = DIVIDE([PositiveReviews], [TotalReviews], 0)

* 10. Negative Ratio

    NegativeRatio = DIVIDE([NegativeReviews], [TotalReviews], 0)

* 11. Classement des banques

    BankScore = [PositiveRatio] - [NegativeRatio]



# SCREENSHORTS
**HOME**
![alt text](./screenshorts/home.png)

**OVERVIEW BANK**
![alt text](./screenshorts/overview_bank.png)

**UNHAPPY CUSTOMER**
![alt text](./screenshorts/unhappy_customer.png)