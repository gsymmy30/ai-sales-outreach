from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
import datetime

Base = declarative_base()

class EmailInteraction(Base):
    __tablename__ = 'email_interactions'

    id = Column(Integer, primary_key=True)
    linkedin_url = Column(String, nullable=False)
    name = Column(String)
    title = Column(String)
    company = Column(String)
    industry = Column(String)
    product_company = Column(String, nullable=False)
    product_description = Column(Text, nullable=False)
    research_summary = Column(Text)
    generated_email = Column(Text)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
