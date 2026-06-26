import os
from sqlalchemy import create_engine, Column, String, Integer, Boolean, ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

#Match Environment Data
class MatchMetadata(Base):
    __tablename__ = 'valorant_matches'

    match_id   = Column(String,  primary_key=True)
    map_name   = Column(String,  nullable=False)
    queue_type = Column(String,  nullable=False)   # "competitive" | "unrated" | "swiftplay" …
    # Robust Safeguard:match delete:all its stats delete
    performance_stats = relationship(
        "PlayerMatchStats",
        backref="match",
        cascade="all, delete-orphan"
    )

class PlayerMatchStats(Base):
    __tablename__ = 'player_match_stats'

    id = Column(Integer, primary_key=True, autoincrement=True)
    match_id = Column(String,  ForeignKey('valorant_matches.match_id', ondelete='CASCADE'), nullable=False)
    agent_name = Column(String,  nullable=False)
    agent_role = Column(String,  nullable=False)
    kills = Column(Integer, default=0)
    deaths = Column(Integer, default=0)
    assists = Column(Integer, default=0)
    headshots = Column(Integer, default=0)
    bodyshots = Column(Integer, default=0)
    legshots = Column(Integer, default=0)
    won = Column(Boolean, nullable=True)   # True = win, False = loss, None = couldn't determine

DATABASE_URL = "sqlite:///local_valorant.db"

def init_db(drop_existing=False):
    engine = create_engine(DATABASE_URL)
    if drop_existing:
        print("Cleansing previous data structures...")
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("Robust relational tables created successfully!")
    return engine