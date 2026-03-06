
from flask import Flask, request
import requests
import os
from dotenv import load_dotenv
import re

# Import database functions
from database import (
    save_customer, 
    save_conversation, 
    save_booking_inquiry, 
    update_lead_score,
    get_customer,
    Session,
    BookingInquiry
)

# Import message templates
from templates import (
    generate_confirmation_number,
    booking_confirmation_message,
    payment_received_message
)


load_dotenv()

app = Flask(__name__)

PAGE_ACCESS_TOKEN = os.getenv('PAGE_ACCESS_TOKEN')
VERIFY_TOKEN = os.getenv('VERIFY_TOKEN', 'my_verify_token_123')

print(f"Starting professional chatbot... Verify Token: {VERIFY_TOKEN}")

# ===== WEBHOOK VERIFICATION =====
@app.route('/webhook', methods=['GET'])
def verify_webhook():
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode == 'subscribe' and token == VERIFY_TOKEN:
        print('WEBHOOK VERIFIED')
        return challenge, 200
    return 'Forbidden', 403

# ===== WEBHOOK RECEIVER =====
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()
    
    if data.get('object') == 'page':
        for entry in data['entry']:
            webhook_event = entry['messaging'][0]
            sender_id = webhook_event['sender']['id']
            
            if webhook_event.get('message'):
                handle_message(sender_id, webhook_event['message'])
            elif webhook_event.get('postback'):
                handle_postback(sender_id, webhook_event['postback'])
    
    return 'EVENT_RECEIVED', 200

# ===== MESSAGE HANDLERS =====
def handle_message(sender_id, message):
    user_message = message.get('text', '').lower()
    print(f"Message from {sender_id}: {user_message}")
    
    save_customer(sender_id)
    
    if message.get('quick_reply'):
        payload = message['quick_reply']['payload']
        user_message = payload
    
    response_text = get_and_send_response(sender_id, user_message)
    
    if response_text:
        save_conversation(sender_id, user_message, response_text)

def handle_postback(sender_id, postback):
    payload = postback.get('payload')
    print(f"Button clicked: {payload}")
    get_and_send_response(sender_id, payload)

# ===== TEXT PROCESSING =====
def normalize_text(text):
    text = text.lower()
    text = ' '.join(text.split())
    # Remove common punctuation but keep important ones
    text = re.sub(r'[?!.,;]', '', text)
    return text

def contains_any(text, keywords):
    text = normalize_text(text)
    return any(keyword in text for keyword in keywords)

def contains_all(text, keywords):
    text = normalize_text(text)
    return all(keyword in text for keyword in keywords)

