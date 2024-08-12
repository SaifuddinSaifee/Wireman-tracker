# File: database/models.py

from sqlalchemy import Column, Integer, String, Date, Numeric, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Wireman(Base):
    __tablename__ = "wiremen"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    contact_info = Column(String)
    date_registered = Column(Date)

    bills = relationship("Bill", back_populates="wireman")
    points = relationship("Point", back_populates="wireman")

class Bill(Base):
    __tablename__ = "bills"

    id = Column(Integer, primary_key=True, index=True)
    wireman_id = Column(Integer, ForeignKey("wiremen.id"))
    client_name = Column(String)
    amount = Column(Numeric(10, 2))
    date = Column(Date)
    payment_status = Column(String)
    points_earned = Column(Numeric(10, 2))

    wireman = relationship("Wireman", back_populates="bills")

class Point(Base):
    __tablename__ = "points"

    id = Column(Integer, primary_key=True, index=True)
    wireman_id = Column(Integer, ForeignKey("wiremen.id"))
    total_points = Column(Numeric(10, 2))
    redeemed_points = Column(Numeric(10, 2))
    balance_points = Column(Numeric(10, 2))

    wireman = relationship("Wireman", back_populates="points")