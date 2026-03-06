"""
AUTOMATED REMINDERS
===================
Send automatic reminders and thank you messages.

USAGE:
python automated_reminders.py reminders    # Send check-in reminders
python automated_reminders.py thankyou     # Send thank you messages
"""
from database import Session, BookingInquiry
from templates import reminder_message_24h, thank_you_message
from datetime import datetime, timedelta
import requests
import os
from dotenv import load_dotenv

load_dotenv()

PAGE_ACCESS_TOKEN = os.getenv('PAGE_ACCESS_TOKEN')

def send_facebook_message(sender_id, text):
    """Send message via Facebook API"""
    url = f"https://graph.facebook.com/v18.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    
    data = {
        "recipient": {"id": sender_id},
        "message": {"text": text}
    }
    
    response = requests.post(url, params=params, json=data)
    return response.status_code == 200

def send_24h_reminders():
    """Send reminders 24 hours before check-in"""
    session = Session()
    try:
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%B %d')
        bookings = session.query(BookingInquiry).filter_by(status='confirmed').all()
        
        sent_count = 0
        for booking in bookings:
            if booking.checkin_date and tomorrow.lower() in booking.checkin_date.lower():
                booking_info = {
                    'name': booking.name,
                    'checkin': booking.checkin_date,
                    'guests': booking.num_guests
                }
                
                message = reminder_message_24h(booking_info, booking.confirmation_number)
                
                if send_facebook_message(booking.sender_id, message):
                    print(f"✅ Reminder sent to {booking.name}")
                    sent_count += 1
        
        print(f"\n📨 Sent {sent_count} reminders")
        return sent_count
    finally:
        session.close()

def send_thank_you_messages():
    """Send thank you messages after checkout"""
    session = Session()
    try:
        today = datetime.now().strftime('%B %d')
        bookings = session.query(BookingInquiry).filter_by(status='confirmed').all()
        
        sent_count = 0
        for booking in bookings:
            if booking.checkout_date and today.lower() in booking.checkout_date.lower():
                booking_info = {'name': booking.name}
                message = thank_you_message(booking_info)
                
                if send_facebook_message(booking.sender_id, message):
                    booking.status = 'completed'
                    session.commit()
                    print(f"✅ Thank you sent to {booking.name}")
                    sent_count += 1
        
        print(f"\n💖 Sent {sent_count} thank you messages")
        return sent_count
    finally:
        session.close()

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == 'reminders':
            send_24h_reminders()
        elif sys.argv[1] == 'thankyou':
            send_thank_you_messages()
        else:
            print("Usage: python automated_reminders.py [reminders|thankyou]")
    else:
        send_24h_reminders()
        send_thank_you_messages()