# ===== MAIN RESPONSE LOGIC =====
def get_and_send_response(sender_id, user_message):
    """Professional response system with comprehensive FAQ coverage"""
    msg = normalize_text(user_message)
    
    # ===== CHECK FOR PAYMENT PROOF =====
    if detect_payment_proof(user_message, sender_id):
        if handle_payment_confirmation(sender_id, user_message):
            return "Payment confirmation sent"
    
    # ===== GREETINGS =====
    if contains_any(msg, ['hi', 'hello', 'hey', 'kumusta', 'good morning', 'good afternoon', 'good evening', 'magandang', 'start', 'get started']):
        quick_replies = [
            {"title": "Room Rates", "payload": "rates"},
            {"title": "Current Promos", "payload": "promo"},
            {"title": "Check Availability", "payload": "available"},
            {"title": "Book Now", "payload": "book"}
        ]
        
        text = """Good day! Welcome to Paradise Resort.

How may I assist you today? I can help you with:
- Room rates and packages
- Availability and reservations
- Promotions and discounts
- Hotel amenities and policies
- Booking inquiries

Please feel free to ask your questions."""
        
        send_quick_replies(sender_id, text, quick_replies)
        return text
    
    # ===== PRICING & RATES (Comprehensive) =====
    elif contains_any(msg, ['hm', 'how much', 'magkano', 'price', 'rates', 'rate', 'pa-send ng rates', 'price list', 'room rates']):
        update_lead_score(sender_id, 'asked_rates')
        
        # Check for specific room types
        if contains_any(msg, ['standard', 'standard room']):
            text = """STANDARD ROOM RATES:

Weekday (Sunday - Thursday):
2,000 pesos per night

Weekend (Friday - Saturday):
2,500 pesos per night

Inclusions:
- Good for 2 guests
- Complimentary breakfast for 2
- Free Wi-Fi access
- Free parking

Room amenities: Air-conditioning, cable TV, hot & cold shower, mini-refrigerator, complimentary toiletries.

All rates are nett prices (no additional charges).

Would you like information on other room types or need to check availability?"""
        
        elif contains_any(msg, ['deluxe', 'deluxe room']):
            text = """DELUXE ROOM RATES:

Weekday (Sunday - Thursday):
2,800 pesos per night

Weekend (Friday - Saturday):
3,500 pesos per night

Inclusions:
- Good for 2 guests
- Complimentary breakfast for 2
- Free Wi-Fi access
- Free parking
- Lake/garden view

Room amenities: Air-conditioning, Smart TV with cable, hot & cold shower, mini-refrigerator, electric kettle, hairdryer, safe deposit box, complimentary toiletries.

All rates are nett prices (no additional charges).

Would you like to proceed with a reservation?"""
        
        elif contains_any(msg, ['family', 'suite', 'family room', 'family suite']):
            text = """FAMILY SUITE RATES:

Weekday (Sunday - Thursday):
4,000 pesos per night

Weekend (Friday - Saturday):
5,000 pesos per night

Inclusions:
- Good for up to 4 guests
- Complimentary breakfast for 4
- Free Wi-Fi access
- Free parking
- Spacious living area

Room amenities: Air-conditioning, Smart TV with cable, hot & cold shower, mini-refrigerator, electric kettle, hairdryer, iron & ironing board, safe deposit box, complimentary toiletries.

All rates are nett prices (no additional charges).

Would you like to check availability for specific dates?"""
        
        elif contains_any(msg, ['2 night', 'two night', 'dalawang gabi', '2 nights']):
            text = """TWO NIGHTS STAY RATES:

Weekday Package (Sunday - Thursday):
Standard Room: 4,000 pesos (2,000 per night)
Deluxe Room: 5,600 pesos (2,800 per night)
Family Suite: 8,000 pesos (4,000 per night)

Weekend Package (Friday - Saturday):
Standard Room: 5,000 pesos (2,500 per night)
Deluxe Room: 7,000 pesos (3,500 per night)
Family Suite: 10,000 pesos (5,000 per night)

All packages include:
- Breakfast for applicable number of guests
- Free Wi-Fi and parking
- Full access to hotel facilities

Rates quoted are final nett prices with no additional charges.

May I assist you with checking availability or making a reservation?"""
        
        elif contains_any(msg, ['weekday', 'monday', 'tuesday', 'wednesday', 'thursday', 'sun-thu']):
            text = """WEEKDAY RATES (Sunday - Thursday):

Standard Room: 2,000 pesos per night
Deluxe Room: 2,800 pesos per night
Family Suite: 4,000 pesos per night

All rates include:
- Breakfast for 2 guests (4 for Family Suite)
- Free Wi-Fi and parking
- Access to all facilities

Rates are nett prices (all-inclusive, no hidden charges).

Check-in time: 2:00 PM
Check-out time: 12:00 NN

Would you like to make a reservation?"""
        
        elif contains_any(msg, ['weekend', 'friday', 'saturday', 'fri-sat']):
            text = """WEEKEND RATES (Friday - Saturday):

Standard Room: 2,500 pesos per night
Deluxe Room: 3,500 pesos per night
Family Suite: 5,000 pesos per night

All rates include:
- Breakfast for 2 guests (4 for Family Suite)
- Free Wi-Fi and parking
- Access to all facilities

Rates are nett prices (all-inclusive, no hidden charges).

Check-in time: 2:00 PM
Check-out time: 12:00 NN

May I help you check availability for your preferred dates?"""
        
        else:
            # General pricing
            text = """ROOM RATES:

WEEKDAY RATES (Sunday - Thursday):
Standard Room: 2,000 pesos
Deluxe Room: 2,800 pesos
Family Suite: 4,000 pesos

WEEKEND RATES (Friday - Saturday):
Standard Room: 2,500 pesos
Deluxe Room: 3,500 pesos
Family Suite: 5,000 pesos

All rates are nett prices (no additional charges).
Rates include breakfast and free Wi-Fi/parking.

For more information, you may inquire about:
- Current promotions
- Senior citizen/PWD discounts
- Group bookings
- Long-term stay rates

How may I further assist you?"""
        
        quick_replies = [
            {"title": "See Promos", "payload": "promo"},
            {"title": "SC/PWD Discount", "payload": "senior"},
            {"title": "Check Availability", "payload": "available"},
            {"title": "Book Now", "payload": "book"}
        ]
        send_quick_replies(sender_id, text, quick_replies)
        return text
    
    # ===== NETT PRICE / PLUS PLUS =====
    elif contains_any(msg, ['nett', 'all-in', 'all in', 'plus plus', '++', 'hidden', 'additional charge', 'vat', 'service charge']):
        text = """PRICING STRUCTURE:

All our quoted room rates are NETT PRICES.

This means:
- No service charge
- No VAT to be added
- No hidden fees
- No "plus plus" (++) charges

What you see is what you pay.

Additional charges apply only for:
- Extra person beyond room capacity (500 pesos)
- Early check-in fee (300-500 pesos, subject to availability)
- Late check-out fee (300-500 pesos, subject to availability)
- Incidental damages (if applicable)

All room rates already include applicable taxes and service charges.

Would you like to know more about our room rates or policies?"""
        
        quick_replies = [
            {"title": "View Rates", "payload": "rates"},
            {"title": "Extra Person Policy", "payload": "extra person"},
            {"title": "Check-in Times", "payload": "check-in"}
        ]
        send_quick_replies(sender_id, text, quick_replies)
        return text
    
    # ===== PROMOTIONS =====
    elif contains_any(msg, ['promo', 'promotion', 'discount', 'sale', 'offer', 'deal', 'package']):
        text = """CURRENT PROMOTIONS:

MIDWEEK SPECIAL (Monday - Wednesday)
- Save 20% on room rates
- Standard Room: 1,600 pesos (Regular: 2,000)
- Book 3 nights, get the 4th night free

WEEKEND GETAWAY PACKAGE
- Friday to Saturday stay
- 4,500 pesos for 2 nights
- Includes breakfast for 2

BIRTHDAY MONTH PROMO
- 15% discount with valid ID
- Complimentary birthday cake
- Must present ID showing birth month

All promotions valid until March 31, 2026.
Senior citizen and PWD discounts can be applied on top of promotional rates.

Terms and conditions apply. Advance reservation required.

Would you like to make a booking or inquire about specific dates?"""
        
        quick_replies = [
            {"title": "View Regular Rates", "payload": "rates"},
            {"title": "Senior Discount", "payload": "senior"},
            {"title": "Check Availability", "payload": "available"},
            {"title": "Book Now", "payload": "book"}
        ]
        send_quick_replies(sender_id, text, quick_replies)
        return text
    
    # ===== AVAILABILITY =====
    elif contains_any(msg, ['available', 'avail', 'vacancy', 'may room', 'open', 'fully book', 'meron pa']):
        update_lead_score(sender_id, 'asked_availability')
        
        text = """ROOM AVAILABILITY INQUIRY:

To check room availability, please provide the following information:

1. Check-in date (example: March 15, 2026)
2. Check-out date (example: March 17, 2026)
3. Number of guests
4. Room type preference (if any)

You may send your details in this format:
"March 15-17, 4 guests, Deluxe Room"

Alternatively, you may contact us directly:
Phone: 0917-123-4567
Landline: (046) 123-4567

We will confirm availability within a few minutes.

How would you like to proceed?"""
        
        buttons = [
            {"title": "Call Us", "payload": "contact"},
            {"title": "View Rates", "payload": "rates"},
            {"title": "See Promos", "payload": "promo"}
        ]
        send_buttons(sender_id, text, buttons)
        return text
    
    # ===== SENIOR CITIZEN & PWD DISCOUNT =====
    elif contains_any(msg, ['senior', 'pwd', 'sc', 'senior citizen', 'disability', 'elderly', 'osca']):
        
        if contains_any(msg, ['compute', 'computation', 'calculate', 'paano', 'math', 'how to']):
            text = """SENIOR CITIZEN / PWD DISCOUNT COMPUTATION:

Discount Structure:
- 20% discount on room rate only
- VAT-exempt on the discounted portion
- Does not apply to food, beverages, or other services

Sample Computation:

For a weekend room rate of 2,500 pesos:

Step 1: Apply 20% discount
2,500 pesos less 20% = 2,000 pesos

Step 2: This is your final room rate
Amount to pay: 2,000 pesos

Important Notes:
- Discount applies to one (1) senior citizen or PWD per room
- Can be combined with promotional rates
- Original SC/PWD ID must be presented at check-in
- Discount applies only to room accommodation, not to food or spa services

For mixed groups (seniors and regular guests), the discount is pro-rated based on the number of senior citizens.

Would you like a specific computation for your group?"""
        
        elif contains_any(msg, ['id', 'requirements', 'requirement', 'need', 'kailangan', 'accepted', 'valid']):
            text = """SENIOR CITIZEN / PWD DISCOUNT REQUIREMENTS:

Accepted Identification:
- Original Senior Citizen ID
- Original PWD ID
- OSCA (Office of Senior Citizens Affairs) ID
- Government-issued SC/PWD card

NOT Accepted:
- Photocopies or scanned copies
- Digital or electronic copies
- Expired identification cards

Requirements:
- Discount holder must be present during check-in
- Original ID must be shown
- One discount per room booking
- Authorization letter if senior/PWD will not be present (with valid ID copy)

The discount applies only to the room rate and not to food, beverages, or other hotel services.

May I assist you with a booking inquiry?"""
        
        elif contains_any(msg, ['promo', 'promotion', 'double', 'combine', 'top', 'additional']):
            text = """COMBINING SENIOR/PWD DISCOUNT WITH PROMOTIONS:

Yes, senior citizen and PWD discounts can be combined with our promotional rates.

Example Computation:

Regular Weekend Rate: 2,500 pesos
Promotional Rate (20% off): 2,000 pesos
Less SC/PWD Discount (20%): -400 pesos
Final Rate: 1,600 pesos

This represents a total savings of 900 pesos (36% off regular rate).

Requirements:
- Valid and original SC/PWD ID
- Must mention the promo code at time of booking
- Subject to room availability
- Advance reservation recommended

To maximize your savings:
1. Book during promotional periods
2. Present valid SC/PWD ID at check-in
3. Reserve in advance to secure availability

Would you like to make a reservation?"""
        
        else:
            text = """SENIOR CITIZEN & PWD DISCOUNT POLICY:

Discount: 20% off on room rate

Eligibility:
- Filipino senior citizens (60 years and above)
- Persons with disability with valid PWD ID

Requirements:
- Original and valid SC/PWD ID
- ID must be presented upon check-in
- Discount holder must be present

Discount Application:
- Applies to room rate only
- Does not cover food, beverages, or spa services
- One discount per room
- Can be combined with promotional rates

Sample Rates with Discount:

Weekday:
Standard: 1,600 pesos (from 2,000)
Deluxe: 2,240 pesos (from 2,800)
Suite: 3,200 pesos (from 4,000)

Weekend:
Standard: 2,000 pesos (from 2,500)
Deluxe: 2,800 pesos (from 3,500)
Suite: 4,000 pesos (from 5,000)

May I help you with a reservation?"""
        
        quick_replies = [
            {"title": "View Regular Rates", "payload": "rates"},
            {"title": "Check Availability", "payload": "available"},
            {"title": "Book Now", "payload": "book"}
        ]
        send_quick_replies(sender_id, text, quick_replies)
        return text
    
    # ===== CHILDREN & EXTRA PERSON =====
    elif contains_any(msg, ['kid', 'child', 'bata', 'baby', 'infant', 'toddler', 'free', 'age', 'extra person', 'additional', 'extra pax', 'extra head']):
        
        if contains_any(msg, ['breakfast', 'meal', 'food']):
            text = """CHILDREN'S BREAKFAST POLICY:

Complimentary Breakfast:
- Children 5 years and below: FREE
- Must share with parents' meal

Charged Breakfast:
- Children 6-12 years old: 200 pesos
- 13 years and above: 350 pesos (regular adult rate)

Extra Person Package (500 pesos):
- Includes breakfast
- Includes bedding and amenities

Breakfast Service Hours: 6:30 AM - 10:00 AM

Menu Options:
- Filipino breakfast set
- Continental breakfast
- Children's meal (available for kids)

All children staying in the room must be declared at check-in.

May I assist you with anything else?"""
        
        elif contains_any(msg, ['extra', 'additional', 'charge', 'fee']):
            text = """EXTRA PERSON POLICY:

Room rates are based on 2 adults per room.

Extra Person Charges:
- Additional adult or child (6 years +): 500 pesos per night
- Includes breakfast and bedding

Free of Charge:
- Children 5 years and below
- Must share bed with parents
- Maximum 1 free child per room

Maximum Occupancy per Room Type:
- Standard Room: 3 persons (2 adults + 1 child)
- Deluxe Room: 4 persons
- Family Suite: 6 persons

Extra Bed:
- Available upon request: 500 pesos
- Includes breakfast
- Subject to availability

All extra persons must be declared during booking or upon check-in.

Would you like to make a reservation?"""
        
        else:
            text = """CHILDREN'S POLICY:

Free Accommodation:
- Children 0-5 years old stay free
- Must share existing bedding with parents
- Includes complimentary breakfast
- Maximum 1 free child per room

Charged Accommodation:
- Children 6-12 years: 300 pesos per night
- 13 years and above: 500 pesos (extra person rate)
- Includes breakfast

Extra Bed Option:
- Available for 500 pesos per night
- Includes breakfast and linens

Age Determination:
- Based on age at time of check-in
- Valid ID may be required

Maximum Children per Room:
- Standard Room: 2 children
- Deluxe Room: 3 children
- Family Suite: 4 children

We are a family-friendly establishment and welcome guests of all ages.

How may I further assist you?"""
        
        quick_replies = [
            {"title": "View Room Rates", "payload": "rates"},
            {"title": "Check Availability", "payload": "available"},
            {"title": "Book Now", "payload": "book"}
        ]
        send_quick_replies(sender_id, text, quick_replies)
        return text
    
    # ===== AMENITIES & FACILITIES =====
    elif contains_any(msg, ['amenities', 'facilities', 'feature', 'included', 'wifi', 'pool', 'parking', 'gym']):
        
        if contains_any(msg, ['wifi', 'wi-fi', 'internet', 'connection', 'work from home', 'wfh']):
            text = """WI-FI INTERNET SERVICE:

Connection Details:
- Complimentary high-speed Wi-Fi
- 100 Mbps fiber connection
- Available in all rooms and common areas
- 24/7 stable connection

Suitable For:
- Video streaming (Netflix, YouTube)
- Video conferencing (Zoom, Teams, Google Meet)
- Work from home arrangements
- Online gaming
- General browsing

Technical Details:
- Separate network per room for security
- Password provided at check-in
- Technical support available 24/7

Our Wi-Fi is suitable for both leisure and business travelers.

May I help you with a reservation?"""
        
        elif contains_any(msg, ['pool', 'swim', 'swimming']):
            text = """SWIMMING POOL FACILITIES:

Pool Hours: 6:00 AM - 10:00 PM daily

Features:
- Main swimming pool (adults)
- Kiddie pool section
- Heated during cooler months
- Poolside loungers and umbrellas
- Pool towels provided

Pool Rules:
- Proper swimming attire required
- Children must be supervised by adults
- No diving
- No food or drinks in pool area
- Shower before entering pool

Pool Bar:
- Operating hours: 10:00 AM - 8:00 PM
- Refreshments and light meals available

All hotel guests have complimentary access to pool facilities.

Would you like to know more about our other amenities?"""
        
        elif contains_any(msg, ['parking', 'park', 'car']):
            text = """PARKING FACILITIES:

Parking Details:
- Complimentary for all hotel guests
- Covered parking slots available
- 24/7 security and CCTV monitoring
- One parking slot per room

Vehicle Types Accommodated:
- Cars and SUVs
- Vans
- Motorcycles (complimentary)

Additional Vehicles:
- 100 pesos per day for 2nd vehicle

Security Measures:
- 24-hour security personnel
- CCTV surveillance
- Well-lit parking area
- Secure access

Parking is on a first-come, first-served basis. We recommend early check-in during peak seasons to secure a slot.

May I assist you with anything else?"""
        
        else:
            text = """HOTEL AMENITIES & FACILITIES:

Room Amenities (All Rooms):
- Air-conditioning
- Cable television (Smart TV in Deluxe/Suite)
- Hot and cold shower
- Mini-refrigerator
- Complimentary toiletries
- Fresh towels and linens
- Hairdryer
- Safe deposit box

Deluxe & Suite Additional Features:
- Electric kettle
- Coffee/tea making facilities
- Iron and ironing board
- Bathrobe and slippers

Hotel Facilities:
- Swimming pool with kiddie section
- Restaurant and dining area
- Function hall for events
- Free parking
- Garden and outdoor seating
- 24-hour front desk
- 24-hour security with CCTV

Complimentary Services:
- Wi-Fi internet (100 Mbps)
- Breakfast (per room inclusion)
- Parking (one vehicle per room)
- Use of pool and garden areas

How may I assist you further?"""
        
        quick_replies = [
            {"title": "Room Rates", "payload": "rates"},
            {"title": "Check Availability", "payload": "available"},
            {"title": "Book Now", "payload": "book"}
        ]
        send_quick_replies(sender_id, text, quick_replies)
        return text
    
    # ===== VIEWS (Taal, Lake, Garden, etc.) =====
    elif contains_any(msg, ['view', 'taal', 'lake', 'garden', 'mountain', 'scenery']):
        text = """ROOM VIEWS AVAILABLE:

LAKE VIEW (Taal Lake):
Deluxe Lake View Room: 3,500 pesos (weekday) / 4,500 pesos (weekend)
Premium Suite: 5,500 pesos (weekday) / 7,000 pesos (weekend)
- Private balcony with seating
- Unobstructed view of Taal Lake
- Best for sunrise viewing

GARDEN VIEW:
Standard Garden View: 2,000 pesos (weekday) / 2,500 pesos (weekend)
- Peaceful garden setting
- Direct pool access
- Ground floor convenience

MOUNTAIN VIEW:
Deluxe Mountain View: 3,200 pesos (weekday) / 4,200 pesos (weekend)
- Tagaytay ridge and mountains
- Higher floor rooms
- Balcony with outdoor chairs

All rates include breakfast and standard amenities.

Lake view rooms are limited and subject to high demand. Advance booking is recommended.

Would you like to reserve a specific view?"""
        
        quick_replies = [
            {"title": "Book Lake View", "payload": "book lake view"},
            {"title": "View All Rates", "payload": "rates"},
            {"title": "Check Availability", "payload": "available"}
        ]
        send_quick_replies(sender_id, text, quick_replies)
        return text
    
    # ===== FOOD & CORKAGE =====
    elif contains_any(msg, ['food', 'outside food', 'corkage', 'bring', 'magdala', 'deliver', 'delivery', 'grilling', 'cook']):
        
        if contains_any(msg, ['liquor', 'wine', 'beer', 'alcohol', 'drinks', 'alak']):
            text = """LIQUOR AND BEVERAGE CORKAGE POLICY:

Outside Liquor: ALLOWED

Corkage Fee: 200 pesos per bottle

Includes:
- Ice bucket
- Drinking glasses
- Bottle opener/corkscrew

Corkage-Free Items:
- Soft drinks and bottled water
- Non-alcoholic beverages

Hotel Bar Available:
- San Miguel Beer: 80 pesos
- Red Horse: 90 pesos
- Wine selection: 800-2,000 pesos
- Cocktails and mixed drinks available

House Rules:
- Drink responsibly
- No drinking in pool area
- Quiet hours: 10:00 PM - 6:00 AM
- Intoxicated guests may be denied entry to common areas

May I assist you with anything else?"""
        
        else:
            text = """OUTSIDE FOOD POLICY:

Outside Food: ALLOWED with corkage fee

Corkage Charges:
- Cooked food: 100 pesos per person
- Beverages (non-alcoholic): FREE
- Alcoholic beverages: 200 pesos per bottle
- Birthday cakes: FREE (complimentary)

You May Also:
- Order food delivery (GrabFood, FoodPanda, etc.)
- Use grilling area: 800 pesos (includes charcoal)
- Request use of kitchen: 500 pesos (for simple heating only)

In-House Restaurant:
- Filipino and international cuisine
- Breakfast buffet included in room rate
- Room service available
- Operating hours: 6:00 AM - 10:00 PM

For events and large groups, customized catering packages are available.

Would you like to know more about our dining options?"""
        
        quick_replies = [
            {"title": "Restaurant Menu", "payload": "restaurant"},
            {"title": "Event Catering", "payload": "events"},
            {"title": "Back to Main", "payload": "hi"}
        ]
        send_quick_replies(sender_id, text, quick_replies)
        return text
    
    # ===== PETS =====
    elif contains_any(msg, ['pet', 'dog', 'cat', 'aso', 'pusa', 'alaga', 'animal']):
        text = """PET POLICY:

Pet-Friendly Accommodation: YES, pets are allowed

Pet Fee: 500 pesos per pet, per night

Conditions:
- Maximum 2 pets per room
- Small to medium-sized pets only
- Must be leashed in common areas
- Not allowed in pool, restaurant, or function areas
- Pet must be house-trained

Required Documents:
- Updated anti-rabies vaccination certificate
- Health certificate from veterinarian (within 30 days)

Pet Amenities:
- Pet mat provided
- Designated walking/relief area
- Water bowls available upon request

Pet Owner Responsibilities:
- Clean up after pets
- Control noise (barking, etc.)
- Supervise pets at all times
- Any damages will be charged to guest

Penalties:
- Undeclared pets: 1,000 peso fine
- Damages caused by pets: Actual cost

We welcome your furry companions with advance notice.

Would you like to make a reservation?"""
        
        quick_replies = [
            {"title": "View Room Rates", "payload": "rates"},
            {"title": "Check Availability", "payload": "available"},
            {"title": "Book Now", "payload": "book"}
        ]
        send_quick_replies(sender_id, text, quick_replies)
        return text
    
    # ===== CHECK-IN / CHECK-OUT =====
    elif contains_any(msg, ['check-in', 'check in', 'check-out', 'check out', 'time', 'early', 'late', 'anong oras']):
        
        if contains_any(msg, ['early', 'maaga', 'before 2']):
            text = """EARLY CHECK-IN POLICY:

Standard Check-in Time: 2:00 PM

Early Check-in Options:

1:00 PM - 2:00 PM
Fee: FREE (subject to room availability)

12:00 NN - 1:00 PM
Fee: 300 pesos

11:00 AM - 12:00 NN
Fee: 400 pesos

9:00 AM or earlier
Fee: 500 pesos

Important Notes:
- Early check-in is NOT guaranteed
- Dependent on room availability and cleaning schedule
- Must be requested in advance
- Payment required at check-in

If room is not ready:
- Complimentary luggage storage available
- May use common areas and facilities
- Will notify you when room is ready

For guaranteed early access, we recommend arriving after 2:00 PM.

May I assist you with a booking?"""
        
        elif contains_any(msg, ['late', 'extend', 'after 12', 'huli']):
            text = """LATE CHECK-OUT POLICY:

Standard Check-out Time: 12:00 NN (noon)

Late Check-out Options:

12:00 NN - 1:00 PM
Fee: FREE (subject to availability)

1:00 PM - 2:00 PM
Fee: 300 pesos

2:00 PM - 3:00 PM
Fee: 400 pesos

3:00 PM - 5:00 PM
Fee: 500 pesos

5:00 PM and later
Fee: Full day rate applies

Important Notes:
- Late check-out must be requested at front desk
- Subject to room availability
- Payment due before 12:00 NN
- For stays beyond 5:00 PM, half-day or full-day rates apply

Complimentary Services:
- Luggage storage after check-out (FREE)
- Use of common areas until departure

How may I further assist you?"""
        
        else:
            text = """CHECK-IN & CHECK-OUT INFORMATION:

Standard Times:
Check-in: 2:00 PM
Check-out: 12:00 NN (noon)

Early Check-in:
Available from 9:00 AM onwards
Fee: 300-500 pesos (subject to availability)

Late Check-out:
Available until 5:00 PM
Fee: 300-500 pesos (subject to availability)

Check-in Requirements:
- Valid government-issued ID
- Booking confirmation or reference number
- Payment of balance (if not fully paid)
- Incidental deposit (1,000 pesos, refundable)

Complimentary Services:
- Luggage storage (before check-in/after check-out)
- Room ready notification
- Express check-out

For special timing requests, please inform us during booking or call in advance.

Would you like to make a reservation?"""
        
        quick_replies = [
            {"title": "View Room Rates", "payload": "rates"},
            {"title": "Check Availability", "payload": "available"},
            {"title": "Book Now", "payload": "book"}
        ]
        send_quick_replies(sender_id, text, quick_replies)
        return text
    
    # ===== PAYMENT METHODS =====
    elif contains_any(msg, ['payment', 'pay', 'gcash', 'maya', 'bank', 'transfer', 'cash', 'card', 'credit', 'bayad']):
        text = """PAYMENT METHODS ACCEPTED:

Electronic Payments:
- GCash (mobile number: 0917-123-4567)
- Maya / PayMaya
- Bank Transfer:
  BDO Account: 1234-5678-9012
  BPI Account: 9876-5432-1098
  Metrobank Account: 5555-6666-7777
  Account Name: Paradise Resort Inc.

Card Payments:
- Visa
- Mastercard
- American Express
- Debit cards

Cash Payment:
- Accepted at check-in
- Philippine Peso only

Payment Schedule:

Reservation:
- 50% deposit required to confirm booking
- Balance payable upon check-in

Incidental Deposit:
- 1,000 pesos (cash or card authorization)
- Refundable upon check-out if no damages

Payment Reminders:
- Send proof of payment (screenshot) after transfer
- Include booking reference number
- Official receipt provided upon request
- No-show policy: Deposit is non-refundable

For bank transfers, please allow 1-2 banking days for confirmation.

How may I assist you with your booking?"""
        
        quick_replies = [
            {"title": "Make a Reservation", "payload": "book"},
            {"title": "View Rates", "payload": "rates"},
            {"title": "Contact Us", "payload": "contact"}
        ]
        send_quick_replies(sender_id, text, quick_replies)
        return text
    
    # ===== SMOKING POLICY =====
    elif contains_any(msg, ['smoke', 'smoking', 'vape', 'vaping', 'cigarette', 'yosi']):
        text = """SMOKING POLICY:

Non-Smoking Property: All indoor areas are smoke-free

Designated Smoking Areas:
- Garden area (outdoor)
- Parking lot
- Balconies (selected rooms only)

Vaping / E-Cigarettes:
- Same policy as smoking
- Allowed only in designated outdoor areas

Strictly Prohibited:
- Smoking inside rooms
- Smoking in hallways, lobbies, or enclosed areas
- Smoking in pool area
- Smoking in restaurant

Penalty for Violation:
- 2,500 pesos cleaning and deodorizing fee
- Additional charges for extensive damage
- Possible eviction without refund

Detection Methods:
- Smoke detectors in all rooms
- Staff inspection
- Guest reports

We maintain a smoke-free environment for the comfort and health of all guests.

Thank you for your cooperation.

May I help you with anything else?"""
        
        quick_replies = [
            {"title": "Hotel Policies", "payload": "policies"},
            {"title": "Room Amenities", "payload": "amenities"},
            {"title": "Book Now", "payload": "book"}
        ]
        send_quick_replies(sender_id, text, quick_replies)
        return text
    
    # ===== EVENTS & FUNCTIONS =====
    elif contains_any(msg, ['event', 'wedding', 'debut', 'birthday', 'seminar', 'conference', 'function', 'venue', 'package', 'celebration']):
        text = """EVENTS & FUNCTIONS:

We host various events and celebrations:

Event Types:
- Weddings and receptions
- Debut (18th birthday celebration)
- Birthday parties
- Corporate events and seminars
- Team building activities
- Family reunions
- Anniversary celebrations

Function Hall:
Capacity: 50-150 persons (air-conditioned)
Garden Venue: Up to 200 persons

Package Rates (starting prices):

Small Events (50 pax): 25,000 pesos
Medium Events (100 pax): 45,000 pesos
Large Events (150+ pax): Custom quotation

Basic Package Includes:
- Venue rental (4 hours)
- Tables and chairs
- Sound system
- Basic lighting
- Air-conditioning (indoor venue)

Optional Add-ons:
- Catering services
- Event styling and decoration
- Photography and videography
- Entertainment
- Extended venue hours

For detailed proposals and customized packages:

Phone: 0917-123-4567
Email: events@paradiseresort.com

We require at least 30 days advance booking for events.

Would you like to schedule a consultation?"""
        
        buttons = [
            {"title": "Contact Events Team", "payload": "contact"},
            {"title": "View Packages", "payload": "event packages"},
            {"title": "Back to Main", "payload": "hi"}
        ]
        send_buttons(sender_id, text, buttons)
        return text
    
    # ===== LOCATION & DIRECTIONS =====
    elif contains_any(msg, ['location', 'address', 'where', 'saan', 'direction', 'paano', 'commute', 'how to get', 'papunta']):
        text = """LOCATION & DIRECTIONS:

Address:
Paradise Resort
123 Main Highway, Tagaytay City, Cavite
(Near Olivarez Plaza)

Landmark: 5 minutes from Picnic Grove

From Manila (via SLEX):
1. Take SLEX southbound
2. Exit at Sta. Rosa
3. Follow Tagaytay-Sta. Rosa Road
4. Travel time: Approximately 1.5 hours
5. Hotel is along the main highway

GPS Coordinates: [Available upon request]

Nearby Attractions:
- Sky Ranch: 15 minutes
- People's Park in the Sky: 10 minutes
- SM Tagaytay: 10 minutes
- Picnic Grove: 5 minutes

Public Transportation:
- Bus from EDSA/Cubao to Tagaytay
- Jeepney from Nasugbu Highway
- Tricycle from town proper

Private Transfer Options:
- Grab/taxi from Manila: Approx. 1,500-2,000 pesos
- Hotel shuttle service: 2,500 pesos (advance booking required)

Contact Numbers:
Phone: 0917-123-4567
Landline: (046) 123-4567

For real-time traffic updates or directions, please call us.

May I assist you with a reservation?"""
        
        quick_replies = [
            {"title": "Call for Directions", "payload": "contact"},
            {"title": "Book Shuttle Service", "payload": "shuttle"},
            {"title": "Make Reservation", "payload": "book"}
        ]
        send_quick_replies(sender_id, text, quick_replies)
        return text
    
    # ===== SHUTTLE / TRANSFER SERVICES =====
    elif contains_any(msg, ['shuttle', 'transfer', 'transport', 'naia', 'airport', 'pick up', 'drop off', 'hatid', 'sundo']):
        text = """SHUTTLE & TRANSFER SERVICES:

Airport Transfer (NAIA):

Manila Airport to Hotel:
- Private van (up to 6 passengers): 2,500 pesos
- Travel time: Approximately 2 hours
- Advance booking required (24 hours)

Hotel to Manila Airport:
- Private van (up to 6 passengers): 2,500 pesos
- Recommended departure: 3 hours before flight

Round Trip Package:
- Both ways: 4,500 pesos
- Valid for up to 7 days

Local Tours & Transfers:

Tagaytay City Tour: 1,500 pesos (4 hours)
Taal Volcano Tour: 2,000 pesos
Custom destinations: Rates upon inquiry

Service Includes:
- Door-to-door service
- Professional driver
- Air-conditioned vehicle
- Fuel and toll fees

Meet & Greet Service:
- Available at airport arrivals
- Driver with name signage
- Assistance with luggage

Booking Requirements:
- At least 24 hours advance notice
- Full passenger details
- Flight information (for airport transfers)

To book shuttle service:
Phone: 0917-123-4567
Email: transport@paradiseresort.com

How may I help you further?"""
        
        quick_replies = [
            {"title": "Book Transfer", "payload": "contact"},
            {"title": "View Room Rates", "payload": "rates"},
            {"title": "Make Reservation", "payload": "book"}
        ]
        send_quick_replies(sender_id, text, quick_replies)
        return text
    
    # ===== BOOKING / RESERVATION =====
    elif contains_any(msg, ['book', 'reserve', 'reservation', 'resv', 'pag-book', 'mag-reserve']):
        update_lead_score(sender_id, 'asked_booking')
        update_lead_score(sender_id, 'clicked_book')
        
        text = """RESERVATION PROCESS:

To make a reservation, please provide:

1. Guest name (as it appears on ID)
2. Contact number
3. Check-in date
4. Check-out date
5. Number of guests
6. Room type preference

Sample Format:
"Juan Dela Cruz
0917-1234567
Check-in: March 15, 2026
Check-out: March 17, 2026
4 guests, Deluxe Room"

Reservation Requirements:

Deposit: 50% of total room rate
Acceptable Payment: GCash, bank transfer, credit card
Balance: Payable upon check-in

You will receive:
- Booking confirmation number
- Payment instructions
- Official receipt (upon request)

For immediate assistance:
Phone: 0917-123-4567
Landline: (046) 123-4567
Email: reservations@paradiseresort.com

We will confirm your booking within 5 minutes upon receipt of deposit.

Please send your booking details to proceed."""
        
        buttons = [
            {"title": "View Room Rates", "payload": "rates"},
            {"title": "See Promotions", "payload": "promo"},
            {"title": "Call Us", "payload": "contact"}
        ]
        send_buttons(sender_id, text, buttons)
        return text
    
    # ===== CONTACT INFORMATION =====
    elif contains_any(msg, ['contact', 'number', 'phone', 'email', 'reach', 'call', 'text']):
        text = """CONTACT INFORMATION:

Paradise Resort
123 Main Highway, Tagaytay City

Reservations & Inquiries:
Mobile: 0917-123-4567
Landline: (046) 123-4567
Email: reservations@paradiseresort.com

Events & Functions:
Email: events@paradiseresort.com

General Inquiries:
Email: info@paradiseresort.com

Social Media:
Facebook: facebook.com/ParadiseResortTagaytay
Instagram: @paradiseresortph

Office Hours:
Daily: 8:00 AM - 8:00 PM

Front Desk (for guests):
24 hours, 7 days a week

For reservations, we recommend:
- Calling during office hours for immediate assistance
- Messaging via Facebook for quick responses
- Emailing for detailed inquiries

We typically respond within 30 minutes during office hours.

How else may I assist you?"""
        
        quick_replies = [
            {"title": "Make Reservation", "payload": "book"},
            {"title": "View Rates", "payload": "rates"},
            {"title": "Check Availability", "payload": "available"}
        ]
        send_quick_replies(sender_id, text, quick_replies)
        return text
    
    # ===== CANCELLATION POLICY =====
    elif contains_any(msg, ['cancel', 'refund', 'rebooking', 'change date', 'reschedule']):
        text = """CANCELLATION & REBOOKING POLICY:

Cancellation:

More than 7 days before check-in:
- Full refund of deposit
- No cancellation fee

3-7 days before check-in:
- 50% refund of deposit
- 50% cancellation fee

Less than 3 days before check-in:
- No refund
- Full deposit forfeited

No-show:
- No refund
- Reservation automatically cancelled

Rebooking / Rescheduling:

First time change (free):
- At least 7 days before check-in
- Subject to room availability
- No rebooking fee

Subsequent changes:
- 500 pesos rebooking fee per change
- At least 3 days before original check-in date

Force Majeure (typhoons, natural disasters):
- Full rebooking allowed
- No penalty or fees
- Subject to availability
- Valid for 1 year from original date

Process:
- Contact us via phone or email
- Provide booking reference number
- Specify reason for cancellation/change
- Refund processing: 7-14 business days

For cancellations or changes:
Phone: 0917-123-4567
Email: reservations@paradiseresort.com

How may I assist you further?"""
        
        quick_replies = [
            {"title": "Contact Us", "payload": "contact"},
            {"title": "View Policies", "payload": "policies"},
            {"title": "Book Now", "payload": "book"}
        ]
        send_quick_replies(sender_id, text, quick_replies)
        return text
    
    # ===== DETECT BOOKING INFORMATION =====
    elif len(user_message) > 30:
        booking_info = extract_booking_info(user_message)
        
        if booking_info:
            confirmation_number = generate_confirmation_number()
            
            booking = save_booking_inquiry(
                sender_id=sender_id,
                name=booking_info.get('name'),
                phone=booking_info.get('phone'),
                checkin=booking_info.get('checkin'),
                checkout=booking_info.get('checkout'),
                guests=booking_info.get('guests')
            )
            
            if booking:
                session = Session()
                try:
                    db_booking = session.query(BookingInquiry).filter_by(id=booking.id).first()
                    if db_booking:
                        db_booking.confirmation_number = confirmation_number
                        session.commit()
                finally:
                    session.close()
            
            if booking_info.get('name') or booking_info.get('phone'):
                save_customer(
                    sender_id=sender_id,
                    name=booking_info.get('name'),
                    phone=booking_info.get('phone')
                )
                update_lead_score(sender_id, 'provided_contact')
            
            confirmation_msg = booking_confirmation_message(booking_info, confirmation_number)
            send_message(sender_id, confirmation_msg)
            
            quick_replies = [
                {"title": "Payment Methods", "payload": "payment"},
                {"title": "Contact Us", "payload": "contact"}
            ]
            
            followup_text = "For payment instructions or questions, please select from the options below or contact us directly."
            send_quick_replies(sender_id, followup_text, quick_replies)
            
            return confirmation_msg
    
    # ===== THANK YOU =====
    elif contains_any(msg, ['thank', 'thanks', 'salamat', 'maraming salamat']):
        text = """You're welcome. We're glad to assist you.

Is there anything else you would like to know about our hotel, rates, or services?

Feel free to ask any questions."""
        
        quick_replies = [
            {"title": "Room Rates", "payload": "rates"},
            {"title": "Promotions", "payload": "promo"},
            {"title": "Make Reservation", "payload": "book"}
        ]
        send_quick_replies(sender_id, text, quick_replies)
        return text
    
    # ===== LEGITIMACY / VERIFICATION =====
    elif contains_any(msg, ['legit', 'scam', 'fake', 'totoo', 'real', 'verified', 'legitimate', 'authorized']):
        text = """BUSINESS VERIFICATION:

Paradise Resort is a legitimate and registered business.

Official Registrations:
- DTI Registration: 1234567890
- DOT Accreditation: TAG-2024-001
- Mayor's Permit: 2024-001-MP
- BIR Registration: 123-456-789-000

Business Address:
123 Main Highway, Tagaytay City, Cavite

Verification:
- Facebook: Verified business page (blue checkmark)
- Physical location: Can accommodate ocular visits
- Operating since: 2015

Contact Verification:
Official Numbers:
- Mobile: 0917-123-4567
- Landline: (046) 123-4567

Warning Signs of Scams:
- Requests for payment to personal accounts only
- Extremely low prices (too good to be true)
- Pressure to pay immediately
- No physical address or contact number
- Poor quality or watermarked photos

Our Commitment:
- Transparent pricing
- Official receipts provided
- Legitimate business operations
- Customer reviews available
- Proper documentation

You may verify our business through:
- Google Maps listing
- Facebook reviews
- TripAdvisor
- DOT accreditation list

Visit us at our physical location for peace of mind.

How may we further assist you?"""
        
        quick_replies = [
            {"title": "View Rates", "payload": "rates"},
            {"title": "Contact Us", "payload": "contact"},
            {"title": "Book Now", "payload": "book"}
        ]
        send_quick_replies(sender_id, text, quick_replies)
        return text
    
    # ===== DEFAULT RESPONSE =====
    else:
        text = """Thank you for your message.

I can assist you with information about:

RESERVATIONS & RATES
- Room rates and packages
- Current promotions
- Availability checking
- Booking process

POLICIES & INFORMATION
- Senior citizen and PWD discounts
- Children and extra person policies
- Check-in and check-out procedures
- Payment methods
- Cancellation policy

FACILITIES & SERVICES
- Hotel amenities
- Wi-Fi and connectivity
- Swimming pool
- Parking
- Restaurant and dining

SPECIAL REQUESTS
- Airport transfers
- Events and functions
- Pet accommodation
- Special occasions

Please type your question, or select from the options below."""
        
        quick_replies = [
            {"title": "Room Rates", "payload": "rates"},
            {"title": "Promotions", "payload": "promo"},
            {"title": "Check Availability", "payload": "available"},
            {"title": "Contact Information", "payload": "contact"}
        ]
        send_quick_replies(sender_id, text, quick_replies)
        return text

