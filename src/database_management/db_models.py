import pandas as pd
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, Date, ForeignKey, insert
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


# ------------------------------------------------------------------------------
# Definition des classes de modèle
# ------------------------------------------------------------------------------
class Country(Base):
    __tablename__ = 'countries'
    id = Column(Integer, primary_key=True)
    country_name = Column(String(255), unique=True, nullable=False) 
    towns = relationship('Town', back_populates='country')

class Town(Base):
    __tablename__ = 'towns'
    id = Column(Integer, primary_key=True)
    town_name = Column(String(255), unique=True, nullable=False)
    country_id = Column(Integer, ForeignKey('countries.id'))
    country = relationship('Country', back_populates='towns')
    banks = relationship('Bank', back_populates='town')

class Bank(Base):
    __tablename__ = 'banks'
    id = Column(Integer, primary_key=True)
    bank_name = Column(String(255), nullable=False)
    phone_number = Column(String(50))
    address = Column(String(255))
    website = Column(String(255))
    town_id = Column(Integer, ForeignKey('towns.id'))
    town = relationship('Town', back_populates='banks')


class Reviewer(Base):
    __tablename__ = 'reviewers'
    id = Column(Integer, primary_key=True)
    reviewer_name = Column(String(255))
    profile_link = Column(String(255))

class Topic(Base):
    __tablename__ = 'topics'
    id = Column(Integer, primary_key=True)
    topic_name = Column(String(255), unique=True, nullable=False)

class Sentiment(Base):
    __tablename__ = 'sentiments'
    id = Column(Integer, primary_key=True)
    sentiment_name = Column(String(255), unique=True, nullable=False)

class SubTopic(Base):
    __tablename__ = 'sub_topics'
    id = Column(Integer, primary_key=True)
    topic_id = Column(Integer, ForeignKey('topics.id'), nullable=False)
    sub_topic_name = Column(String(255), unique=True, nullable=False)

class Review(Base):
    __tablename__ = 'reviews'
    id = Column(Integer, primary_key=True)
    reviewer_id = Column(Integer, ForeignKey('reviewers.id'))
    bank_id = Column(Integer, ForeignKey('banks.id'))
    publish_date = Column(Date, nullable=False)
    star_rating = Column(Integer, nullable=False)
    review_text = Column(Text)
    like_reaction = Column(Integer)
    owner_reply = Column(Text)
    owner_reply_date = Column(Date)
    topic_id = Column(Integer, ForeignKey('topics.id'))
    sentiment_id = Column(Integer, ForeignKey('sentiments.id'))
    sub_topic_id = Column(Integer, ForeignKey('sub_topics.id'))



# ------------------------------------------------------------------------------
# Creation des tables
# ------------------------------------------------------------------------------

# Gestion des opérations liées aux pays
class CountryManager:
    def __init__(self, session):
        self.session = session
    
    def get_or_create_country(self, country_name):
        country = self.session.query(Country).filter_by(country_name=country_name).first()
        if not country:
            country = Country(country_name=country_name)
            self.session.add(country)
            self.session.commit()
        return country
    
# Gestion des opérations liées aux villes
class TownManager:
    def __init__(self, session):
        self.session = session
    
    def get_or_create_town(self, town_name, country_id):
        town = self.session.query(Town).filter_by(town_name=town_name).first()
        if not town:
            town = Town(town_name=town_name, country_id=country_id)
            self.session.add(town)
            self.session.commit()
        return town
    
# Gestion des opérations liées aux banques
class BankManager:
    def __init__(self, session):
        self.session = session
    
    def get_or_create_bank(self, bank_data):
        bank = self.session.query(Bank).filter_by(bank_name=bank_data['bank_name']).first()
        if not bank:
            bank = Bank(**bank_data)
            self.session.add(bank)
            self.session.commit()
        return bank

   
# Gestion des opérations liées aux reviewers
class ReviewerManager:
    def __init__(self, session):
        self.session = session
    
    def get_or_create_reviewer(self, reviewer_name, profile_link):
        reviewer = self.session.query(Reviewer).filter_by(reviewer_name=reviewer_name).first()
        if not reviewer:
            reviewer = Reviewer(reviewer_name=reviewer_name, profile_link=profile_link)
            self.session.add(reviewer)
            self.session.commit()
        return reviewer
    
# Gestion des opérations liées aux topics
class TopicManager:
    def __init__(self, session):
        self.session = session
    
    def get_or_create_topic(self, topic_name):
        topic = self.session.query(Topic).filter_by(topic_name=topic_name).first()
        if not topic:
            topic = Topic(topic_name=topic_name)
            self.session.add(topic)
            self.session.commit()
        return topic
    
# Gestion des opérations liées aux sentiments
class SentimentManager:
    def __init__(self, session):
        self.session = session
    
    def get_or_create_sentiment(self, sentiment_name):
        sentiment = self.session.query(Sentiment).filter_by(sentiment_name=sentiment_name).first()
        if not sentiment:
            sentiment = Sentiment(sentiment_name=sentiment_name)
            self.session.add(sentiment)
            self.session.commit()
        return sentiment
    

# Gestion des opérations liées aux sub_topics
class SubTopicManager:
    def __init__(self, session):
        self.session = session
    def get_or_create_sub_topic(self, sub_topic_name, topic_id):
        existing_sub_topic = self.session.query(SubTopic).filter_by(sub_topic_name=sub_topic_name).first()
        if existing_sub_topic:
            return existing_sub_topic
        new_sub_topic = SubTopic(topic_id=topic_id, sub_topic_name=sub_topic_name)
        self.session.add(new_sub_topic)
        self.session.commit()
        return new_sub_topic

# Gestion des opérations liées aux avis
class ReviewManager:
    def __init__(self, session):
        self.session = session
    
    def create_review(self, review_data):
        review = Review(**review_data)
        self.session.add(review)
        self.session.commit()
        return review
    
