import psycopg2
from psycopg2 import sql
import os, sys
import time
from psycopg2 import OperationalError
import pandas as pd
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))


class DatabaseInitializer:
    def __init__(self, admin_user, admin_password, host, port):
        self.admin_user = admin_user
        self.admin_password = admin_password
        self.host = host
        self.port = port

    def create_database_and_user(self, new_db_user, new_db_password, new_db_name):
        try:
            # Connexion à PostgreSQL en tant qu'administrateur
            admin_conn = psycopg2.connect(
                dbname='postgres',
                user=self.admin_user,
                password=self.admin_password,
                host=self.host,
                port=self.port
            )
            admin_conn.autocommit = True
            admin_cursor = admin_conn.cursor()

            # Vérification si l'utilisateur existe déjà
            admin_cursor.execute(sql.SQL("SELECT 1 FROM pg_roles WHERE rolname=%s"), (new_db_user,))
            user_exists = admin_cursor.fetchone()

            if user_exists:
                print(f"User {new_db_user} already exists.")
            else:
                # Création d'un nouvel utilisateur
                admin_cursor.execute(sql.SQL("CREATE USER {} WITH PASSWORD %s").format(sql.Identifier(new_db_user)), (new_db_password,))
                print(f"User {new_db_user} created successfully.")

            # Vérification si la base de données existe déjà
            admin_cursor.execute(sql.SQL("SELECT 1 FROM pg_database WHERE datname=%s"), (new_db_name,))
            db_exists = admin_cursor.fetchone()

            if db_exists:
                print(f"Database {new_db_name} already exists.")
            else:
                # Création d'une nouvelle base de données
                admin_cursor.execute(sql.SQL("CREATE DATABASE {} WITH OWNER {}").format(sql.Identifier(new_db_name), sql.Identifier(new_db_user)))
                print(f"Database {new_db_name} created successfully.")

            # Connexion à la nouvelle base de données pour accorder des privilèges
            db_conn = psycopg2.connect(
                dbname=new_db_name,
                user=self.admin_user,
                password=self.admin_password,
                host=self.host,
                port=self.port
            )
            db_conn.autocommit = True
            db_cursor = db_conn.cursor()

            # Grant all privileges on the database to the user
            db_cursor.execute(sql.SQL("GRANT ALL PRIVILEGES ON DATABASE {} TO {}").format(sql.Identifier(new_db_name), sql.Identifier(new_db_user)))
            print(f"Granted all privileges on database {new_db_name} to user {new_db_user}.")

            # Grant all privileges on the public schema to the user
            db_cursor.execute(sql.SQL("GRANT ALL PRIVILEGES ON SCHEMA public TO {}").format(sql.Identifier(new_db_user)))
            print(f"Granted all privileges on schema public to user {new_db_user}.")

            # Fermeture de la connexion
            admin_cursor.close()
            admin_conn.close()
            db_cursor.close()
            db_conn.close()
        except Exception as e:
            print(f"Error creating database and user: {e}")

    def drop_database_and_user(self, db_user, db_name):
        try:
            # Connexion à PostgreSQL en tant qu'administrateur
            admin_conn = psycopg2.connect(
                dbname='postgres',
                user=self.admin_user,
                password=self.admin_password,
                host=self.host,
                port=self.port
            )
            admin_conn.autocommit = True
            admin_cursor = admin_conn.cursor()

            # Révocation des droits de l'utilisateur sur la base de données
            admin_cursor.execute(sql.SQL("REVOKE ALL PRIVILEGES ON DATABASE {} FROM {}").format(sql.Identifier(db_name), sql.Identifier(db_user)))

            # Suppression de la base de données
            admin_cursor.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(db_name)))
            print(f"Database {db_name} dropped successfully.")

            # Suppression de l'utilisateur
            admin_cursor.execute(sql.SQL("DROP USER IF EXISTS {}").format(sql.Identifier(db_user)))
            print(f"User {db_user} dropped successfully.")

            # Fermeture de la connexion
            admin_cursor.close()
            admin_conn.close()
        except Exception as e:
            print(f"Error dropping database and user: {e}")


