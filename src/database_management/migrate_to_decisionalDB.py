from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pandas as pd

def migration_to_decisionalDB(DB_USER, DB_PASSWORD, trans_engine=None, DB_NAME='decisional_db', HOST='localhost'):
    # Connexion à la base de données décisionnelle
    DB_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{HOST}:5432/{DB_NAME}'
    decis_engine = create_engine(DB_URI)
    DecisSession = sessionmaker(bind=decis_engine)
    decis_session = DecisSession()

    # Extraction des données depuis la base de données transactionnelle
    countries = pd.read_sql('SELECT * FROM countries', trans_engine)
    towns = pd.read_sql('SELECT * FROM towns', trans_engine)
    banks = pd.read_sql('SELECT * FROM banks', trans_engine)
    reviewers = pd.read_sql('SELECT * FROM reviewers', trans_engine)
    topics = pd.read_sql('SELECT * FROM topics', trans_engine)
    sentiments = pd.read_sql('SELECT * FROM sentiments', trans_engine)
    sub_topics = pd.read_sql('SELECT * FROM sub_topics', trans_engine)
    reviews = pd.read_sql('SELECT * FROM reviews', trans_engine)

    # Combinaison des topics et sub_topics dans un seul DataFrame
    topics_with_sub_topics = topics.merge(sub_topics, left_on='id', right_on='topic_id', suffixes=('_topic', '_sub_topic'))
    columns_needed = ['id', 'topic_id', 'sub_topic_name']
    missing_columns = [col for col in columns_needed if col not in topics_with_sub_topics.columns]
    print(f"Columns : {topics_with_sub_topics.columns}")

    new_column_names = ['id_topic', 'topic_name', 'id_sub_topic', 'topic_id', 'sub_topic_name']

    if len(topics_with_sub_topics.columns) == len(new_column_names):
        topics_with_sub_topics.columns = new_column_names
    else:
        raise ValueError(f"Le nombre de colonnes dans le DataFrame ({len(topics_with_sub_topics.columns)}) ne correspond pas au nombre de nouveaux noms ({len(new_column_names)})")

    # Chargement des données dans la base de données décisionnelle
    countries.to_sql('dimension_country', decis_engine, if_exists='replace', index=False)
    towns.to_sql('dimension_town', decis_engine, if_exists='replace', index=False)
    banks.to_sql('dimension_bank', decis_engine, if_exists='replace', index=False)
    reviewers.to_sql('dimension_reviewer', decis_engine, if_exists='replace', index=False)
    topics_with_sub_topics.to_sql('dimension_topic', decis_engine, if_exists='replace', index=False)
    sentiments.to_sql('dimension_sentiment', decis_engine, if_exists='replace', index=False)

    # Préparation de la table Dimension_Time
    print("Columns in reviews before creating time_df:", reviews.columns)  # Diagnostic print

    if 'publish_date' in reviews.columns:
        reviews['publish_date'] = pd.to_datetime(reviews['publish_date'])
        time_df = reviews[['publish_date']].drop_duplicates()
        time_df['week'] = time_df['publish_date'].dt.isocalendar().week
        time_df['month'] = time_df['publish_date'].dt.month
        time_df['year'] = time_df['publish_date'].dt.year
        time_df = time_df[['week', 'month', 'year', 'publish_date']].drop_duplicates().reset_index(drop=True)
        print("Columns in time_df after creation:", time_df.columns)  # Diagnostic print
        time_df.to_sql('dimension_time', decis_engine, if_exists='replace', index=False)
    else:
        raise KeyError("'publish_date' not found in reviews")

    # Préparation de la table des faits
    fact_reviews = reviews[['id', 'reviewer_id', 'bank_id', 'publish_date', 'star_rating', 'like_reaction', 'topic_id', 'sentiment_id']]
    fact_reviews.columns = ['review_id', 'reviewer_id', 'bank_id', 'publish_date', 'star_rating', 'like_reaction', 'topic_id', 'sentiment_id']
    fact_reviews['count_review'] = 1  # Ajouter une colonne pour le comptage des avis
    fact_reviews = fact_reviews.groupby(['review_id', 'bank_id', 'reviewer_id', 'publish_date', 'star_rating', 'like_reaction', 'topic_id', 'sentiment_id']).sum().reset_index()

    # Insertion des faits en utilisant des clés étrangères
    time_df = pd.read_sql('SELECT * FROM dimension_time', decis_engine)
    print("Columns in time_df after loading from database:", time_df.columns)  # Diagnostic print

    # Vérification de l'existence de 'publish_date'
    if 'publish_date' in time_df.columns:
        fact_reviews = fact_reviews.merge(time_df[['publish_date', 'week']], 
                                          left_on='publish_date', 
                                          right_on='publish_date', 
                                          suffixes=('', '_time'))
    else:
        raise KeyError("'publish_date' not found in time_df")

    fact_reviews = fact_reviews[['review_id', 'bank_id', 'reviewer_id', 'week', 'topic_id', 'sentiment_id', 'count_review']]
    fact_reviews.columns = ['review_id', 'bank_id', 'reviewer_id', 'time_week', 'topic_id', 'sentiment_id', 'count_review']
    fact_reviews.to_sql('fact_reviews', decis_engine, if_exists='replace', index=False)

    # Impression de l'état d'avancement avec une couleur verte
    print("\033[1;92mMIGRATION TO DECISION-SUPPORT DATABASE COMPLETED SUCCESSFULLY.\033[0m")
    print("\033[1;94mTables created in decision-support database:\033[0m")
    print("\033[1;94m [dimension_country, dimension_town, dimension_bank, dimension_reviewer, dimension_time, dimension_topic, dimension_sentiment, fact_reviews]\033[0m")
