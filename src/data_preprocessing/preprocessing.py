import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from src.data_preprocessing.utils import remove_some_cols

from data_preprocessing.utils import parse_relative_date, generate_static_topics_and_sentiments, generate_static_reviews_form_stars
# from utils import parse_relative_date, generate_static_topics_and_sentiments
import pandas as pd
import numpy as np
from topificator import TopicExtractor
import pandas as pd
from datetime import datetime, timedelta
from tqdm import tqdm


def preprocess_dataframe(df):
    # --------------------------------------------------------
    # 0.1 Drop duplicates
    # --------------------------------------------------------
    df = df.drop_duplicates()

    # --------------------------------------------------------
    # 0.2 Apply transformations
    # --------------------------------------------------------
    TRANSFORMATIONS = {
        'Country': lambda x: x.strip().title(),
        'Town': lambda x: x.strip().title(),
        'Bank_Name': lambda x: x.strip().title(),
        'Bank_Phone_number': lambda x: x.strip(),
        'Bank_Address': lambda x: x.strip().title(),
        'Bank_Website': lambda x: x.strip().lower(),
        'Reviewer_Name': lambda x: x.strip().title(),
        'Reviewer_Star': lambda x: int(x),
        'Reviewer_Text': lambda x: x.strip(),
        'Reviewer_Publish_Date': lambda x: parse_relative_date(x),
        'Reviewer_Like_Reaction': lambda x: int(x),
        'Reviewer_Profile_Link': lambda x: x.strip(),
        'Reviewer_Owner_Reply': lambda x: str(x).strip(),
        'Reviewer_Owner_Reply_Date': lambda x: parse_relative_date(x) if pd.notnull(x) or x!="NAN" else None
    }

    # Use .loc to avoid SettingWithCopyWarning
    df.loc[:, 'Reviewer_Publish_Date'] = df['Reviewer_Publish_Date'].str.replace('\xa0', ' ')
    df.loc[:, 'Reviewer_Text'] = df['Reviewer_Text'].replace(np.nan, 'NAN')

    # Use .loc in the loop to avoid SettingWithCopyWarning
    for column, transformation in TRANSFORMATIONS.items():
        if column in df.columns:
            df.loc[:, column] = df[column].apply(transformation)

    # --------------------------------------------------------
    # 0.3 Handle NaN values of reviews text with  reviewer_start
    # --------------------------------------------------------
    def handle_nan_reviewer_text(row):
        if pd.isna(row['Reviewer_Text']) or row['Reviewer_Text'] == 'NAN' or row['Reviewer_Text'].strip()=='':
            topic = generate_static_reviews_form_stars(row['Reviewer_Star'])
            row['Reviewer_Text'] = topic
        return row
    
    if 'Reviewer_Text' in df.columns and 'Reviewer_Star' in df.columns:
        df = df.apply(handle_nan_reviewer_text, axis=1)

    default_date = pd.Timestamp('1970-01-01')
    df = df.fillna({
        'Reviewer_Publish_Date': default_date,
        'Reviewer_Owner_Reply_Date': default_date
    }).infer_objects(copy=False)

    # --------------------------------------------------------
    # 0.4 Remove some columns
    # --------------------------------------------------------
    df = remove_some_cols(['date','country','city'], df)


    # --------------------------------------------------------
    # 0.5 Replace NaT values with a default date
    # --------------------------------------------------------
    default_date = pd.Timestamp('1970-01-01')
    df['Reviewer_Publish_Date'] = df['Reviewer_Publish_Date'].fillna(default_date)
    df['Reviewer_Owner_Reply_Date'] = df['Reviewer_Owner_Reply_Date'].fillna(default_date)
    def changeNAN_Nothings(row):
        if row == 'NAN':
            return 'Nothing'
    df['Reviewer_Owner_Reply'] = df['Reviewer_Owner_Reply'].apply(changeNAN_Nothings)

    # --------------------------------------------------------
    # 0.6 Ensure conversion to datetime
    # --------------------------------------------------------
    df['Reviewer_Publish_Date'] = pd.to_datetime(df['Reviewer_Publish_Date'], errors='coerce').fillna(default_date)
    df['Reviewer_Owner_Reply_Date'] = pd.to_datetime(df['Reviewer_Owner_Reply_Date'], errors='coerce').fillna(default_date)
    # --------------------------------------------------------
    # Extract topics and sentiments
    # --------------------------------------------------------
    extractor = TopicExtractor(model="llama3.1", patience=5)
    t = "L'application pour acceder a mon compte bug. On n'arrive pas pas a se connecter facilement."
    topics = extractor.extract(reviews=t, stars=5, type='SINGLE_SOURCE')
    print(f"Topic : {topics}")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(os.path.dirname(script_dir))
    output_directory = os.path.join(project_root, 'data', 'processed')
    output_directory = os.path.join(output_directory, datetime.now().strftime('%Y-%m-%d'))

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    output_file = os.path.join(output_directory, 'macro_llamma.csv')

    df_macro = pd.DataFrame()

    print(f"DIRECTORY : {output_directory}")
    header_written = False

    for index, row in tqdm(df.iterrows(), total=df.shape[0]):
        review = row['Reviewer_Text']
        stars = row['Reviewer_Star']
        try:
            topics = extractor.extract(reviews=review, stars=stars,  type='SINGLE_SOURCE')
            print(f"Topic {index} : {review} ::: {topics}")
            topics_array = topics['topics']
        
            if len(topics_array) == 0:
                static_topic, static_sentiment, static_sub_topic = generate_static_topics_and_sentiments(row['Reviewer_Sart'])
                new_row = row.copy()
                new_row['Topic'] = static_topic
                new_row['Sentiment'] = static_sentiment
                new_row['Sub_Topic'] = static_sub_topic
                df_macro = pd.concat([df_macro, pd.DataFrame([new_row])], ignore_index=True)
            else:
                for tuple_ in topics_array:
                    new_row = row.copy()
                    new_row['Topic'] = tuple_[0]
                    new_row['Sentiment'] = tuple_[1]
                    new_row['Sub_Topic'] = tuple_[2]
                    df_macro = pd.concat([df_macro, pd.DataFrame([new_row])], ignore_index=True)
        except Exception as e:
            print(f"Erreur rencontrée à l'index {index}: {e}")
            pass
    df_macro.to_csv(output_file, index=False)
    print(f"File written to {output_file}")
    return df_macro