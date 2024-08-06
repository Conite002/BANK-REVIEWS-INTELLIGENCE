import pandas as pd
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker



def migration_to_decisionalDB(DB_USER, DB_PASSWORD, trans_engine, DB_NAME='decisional_db', HOST='HOST'):

    # Decision-support database connection
    decis_db_url = 'postgresql://username:password@localhost:5432/decisional_db'
    DB_URI = f'postgresql://{DB_USER}:{DB_PASSWORD}@{HOST}:5432/{DB_NAME}'

    decis_engine = create_engine(DB_URI)
    DecisSession = sessionmaker(bind=decis_engine)
    decis_session = DecisSession()
    

    # Extract data from transactional database
    countries = pd.read_sql('SELECT * FROM countries', trans_engine)
    towns = pd.read_sql('SELECT * FROM towns', trans_engine)
    banks = pd.read_sql('SELECT * FROM banks', trans_engine)
    reviewers = pd.read_sql('SELECT * FROM reviewers', trans_engine)
    topics = pd.read_sql('SELECT * FROM topics', trans_engine)
    sentiments = pd.read_sql('SELECT * FROM sentiments', trans_engine)
    sub_topics = pd.read_sql('SELECT * FROM sub_topics', trans_engine)
    reviews = pd.read_sql('SELECT * FROM reviews', trans_engine)

    # Combine topics and sub_topics into a single dataframe
    topics = topics.merge(sub_topics, left_index=True, right_index=True, suffixes=('_topic', '_sub_topic'))
    topics['topic_id'] = topics.index

    # Load data into decision-support database
    countries.to_sql('DimCountries', decis_engine, if_exists='replace', index=False)
    towns.to_sql('DimTowns', decis_engine, if_exists='replace', index=False)
    banks.to_sql('DimBanks', decis_engine, if_exists='replace', index=False)
    reviewers.to_sql('DimReviewers', decis_engine, if_exists='replace', index=False)
    topics.to_sql('DimTopicsSubTopics', decis_engine, if_exists='replace', index=False)
    sentiments.to_sql('DimSentiments', decis_engine, if_exists='replace', index=False)

    # Prepare fact table
    fact_reviews = reviews[['id', 'reviewer_id', 'bank_id', 'publish_date', 'star_rating', 'like_reaction', 'topic_id', 'sentiment_id']]
    fact_reviews.columns = ['review_id', 'reviewer_id', 'bank_id', 'publish_date', 'star_rating', 'like_reaction', 'topic_sub_topic_id', 'sentiment_id']
    fact_reviews.to_sql('FactReviews', decis_engine, if_exists='replace', index=False)

    # Print statement with green text color
    print("\033[92mMigration to decision-support database completed successfully.\033[0m")
