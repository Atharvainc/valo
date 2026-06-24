# src/db_setup.py
import os
from sqlalchemy import create_engine,Column,String,Integer,DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from dotenv import load_dotenv

load_dotenv() 
Base = declarative_base()
class MatchMetadata(Base):
    __tablename__ = 'valorant_matches'
    
    match_id = Column(String, primary_key=True)
    map_name = Column(String)
    queue_type = Column(String)

class PlayerMatchStats(Base):
    __tablename__ = 'player_match_stats'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(String)
    puuid = Column(String)
    agent_name = Column(String)
    kills = Column(Integer)
    deaths = Column(Integer)
    assists = Column(Integer)
    
DATABASE_URL = "sqlite:///local_valorant.db" 

def init_db():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine) 
    print("Database tables initialized successfully.")
    return engine