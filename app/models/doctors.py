from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from app.core.database import Base
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class Doctor(Base):
    __tablename__ = "doctors"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    division = Column(String(50), nullable=False)
    district = Column(String(50), nullable=False)
    chamber_location = Column(String(150), nullable=False)
    appoint_number = Column(String(15), nullable=False)
    appointment_day = Column(String(10), nullable=False)
    fee = Column(Integer, nullable=False)