# ===== HELPER FUNCTIONS =====

def extract_booking_info(message):
    """Extract booking information from user message"""
    info = {}
    
    # Extract phone number
    phone_pattern = r'(\+?63|0)?\s?9\d{2}[\s-]?\d{3}[\s-]?\d{4}'
    phone_match = re.search(phone_pattern, message)
    if phone_match:
        info['phone'] = phone_match.group()
    
    # Extract dates
    month_pattern = r'(january|february|march|april|may|june|july|august|september|october|november|december)\s+\d{1,2}'
    dates = re.findall(month_pattern, message.lower())
    if len(dates) >= 1:
        info['checkin'] = dates[0]
    if len(dates) >= 2:
        info['checkout'] = dates[1]
    
    # Extract number of guests
    pax_pattern = r'(\d+)\s*(pax|person|guest|people|adults?|guests?)'
    pax_match = re.search(pax_pattern, message.lower())
    if pax_match:
        info['guests'] = int(pax_match.group(1))
    
    # Extract name (first line if it looks like a name)
    lines = message.split('\n')
    if len(lines) > 0:
        first_line = lines[0].strip()
        if 2 <= len(first_line.split()) <= 4 and not any(char.isdigit() for char in first_line):
            info['name'] = first_line
    
    if len(info) >= 2:
        return info
    return None

