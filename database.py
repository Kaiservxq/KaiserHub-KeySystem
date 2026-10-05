from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, String, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///./keys.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class KeyModel(Base):
  __tablename__ = "keys"

  key = Column(String, primary_key=True, index=True)
  owner = Column(String, nullable=False)
  hwid = Column(String, nullable=True)
  is_active = Column(Boolean, default=True)
  created_at = Column(DateTime, default=datetime.utcnow)


Base.metadata.create_all(bind=engine)