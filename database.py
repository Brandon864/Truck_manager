from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)

class Truck(Base):
    __tablename__ = 'trucks'
    id = Column(Integer, primary_key=True)
    truck_id = Column(String, unique=True)
    type = Column(String)
    capacity = Column(Float)
    status = Column(String, default='Available')

class Driver(Base):
    __tablename__ = 'drivers'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    phone = Column(String)
    license_number = Column(String)
    email = Column(String, nullable=True)
    truck_id = Column(Integer, ForeignKey('trucks.id'), nullable=True)
    truck = relationship('Truck', backref='drivers')

class Delivery(Base):
    __tablename__ = 'deliveries'
    id = Column(Integer, primary_key=True)
    pickup_location = Column(String)
    dropoff_location = Column(String)
    truck_id = Column(Integer, ForeignKey('trucks.id'))
    driver_id = Column(Integer, ForeignKey('drivers.id'))
    status = Column(String, default='Pending') 
    start_datetime = Column(DateTime, nullable=True)
    truck = relationship('Truck', backref='deliveries')
    driver = relationship('Driver', backref='deliveries')

# Initialize database
engine = create_engine('sqlite:///truck_manager.db')
Base.metadata.create_all(engine)
Session = sessionmaker(bind=engine)