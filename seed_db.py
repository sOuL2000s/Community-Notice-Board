import sqlite3
from datetime import datetime, timedelta

DATABASE = 'community_notice_board.db'

def get_db_connection():
    """Establishes a database connection."""
    try:
        conn = sqlite3.connect(DATABASE)
        conn.row_factory = sqlite3.Row # Allows accessing columns by name
        print(f"DEBUG: Successfully opened database connection to {DATABASE}")
        return conn
    except sqlite3.Error as e:
        print(f"ERROR: Could not connect to database {DATABASE}. Error: {e}")
        return None # Explicitly return None if connection fails

def seed_data():
    """Populates the database with sample notices."""
    conn = get_db_connection()
    
    if conn is None: # Check if connection was successful
        print("ERROR: Database connection failed in seed_data(), cannot proceed with seeding.")
        return

    cursor = conn.cursor()

    # Optional: Clear existing notices for a fresh start.
    # Uncomment the next two lines if you want to wipe existing data before seeding.
    # cursor.execute("DELETE FROM notices")
    # conn.commit()
    # print("Cleared existing notices (if any).")

    now = datetime.now()

    # --- Awesome Notices for Your Portfolio ---
    notices_to_insert = [
        {
            'title': 'Grand Annual Community Festival!',
            'content': '🎉 Get ready for a spectacular day of fun, food, and festivities! Join us for live music, delicious local food trucks, artisan stalls, and exciting activities for all ages. Don\'t miss the biggest event of the year!',
            'category': 'event',
            'is_urgent': 0,
            'created_at': (now - timedelta(days=7)).isoformat(),
            'expires_at': (now + timedelta(days=15)).isoformat(), # Expires well after the event
            'event_date': (now + timedelta(days=10)).strftime('%Y-%m-%d'),
            'event_time': '10:00',
            'event_location': 'Central Town Square & Park',
            'is_active': 1
        },
        {
            'title': 'New Weekly Farmers Market Opening!',
            'content': '🌱 We\'re excited to announce the grand opening of our new weekly farmers market! Come support local growers and artisans, find fresh produce, homemade goods, and unique crafts. Every Saturday morning!',
            'category': 'event',
            'is_urgent': 0,
            'created_at': (now - timedelta(days=3)).isoformat(),
            'expires_at': None, # Ongoing market
            'event_date': (now + timedelta(days=2)).strftime('%Y-%m-%d'), # This Saturday
            'event_time': '08:00',
            'event_location': 'Old Mill Road Lot',
            'is_active': 1
        },
        {
            'title': 'URGENT: Temporary Road Closure - Main Street',
            'content': '⚠️ Attention Residents! Main Street will be closed between Oak Ave and Elm Street for urgent infrastructure repairs on ' + (now + timedelta(days=1)).strftime('%Y-%m-%d') + ' from 7 AM to 5 PM. Please use detours via Maple Lane. Your cooperation is appreciated.',
            'category': 'urgent',
            'is_urgent': 1,
            'created_at': now.isoformat(),
            'expires_at': (now + timedelta(hours=30)).isoformat(), # Expires day after the event
            'event_date': (now + timedelta(days=1)).strftime('%Y-%m-%d'),
            'event_time': None, # Time range in content
            'event_location': 'Main Street (Oak Ave to Elm St)',
            'is_active': 1
        },
        {
            'title': 'Community Book Club - New Members Welcome!',
            'content': '📚 Love to read and discuss? Our friendly book club is looking for new members! We meet bi-weekly to discuss a variety of genres. First meeting for the new season is ' + (now + timedelta(days=14)).strftime('%Y-%m-%d') + '. Come share your passion for books!',
            'category': 'event',
            'is_urgent': 0,
            'created_at': (now - timedelta(days=10)).isoformat(),
            'expires_at': (now + timedelta(days=30)).isoformat(), # Expires a month after posting
            'event_date': (now + timedelta(days=14)).strftime('%Y-%m-%d'),
            'event_time': '19:30',
            'event_location': 'Community Library Reading Room',
            'is_active': 1
        },
        {
            'title': 'Reminder: Annual Town Hall Meeting Next Week',
            'content': '🗣️ Don\'t forget! Our annual Town Hall Meeting is scheduled for next ' + (now + timedelta(days=7)).strftime('%A, %B %d') + '. This is your chance to voice concerns, ask questions, and contribute to our community\'s future. Light refreshments will be served.',
            'category': 'announcement',
            'is_urgent': 0,
            'created_at': (now - timedelta(days=5)).isoformat(),
            'expires_at': (now + timedelta(days=8)).isoformat(), # Expires after the meeting
            'event_date': (now + timedelta(days=7)).strftime('%Y-%m-%d'),
            'event_time': '18:00',
            'event_location': 'Town Hall Auditorium',
            'is_active': 1
        },
        {
            'title': 'Join Our Community Garden Project!',
            'content': '🌻 Get your hands dirty and help us cultivate our beautiful community garden! We\'re looking for volunteers to help with planting, weeding, and harvesting. No experience necessary, just a love for nature!',
            'category': 'announcement',
            'is_urgent': 0,
            'created_at': (now - timedelta(days=20)).isoformat(),
            'expires_at': None, # Ongoing project
            'event_date': None,
            'event_time': None,
            'event_location': 'Behind the Community Center',
            'is_active': 1
        },
        {
            'title': 'Expired: Flash Sale at Local Bakery!',
            'content': '🥐 For a limited time, get 20% off all pastries at "Sweet Treats Bakery"! This amazing offer has now ended, but thank you for supporting local businesses!',
            'category': 'announcement',
            'is_urgent': 1,
            'created_at': (now - timedelta(days=10)).isoformat(),
            'expires_at': (now - timedelta(days=2)).isoformat(), # Expired two days ago
            'event_date': None,
            'event_time': None,
            'event_location': 'Sweet Treats Bakery',
            'is_active': 1 # Active, but expired, so should not show on public index
        },
        {
            'title': 'Draft: Proposal for New Bike Lanes',
            'content': '🚲 We are currently drafting a proposal to introduce dedicated bike lanes throughout the community. We envision a safer and more eco-friendly way to travel. Public consultation details coming soon!',
            'category': 'announcement',
            'is_urgent': 0,
            'created_at': (now - timedelta(days=1)).isoformat(),
            'expires_at': None,
            'event_date': None,
            'event_time': None,
            'event_location': None,
            'is_active': 0 # Not active, only visible in admin dashboard
        },
        {
            'title': 'Volunteer Drive for Local Animal Shelter',
            'content': '🐾 Our furry friends at the local animal shelter need your help! We are looking for compassionate volunteers for various roles: dog walking, cat cuddling, cleaning, and administrative tasks. Make a difference!',
            'category': 'announcement',
            'is_urgent': 0,
            'created_at': (now - timedelta(days=4)).isoformat(),
            'expires_at': (now + timedelta(days=60)).isoformat(), # Expires in 2 months
            'event_date': None,
            'event_time': None,
            'event_location': 'Happy Tails Animal Shelter',
            'is_active': 1
        },
    ]

    for notice in notices_to_insert:
        try:
            cursor.execute(
                """
                INSERT INTO notices (title, content, category, is_urgent, created_at, expires_at,
                                     event_date, event_time, event_location, is_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (notice['title'], notice['content'], notice['category'], notice['is_urgent'],
                 notice['created_at'], notice['expires_at'], notice['event_date'],
                 notice['event_time'], notice['event_location'], notice['is_active'])
            )
            print(f"Inserted notice: {notice['title']}")
        except sqlite3.Error as e:
            print(f"Error inserting notice '{notice['title']}': {e}")
    
    conn.commit()
    conn.close()
    print("\nDatabase seeding complete! Your portfolio notices are ready.")

if __name__ == '__main__':
    seed_data()