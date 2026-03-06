"""
DATABASE MODULE
===============
Handles all database operations for the chatbot.

Creates and manages:
- Customers table
- Conversations table  
- BookingInquiry table
- LeadScore table

USAGE:
from database import save_customer, save_conversation, etc.
"""
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime

DATABASE_URL = "sqlite:///hotel_leads.db"
engine = create_engine(DATABASE_URL, echo=False)

Base = declarative_base()
Session = sessionmaker(bind=engine)

class Customer(Base):
    __tablename__ = 'customers'
    
    id = Column(Integer, primary_key=True)
    sender_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(200))
    phone = Column(String(50))
    email = Column(String(200))
    first_message_date = Column(DateTime, default=datetime.now)
    last_message_date = Column(DateTime, default=datetime.now)
    total_messages = Column(Integer, default=0)
    status = Column(String(50), default='new')

class Conversation(Base):
    __tablename__ = 'conversations'
    
    id = Column(Integer, primary_key=True)
    sender_id = Column(String(100), nullable=False)
    message = Column(Text)
    response = Column(Text)
    timestamp = Column(DateTime, default=datetime.now)
    message_type = Column(String(50))

class BookingInquiry(Base):
    __tablename__ = 'booking_inquiries'
    
    id = Column(Integer, primary_key=True)
    sender_id = Column(String(100), nullable=False)
    name = Column(String(200))
    phone = Column(String(50))
    email = Column(String(200))
    checkin_date = Column(String(100))
    checkout_date = Column(String(100))
    num_guests = Column(Integer)
    room_type = Column(String(100))
    special_requests = Column(Text)
    confirmation_number = Column(String(50))
    inquiry_date = Column(DateTime, default=datetime.now)
    status = Column(String(50), default='pending')

class LeadScore(Base):
    __tablename__ = 'lead_scores'
    
    id = Column(Integer, primary_key=True)
    sender_id = Column(String(100), unique=True, nullable=False)
    score = Column(Integer, default=0)
    asked_about_rates = Column(Integer, default=0)
    asked_about_availability = Column(Integer, default=0)
    asked_about_booking = Column(Integer, default=0)
    clicked_book_button = Column(Integer, default=0)
    provided_contact = Column(Integer, default=0)
    last_updated = Column(DateTime, default=datetime.now)

def init_db():
    Base.metadata.create_all(engine)
    print("✅ Database initialized!")

def save_customer(sender_id, name=None, phone=None, email=None):
    session = Session()
    try:
        customer = session.query(Customer).filter_by(sender_id=sender_id).first()
        
        if customer:
            if name:
                customer.name = name
            if phone:
                customer.phone = phone
            if email:
                customer.email = email
            customer.last_message_date = datetime.now()
            customer.total_messages += 1
        else:
            customer = Customer(
                sender_id=sender_id,
                name=name,
                phone=phone,
                email=email,
                total_messages=1
            )
            session.add(customer)
        
        session.commit()
        return customer
    except Exception as e:
        session.rollback()
        print(f"❌ Error saving customer: {e}")
    finally:
        session.close()

def save_conversation(sender_id, message, response, message_type='user_message'):
    session = Session()
    try:
        conversation = Conversation(
            sender_id=sender_id,
            message=message,
            response=response,
            message_type=message_type
        )
        session.add(conversation)
        session.commit()
    except Exception as e:
        session.rollback()
        print(f"❌ Error saving conversation: {e}")
    finally:
        session.close()

def save_booking_inquiry(sender_id, name=None, phone=None, email=None, 
                        checkin=None, checkout=None, guests=None, room_type=None):
    session = Session()
    try:
        inquiry = BookingInquiry(
            sender_id=sender_id,
            name=name,
            phone=phone,
            email=email,
            checkin_date=checkin,
            checkout_date=checkout,
            num_guests=guests,
            room_type=room_type
        )
        session.add(inquiry)
        session.commit()
        return inquiry
    except Exception as e:
        session.rollback()
        print(f"❌ Error saving booking: {e}")
    finally:
        session.close()

def update_lead_score(sender_id, action):
    session = Session()
    try:
        lead = session.query(LeadScore).filter_by(sender_id=sender_id).first()
        
        if not lead:
            lead = LeadScore(sender_id=sender_id)
            session.add(lead)
        
        if action == 'asked_rates':
            lead.asked_about_rates += 1
            lead.score += 10
        elif action == 'asked_availability':
            lead.asked_about_availability += 1
            lead.score += 20
        elif action == 'asked_booking':
            lead.asked_about_booking += 1
            lead.score += 30
        elif action == 'clicked_book':
            lead.clicked_book_button += 1
            lead.score += 40
        elif action == 'provided_contact':
            lead.provided_contact += 1
            lead.score += 50
        
        session.commit()
        return lead
    except Exception as e:
        session.rollback()
        print(f"❌ Error updating lead score: {e}")
    finally:
        session.close()

def get_customer(sender_id):
    session = Session()
    try:
        return session.query(Customer).filter_by(sender_id=sender_id).first()
    finally:
        session.close()

def get_all_customers(limit=100):
    session = Session()
    try:
        return session.query(Customer).order_by(Customer.last_message_date.desc()).limit(limit).all()
    finally:
        session.close()

def get_hot_leads(min_score=50, limit=20):
    session = Session()
    try:
        return session.query(LeadScore).filter(LeadScore.score >= min_score).order_by(LeadScore.score.desc()).limit(limit).all()
    finally:
        session.close()

def get_pending_bookings():
    session = Session()
    try:
        return session.query(BookingInquiry).filter_by(status='pending').order_by(BookingInquiry.inquiry_date.desc()).all()
    finally:
        session.close()

init_db()
