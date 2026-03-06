"""
ADMIN DASHBOARD
===============
View and manage leads, bookings, and customers.

USAGE:
python admin_dashboard.py              # Show dashboard
python admin_dashboard.py export       # Export to CSV
"""
from database import get_all_customers, get_hot_leads, get_pending_bookings
from datetime import datetime
import csv

def show_dashboard():
    """Display admin dashboard"""
    print("=" * 60)
    print("🏨 PARADISE RESORT - ADMIN DASHBOARD")
    print("=" * 60)
    print()
    
    # HOT LEADS
    print("🔥 HOT LEADS (Score 50+)")
    print("-" * 60)
    hot_leads = get_hot_leads(min_score=50, limit=10)
    
    if hot_leads:
        for lead in hot_leads:
            print(f"Score: {lead.score} | ID: {lead.sender_id}")
            print(f"  - Asked rates: {lead.asked_about_rates}x")
            print(f"  - Asked availability: {lead.asked_about_availability}x")
            print(f"  - Clicked book: {lead.clicked_book_button}x")
            print()
    else:
        print("No hot leads yet.\n")
    
    # PENDING BOOKINGS
    print("📋 PENDING BOOKING INQUIRIES")
    print("-" * 60)
    bookings = get_pending_bookings()
    
    if bookings:
        for booking in bookings:
            print(f"#{booking.id} - {booking.name or 'No name'}")
            print(f"  📱 Phone: {booking.phone or 'Not provided'}")
            print(f"  📅 Dates: {booking.checkin_date} to {booking.checkout_date}")
            print(f"  👥 Guests: {booking.num_guests or 'Not specified'}")
            print()
    else:
        print("No pending bookings.\n")
    
    # RECENT CUSTOMERS
    print("👥 RECENT CUSTOMERS (Last 10)")
    print("-" * 60)
    customers = get_all_customers(limit=10)
    
    if customers:
        for customer in customers:
            print(f"{customer.name or 'Unknown'} ({customer.sender_id})")
            print(f"  📱 Phone: {customer.phone or 'Not provided'}")
            print(f"  💬 Messages: {customer.total_messages}")
            print(f"  📅 Last contact: {customer.last_message_date.strftime('%Y-%m-%d %H:%M')}")
            print()
    else:
        print("No customers yet.\n")

def export_leads_to_csv():
    """Export leads to CSV file"""
    customers = get_all_customers(limit=1000)
    
    filename = f"leads_export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Name', 'Phone', 'Email', 'Sender ID', 'Total Messages', 
                        'First Contact', 'Last Contact', 'Status'])
        
        for customer in customers:
            writer.writerow([
                customer.name or '',
                customer.phone or '',
                customer.email or '',
                customer.sender_id,
                customer.total_messages,
                customer.first_message_date.strftime('%Y-%m-%d %H:%M'),
                customer.last_message_date.strftime('%Y-%m-%d %H:%M'),
                customer.status
            ])
    
    print(f"✅ Exported {len(customers)} customers to {filename}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == 'export':
        export_leads_to_csv()
    else:
        show_dashboard()
