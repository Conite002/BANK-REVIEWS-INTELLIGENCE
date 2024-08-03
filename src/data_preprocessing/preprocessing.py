import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))
from src.data_preprocessing.utils import remove_some_cols

from data_preprocessing.utils import parse_relative_date, generate_static_topics_and_sentiments
# from utils import parse_relative_date, generate_static_topics_and_sentiments
import pandas as pd
import numpy as np

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
        if row['Reviewer_Text'] == 'NAN':
            topic = generate_static_topics_and_sentiments(row['Reviewer_Star'])
            row['Reviewer_Text'] = topic
        return row
    
    if 'Reviewer_Text' in df.columns and 'Reviewer_Star' in df.columns:
        df = df.apply(handle_nan_reviewer_text, axis=1)

    # Filling NaN values
    default_date = pd.Timestamp('1970-01-01')
    df = df.fillna({
        'Reviewer_Publish_Date': default_date,
        'Reviewer_Owner_Reply_Date': default_date
    }).infer_objects(copy=False)

    # Using map instead of applymap
    df = df.map(lambda x: None if pd.isna(x) else x)


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

    # --------------------------------------------------------
    # 0.6 Ensure conversion to datetime
    # --------------------------------------------------------
    df['Reviewer_Publish_Date'] = pd.to_datetime(df['Reviewer_Publish_Date'], errors='coerce').fillna(default_date)
    df['Reviewer_Owner_Reply_Date'] = pd.to_datetime(df['Reviewer_Owner_Reply_Date'], errors='coerce').fillna(default_date)

    # print(df.head())
    print(f"Invalid publish dates: {df['Reviewer_Publish_Date'].isna().sum()}")
    print(f"Invalid owner reply dates: {df['Reviewer_Owner_Reply_Date'].isna().sum()}")

    # --------------------------------------------------------
    # 0.7 Replace NaN values with appropriate defaults
    # --------------------------------------------------------
    df['Reviewer_Star'] = df['Reviewer_Star'].fillna(0)
    df['Reviewer_Like_Reaction'] = df['Reviewer_Like_Reaction'].fillna(0)
    df['Reviewer_Name'] = df['Reviewer_Name'].fillna('Anonymous')
    df['Reviewer_Text'] = df['Reviewer_Text'].fillna('')
    df['Reviewer_Profile_Link'] = df['Reviewer_Profile_Link'].fillna('')
    df['Reviewer_Owner_Reply'] = df['Reviewer_Owner_Reply'].fillna('')

    # After filling NaNs, make sure there are no NaNs left
    # print(df.isna().sum())
    # print(df.dtypes)

    return df