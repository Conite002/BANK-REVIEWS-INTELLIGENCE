from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd

def migration_to_decisionalDB(DB_USER, DB_PASSWORD, trans_engine=None, DB_NAME='decisional_db', DB_HOST='localhost'):
    DB_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:5432/{DB_NAME}'
    decis_engine = create_engine(DB_URI, echo=True)
    DecisSession = sessionmaker(bind=decis_engine)
    decis_session = DecisSession()

    # Use a connection object instead of the engine directly
    with trans_engine.connect() as connection:
        countries = pd.read_sql('SELECT * FROM countries', connection)
        towns = pd.read_sql('SELECT * FROM towns', connection)
        banks = pd.read_sql('SELECT * FROM banks', connection)
        reviewers = pd.read_sql('SELECT * FROM reviewers', connection)
        topics = pd.read_sql('SELECT * FROM topics', connection)
        sentiments = pd.read_sql('SELECT * FROM sentiments', connection)
        sub_topics = pd.read_sql('SELECT * FROM sub_topics', connection)
        reviews = pd.read_sql('SELECT * FROM reviews', connection)


    # Fusionner les sujets avec les sous-sujets
    if 'id' in topics.columns and 'topic_id' in sub_topics.columns:
        topics_with_sub_topics = topics.merge(sub_topics, left_on='id', right_on='topic_id', suffixes=('_topic', '_sub_topic'))
    else:
        raise ValueError("Les colonnes nécessaires pour la fusion sont manquantes dans les DataFrames")

    # print("Colonnes après fusion :", topics_with_sub_topics.columns)

    # Colonnes attendues
    expected_columns = ['id_topic', 'topic_name', 'id_sub_topic', 'topic_id', 'sub_topic_name']
    missing_columns = [col for col in expected_columns if col not in topics_with_sub_topics.columns]

    if missing_columns:
        raise ValueError(f"Colonnes manquantes dans topics_with_sub_topics : {missing_columns}")
    else:
        # Renommer les colonnes si tout est en ordre
        topics_with_sub_topics.columns = expected_columns


    # Insertion des données dans les tables dimensionnelles
    countries.to_sql('dimension_country', decis_engine, if_exists='replace', index=False)
    towns.to_sql('dimension_town', decis_engine, if_exists='replace', index=False)
    banks.to_sql('dimension_bank', decis_engine, if_exists='replace', index=False)
    reviewers.to_sql('dimension_reviewer', decis_engine, if_exists='replace', index=False)
    topics_with_sub_topics.to_sql('dimension_topic', decis_engine, if_exists='replace', index=False)
    sentiments.to_sql('dimension_sentiment', decis_engine, if_exists='replace', index=False)

    # Création de la dimension temps
    if 'publish_date' in reviews.columns:
        reviews['publish_date'] = pd.to_datetime(reviews['publish_date'])
        time_df = reviews[['publish_date']].drop_duplicates()
        time_df['week'] = time_df['publish_date'].dt.isocalendar().week
        time_df['month'] = time_df['publish_date'].dt.month
        time_df['year'] = time_df['publish_date'].dt.year
        time_df = time_df[['week', 'month', 'year', 'publish_date']].drop_duplicates().reset_index(drop=True)
        time_df.to_sql('dimension_time', decis_engine, if_exists='replace', index=False)
    else:
        raise KeyError("'publish_date' non trouvé dans reviews")

    # Création de la dimension région

    if 'country_id' in towns.columns and 'id' in countries.columns:
        regions = towns.merge(countries, left_on='country_id', right_on='id', suffixes=('_town', '_country'))
    else:
        missing_columns = []
        if 'country_id' not in towns.columns:
            missing_columns.append('country_id in towns')
        if 'id' not in countries.columns:
            missing_columns.append('id in countries')
        raise KeyError(f"Les colonnes suivantes sont manquantes pour la fusion : {', '.join(missing_columns)}")
    
    
    # Préparer la table dimension_region
    regions = regions[['id_town', 'town_name', 'country_id', 'country_name']]
    regions.columns = ['id_region', 'town_name', 'country_id', 'country_name']
    regions.to_sql('dimension_region', decis_engine, if_exists='replace', index=False)

    # Préparation de la table des faits
    fact_reviews = reviews[['id', 'reviewer_id', 'bank_id', 'publish_date', 'star_rating', 'like_reaction', 'topic_id', 'sentiment_id']]
    fact_reviews.columns = ['review_id', 'reviewer_id', 'bank_id', 'publish_date', 'star_rating', 'like_reaction', 'topic_id', 'sentiment_id']
    fact_reviews['count_review'] = 1
    fact_reviews = fact_reviews.groupby(['review_id', 'bank_id', 'reviewer_id', 'publish_date', 'star_rating', 'like_reaction', 'topic_id', 'sentiment_id']).sum().reset_index()

    # Fusionner les informations temporelles avec les avis
    time_df = pd.read_sql('SELECT * FROM dimension_time', decis_engine)
    if 'publish_date' in time_df.columns:
        fact_reviews = fact_reviews.merge(time_df[['publish_date', 'week']], 
                                        left_on='publish_date', 
                                        right_on='publish_date', 
                                        suffixes=('', '_time'))
    else:
        raise KeyError("'publish_date' non trouvé dans time_df")

    # Fusionner les informations de région
    fact_reviews = fact_reviews.merge(regions[['id_region', 'town_name', 'country_name']], 
                                    left_on='bank_id', 
                                    right_on='id_region', 
                                    suffixes=('', '_region'))

    fact_reviews = fact_reviews[['review_id', 'bank_id', 'reviewer_id', 'week', 'topic_id', 'sentiment_id', 'count_review', 'town_name', 'country_name']]
    fact_reviews.columns = ['review_id', 'bank_id', 'reviewer_id', 'time_week', 'topic_id', 'sentiment_id', 'count_review', 'town_name', 'country_name']

    # Insérer dans la base de données
    fact_reviews.to_sql('fact_reviews', decis_engine, if_exists='replace', index=False)

    print("\033[1;92mMIGRATION TO DECISION-SUPPORT DATABASE COMPLETED SUCCESSFULLY.\033[0m")
    print("\033[1;94mTables created in decision-support database:\033[0m")
    print("\033[1;94m [dimension_country, dimension_town, dimension_bank, dimension_reviewer, dimension_time, dimension_topic, dimension_sentiment, dimension_region, fact_reviews]\033[0m")