# def insert_data_from_dataframe(df, session):
#     country_manager = CountryManager(session)
#     town_manager = TownManager(session)
#     bank_manager = BankManager(session)
#     reviewer_manager = ReviewerManager(session)
#     topic_manager = TopicManager(session)
#     sentiment_manager = SentimentManager(session)
#     sub_topic_manager = SubTopicManager(session)
#     review_manager = ReviewManager(session)
    
#     default_date = pd.Timestamp('1970-01-01')
#     df['Reviewer_Publish_Date'] = df['Reviewer_Publish_Date'].fillna(default_date)
#     df['Reviewer_Owner_Reply_Date'] = df['Reviewer_Owner_Reply_Date'].fillna(default_date)

#     # Ensure conversion to datetime
#     df['Reviewer_Publish_Date'] = pd.to_datetime(df['Reviewer_Publish_Date'], errors='coerce').fillna(default_date)
#     df['Reviewer_Owner_Reply_Date'] = pd.to_datetime(df['Reviewer_Owner_Reply_Date'], errors='coerce').fillna(default_date)


#     for _, row in df.iterrows():
#         # S'assurer que les valeurs sont des chaînes de caractères
#         country_name = str(row['Country'])
#         town_name = str(row['Town'])
#         bank_name = str(row['Bank_Name'])
#         reviewer_name = str(row['Reviewer_Name'])
#         reviewer_profile_link = str(row['Reviewer_Profile_Link'])
#         topic_name = str(row['Topics'])
#         sentiment_name = str(row['Sentiments'])
#         sub_topic_name = str(row['Sub_Topics'])
        
#         country = country_manager.get_or_create_country(country_name)
#         town = town_manager.get_or_create_town(town_name, country.id)
#         bank_data = {
#             'bank_name': bank_name,
#             'phone_number': str(row['Bank_Phone_number']),
#             'address': str(row['Bank_Address']),
#             'website': str(row['Bank_Website']),
#             'town_id': town.id
#         }
#         bank = bank_manager.get_or_create_bank(bank_data)
#         reviewer = reviewer_manager.get_or_create_reviewer(reviewer_name, reviewer_profile_link)
#         topic = topic_manager.get_or_create_topic(topic_name)
#         sentiment = sentiment_manager.get_or_create_sentiment(sentiment_name)
#         sub_topic = sub_topic_manager.get_or_create_sub_topic(sub_topic_name)
        
#         # Handle NaN values in star_rating and like_reaction
#         star_rating = row['Reviewer_Star'] if pd.notna(row['Reviewer_Star']) else 0  # Default value is 0 if NaN
#         like_reaction = row['Reviewer_Like_Reaction'] if pd.notna(row['Reviewer_Like_Reaction']) else 0  # Default value is 0 if NaN
        
#         review_data = {
#             'reviewer_id': reviewer.id,
#             'bank_id': bank.id,
#             'publish_date': row['Reviewer_Publish_Date'],
#             'star_rating': int(star_rating),
#             'review_text': str(row['Reviewer_Text']),
#             'like_reaction': int(like_reaction),
#             'owner_reply': str(row['Reviewer_Owner_Reply']),
#             'owner_reply_date': row['Reviewer_Owner_Reply_Date'],
#             'topic_id': topic.id,
#             'sentiment_id': sentiment.id,
#             'sub_topic_id': sub_topic.id
#         }

#         review_manager.create_review(review_data)
        
#     session.commit()
#     # print with color
#     print("\033[92m" + "DATA INSERTED SUCCESSFULLY." + "\033[0m")
#     print("Data inserted successfully.")


def wait_for_postgresql(host, port, user, password, dbname):
    while True:
        try:
            conn = psycopg2.connect(host=host, port=port, user=user, password=password, dbname=dbname)

            conn.close()
            print("-------------------PostgreSQL is ready -------------------")
            break
        except OperationalError as e:
            print(f"Waiting for PostgreSQL to be ready... Error: {e}")
            time.sleep(5)