def detect_payment_proof(user_message, sender_id):
    """Detect if user is sending payment proof"""
    payment_keywords = ['paid', 'payment', 'sent', 'transfer', 'gcash', 'maya', 'deposit', 'bayad', 'nag', 'send']
    msg = normalize_text(user_message)
    return any(keyword in msg for keyword in payment_keywords)

def handle_payment_confirmation(sender_id, message):
    """Handle payment confirmation"""
    session = Session()
    try:
        booking = session.query(BookingInquiry)\
            .filter_by(sender_id=sender_id, status='pending')\
            .order_by(BookingInquiry.inquiry_date.desc())\
            .first()
        
        if booking:
            booking.status = 'confirmed'
            session.commit()
            
            booking_info = {
                'name': booking.name,
                'phone': booking.phone,
                'checkin': booking.checkin_date,
                'checkout': booking.checkout_date,
                'guests': booking.num_guests
            }
            
            amount_paid = 2500
            confirmation_msg = payment_received_message(
                booking_info, 
                booking.confirmation_number,
                amount_paid
            )
            
            send_message(sender_id, confirmation_msg)
            update_lead_score(sender_id, 'provided_contact')
            
            return True
    finally:
        session.close()
    
    return False

# ===== SEND FUNCTIONS =====

def send_message(sender_id, text):
    """Send plain text message"""
    url = f"https://graph.facebook.com/v18.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    
    data = {
        "recipient": {"id": sender_id},
        "message": {"text": text}
    }
    
    response = requests.post(url, params=params, json=data)
    
    if response.status_code == 200:
        print(f"Message sent to {sender_id}")
    else:
        print(f"Error: {response.status_code}")

