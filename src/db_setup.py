import os
from pathlib import Path
from sqlalchemy import create_engine, Column, String, Integer, Boolean, ForeignKey, Index
from sqlalchemy.orm import declarative_base, relationship
from dotenv import load_dotenv

load_dotenv()

Base = declarative_base()

#Match Environment Data
class MatchMetadata(Base):
    __tablename__ = 'valorant_matches'

    match_id    = Column(String, primary_key=True)
    player_name = Column(String, nullable=False)
    player_tag  = Column(String, nullable=False)
    map_name    = Column(String, nullable=False)
    queue_type  = Column(String, nullable=False)

    performance_stats = relationship(
        "PlayerMatchStats", backref="match", cascade="all, delete-orphan"
    )

    __table_args__ = (
        Index('idx_player_queue', 'player_name', 'player_tag', 'queue_type'),
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

BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_URL = f"sqlite:///{BASE_DIR / 'local_valorant.db'}"

def init_db(drop_existing=False):
    engine = create_engine(DATABASE_URL)
    if drop_existing:
        print("Cleansing previous data structures...")
        Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    print("Robust relational tables created successfully!")
    return engine