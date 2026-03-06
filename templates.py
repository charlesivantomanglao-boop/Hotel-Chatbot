"""
PROFESSIONAL MESSAGE TEMPLATES
===============================
Formal confirmation messages without emojis.
Maintains professional yet approachable tone.
"""
import random
import string
from datetime import datetime

def generate_confirmation_number():
    """Generate unique confirmation number (PR-YYMMDD-XXXX)"""
    date_part = datetime.now().strftime('%y%m%d')
    random_part = ''.join(random.choices(string.digits, k=4))
    return f"PR-{date_part}-{random_part}"

def booking_confirmation_message(booking_info, confirmation_number):
    """Generate professional booking confirmation"""
    message = f"""BOOKING CONFIRMATION

Dear {booking_info.get('name', 'Valued Guest')},

Thank you for choosing Paradise Resort. We are pleased to confirm your reservation.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESERVATION DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Confirmation Number: {confirmation_number}
Guest Name: {booking_info.get('name', 'N/A')}
Contact Number: {booking_info.get('phone', 'N/A')}

Check-in Date: {booking_info.get('checkin', 'N/A')}
Check-out Date: {booking_info.get('checkout', 'N/A')}
Number of Guests: {booking_info.get('guests', 'N/A')}

Check-in Time: 2:00 PM
Check-out Time: 12:00 NN

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PAYMENT INSTRUCTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

To secure your reservation, please remit 50% deposit within 24 hours.

Payment Options:

GCash: 0917-123-4567
Maya: 0917-123-4567

Bank Transfer:
BDO Account: 1234-5678-9012
Account Name: Paradise Resort Inc.

After payment, kindly send proof of payment (screenshot) to this chat or to our email: reservations@paradiseresort.com

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CHECK-IN REQUIREMENTS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please bring:
- Valid government-issued ID
- This confirmation number
- Proof of payment
- Vaccination card (if required by local government)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
NEED ASSISTANCE?
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Phone: 0917-123-4567
Landline: (046) 123-4567
Email: reservations@paradiseresort.com

We look forward to welcoming you at Paradise Resort.

Best regards,
Paradise Resort Reservations Team
"""
    return message.strip()

def payment_received_message(booking_info, confirmation_number, amount_paid):
    """Professional payment confirmation"""
    message = f"""PAYMENT CONFIRMATION

Dear {booking_info.get('name', 'Valued Guest')},

We acknowledge receipt of your payment. Your reservation is now confirmed.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PAYMENT DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Confirmation Number: {confirmation_number}
Amount Paid: {amount_paid:,.2f} pesos
Payment Date: {datetime.now().strftime('%B %d, %Y')}
Status: CONFIRMED

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESERVATION SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Check-in: {booking_info.get('checkin', 'N/A')}
Check-out: {booking_info.get('checkout', 'N/A')}
Number of Guests: {booking_info.get('guests', 'N/A')}

Your reservation is now confirmed and guaranteed.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IMPORTANT REMINDERS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Check-in Time: 2:00 PM onwards
Check-out Time: 12:00 NN

Please bring:
- Valid government-issued ID
- Remaining balance (if applicable)
- This confirmation for reference

Cancellation Policy:
- Free cancellation up to 7 days before check-in
- Cancellations within 3-7 days: 50% refund
- Less than 3 days: No refund

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CONTACT INFORMATION
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Paradise Resort
123 Main Highway, Tagaytay City

Phone: 0917-123-4567
Email: reservations@paradiseresort.com

We look forward to serving you.

Best regards,
Paradise Resort Reservations Team
"""
    return message.strip()

def reminder_message_24h(booking_info, confirmation_number):
    """Professional 24-hour check-in reminder"""
    message = f"""CHECK-IN REMINDER

Dear {booking_info.get('name', 'Valued Guest')},

This is a friendly reminder that your check-in is scheduled for tomorrow.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RESERVATION DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Confirmation Number: {confirmation_number}
Check-in Date: {booking_info.get('checkin', 'N/A')}
Check-in Time: 2:00 PM
Number of Guests: {booking_info.get('guests', 'N/A')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PRE-ARRIVAL CHECKLIST
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Please ensure you have:
□ Valid government-issued ID
□ Confirmation number: {confirmation_number}
□ Balance payment (if applicable)
□ Personal items and toiletries
□ Vaccination card (if required)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DIRECTIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Paradise Resort
123 Main Highway, Tagaytay City
Near Olivarez Plaza

For directions or assistance:
Phone: 0917-123-4567

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

We look forward to welcoming you tomorrow.

Safe travels,
Paradise Resort Team
"""
    return message.strip()

def thank_you_message(booking_info):
    """Professional thank you message after checkout"""
    message = f"""THANK YOU FOR YOUR STAY

Dear {booking_info.get('name', 'Valued Guest')},

Thank you for choosing Paradise Resort. We hope you had a pleasant and memorable stay with us.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SHARE YOUR EXPERIENCE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Your feedback is valuable to us. Please consider leaving a review:

Facebook: facebook.com/ParadiseResortTagaytay
Google Reviews: [Review Link]
TripAdvisor: [Review Link]

Your comments help us improve our services and assist other travelers.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
RETURNING GUEST BENEFITS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

As a valued returning guest, you are entitled to:

- 10% discount on your next stay
- Priority room selection
- Early check-in privilege (subject to availability)

Use promo code: WELCOMEBACK
Valid for 6 months from today

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
STAY CONNECTED
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

For future reservations:
Phone: 0917-123-4567
Email: reservations@paradiseresort.com
Website: www.paradiseresort.com

Follow us on social media for exclusive offers and updates.

We look forward to welcoming you back.

Best regards,
Paradise Resort Management
"""
    return message.strip()

def cancellation_confirmation_message(booking_info, confirmation_number, refund_amount=None):
    """Professional cancellation confirmation"""
    
    refund_text = f"""
REFUND DETAILS
Amount: {refund_amount:,.2f} pesos
Processing Time: 7-14 business days
Method: Original payment method""" if refund_amount else ""
    
    message = f"""CANCELLATION CONFIRMATION

Dear {booking_info.get('name', 'Valued Guest')},

This confirms the cancellation of your reservation as requested.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
CANCELLATION DETAILS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Confirmation Number: {confirmation_number}
Original Check-in: {booking_info.get('checkin', 'N/A')}
Cancellation Date: {datetime.now().strftime('%B %d, %Y %I:%M %p')}
{refund_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

We regret that your plans have changed. We hope to have the opportunity to serve you in the future.

If you have any questions regarding your cancellation or refund, please contact us:

Phone: 0917-123-4567
Email: reservations@paradiseresort.com

Thank you for considering Paradise Resort.

Best regards,
Paradise Resort Reservations Team
"""
    return message.strip()