def send_quick_replies(sender_id, text, quick_replies):
    """Send message with quick reply buttons"""
    url = f"https://graph.facebook.com/v18.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    
    formatted_replies = []
    for reply in quick_replies:
        formatted_replies.append({
            "content_type": "text",
            "title": reply["title"][:20],
            "payload": reply["payload"]
        })
    
    data = {
        "recipient": {"id": sender_id},
        "message": {
            "text": text,
            "quick_replies": formatted_replies
        }
    }
    
    response = requests.post(url, params=params, json=data)
    
    if response.status_code == 200:
        print(f"Quick replies sent")
    else:
        print(f"Error: {response.status_code}")

def send_buttons(sender_id, text, buttons):
    """Send message with button template"""
    url = f"https://graph.facebook.com/v18.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    
    formatted_buttons = []
    for button in buttons[:3]:
        formatted_buttons.append({
            "type": "postback",
            "title": button["title"][:20],
            "payload": button["payload"]
        })
    
    data = {
        "recipient": {"id": sender_id},
        "message": {
            "attachment": {
                "type": "template",
                "payload": {
                    "template_type": "button",
                    "text": text[:640],
                    "buttons": formatted_buttons
                }
            }
        }
    }
    
    response = requests.post(url, params=params, json=data)
    
    if response.status_code == 200:
        print(f"Buttons sent")
    else:
        print(f"Error: {response.status_code}")

@app.route('/', methods=['GET'])
def home():
    return "Professional Hotel Chatbot Running"

if __name__ == '__main__':
    if not PAGE_ACCESS_TOKEN:
        print("WARNING: PAGE_ACCESS_TOKEN not set!")
    
    print("Starting professional hotel chatbot...")
    app.run(host='0.0.0.0', port=3000, debug=True)
