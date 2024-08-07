
from db_models import BankManager, ReviewerManager, TopicManager, CountryManager, SentimentManager, SubTopicManager, TownManager, ReviewManager
import pandas as pd


def insert_data_from_dataframe(df, session):
    country_manager = CountryManager(session)
    town_manager = TownManager(session)
    bank_manager = BankManager(session)
    reviewer_manager = ReviewerManager(session)
    topic_manager = TopicManager(session)
    sentiment_manager = SentimentManager(session)
    sub_topic_manager = SubTopicManager(session)
    review_manager = ReviewManager(session)
    
    default_date = pd.Timestamp('1970-01-01')
    df['Reviewer_Publish_Date'] = df['Reviewer_Publish_Date'].fillna(default_date)
    df['Reviewer_Owner_Reply_Date'] = df['Reviewer_Owner_Reply_Date'].fillna(default_date)

    # Ensure conversion to datetime
    df['Reviewer_Publish_Date'] = pd.to_datetime(df['Reviewer_Publish_Date'], errors='coerce').fillna(default_date)
    df['Reviewer_Owner_Reply_Date'] = pd.to_datetime(df['Reviewer_Owner_Reply_Date'], errors='coerce').fillna(default_date)


    for _, row in df.iterrows():
        country_name = str(row['Country'])
        town_name = str(row['Town'])
        bank_name = str(row['Bank_Name'])
        reviewer_name = str(row['Reviewer_Name'])
        reviewer_profile_link = str(row['Reviewer_Profile_Link'])
        topic_name = str(row['Topic'])
        sentiment_name = str(row['Sentiment'])
        sub_topic_name = str(row['Sub_Topic'])
        
        country = country_manager.get_or_create_country(country_name)
        town = town_manager.get_or_create_town(town_name, country.id)
        bank_data = {
            'bank_name': bank_name,
            'phone_number': str(row['Bank_Phone_number']),
            'address': str(row['Bank_Address']),
            'website': str(row['Bank_Website']),
            'town_id': town.id
        }
        bank = bank_manager.get_or_create_bank(bank_data)
        reviewer = reviewer_manager.get_or_create_reviewer(reviewer_name, reviewer_profile_link)
        topic = topic_manager.get_or_create_topic(topic_name)
        sentiment = sentiment_manager.get_or_create_sentiment(sentiment_name)
        sub_topic = sub_topic_manager.get_or_create_sub_topic(sub_topic_name)
        
        # Handle NaN values in star_rating and like_reaction
        star_rating = row['Reviewer_Star'] if pd.notna(row['Reviewer_Star']) else 0  # Default value is 0 if NaN
        like_reaction = row['Reviewer_Like_Reaction'] if pd.notna(row['Reviewer_Like_Reaction']) else 0  # Default value is 0 if NaN
        
        review_data = {
            'reviewer_id': reviewer.id,
            'bank_id': bank.id,
            'publish_date': row['Reviewer_Publish_Date'],
            'star_rating': int(star_rating),
            'review_text': str(row['Reviewer_Text']),
            'like_reaction': int(like_reaction),
            'owner_reply': str(row['Reviewer_Owner_Reply']),
            'owner_reply_date': row['Reviewer_Owner_Reply_Date'],
            'topic_id': topic.id,
            'sentiment_id': sentiment.id,
            'sub_topic_id': sub_topic.id
        }

        review_manager.create_review(review_data)
        
    session.commit()
    # print with color
    print("\033[1;92mDATA INSERTED SUCCESSFULLY.\033[0m")
