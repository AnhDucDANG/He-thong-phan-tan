from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Booking(Base):
    __tablename__ = 'bookings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    customer_name = Column(String, nullable=False)
    booking_date = Column(DateTime, nullable=False)
    status = Column(String, default='pending')

    def __repr__(self):
        return f"<Booking(id={self.id}, customer_name={self.customer_name}, booking_date={self.booking_date}, status={self.status})>"