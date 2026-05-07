"""
Events seeder — sample events with realistic data.
"""
from django.utils import timezone
from django.utils.text import slugify
import uuid
from datetime import timedelta


EVENTS_DATA = [
    {
        'title':        'TechFest 2025 — AI & Beyond',
        'description':  (
            'Join us for the biggest tech conference in the region. '
            'Speakers from Google, Microsoft, and leading AI startups '
            'will cover machine learning, generative AI, and the future of work.'
        ),
        'category_slug': 'ai',
        'event_type':   'offline',
        'venue':        'Convention Center Hall A',
        'city':         'Mumbai',
        'days_from_now': 15,
        'duration_hours': 24,
        'max_capacity': 500,
        'ticket_price': 999,
        'is_free':      False,
        'is_featured':  True,
        'status':       'published',
        'organiser':    'organiser',   # 'organiser' = organiser user, 'admin' = admin user
    },
    {
        'title':        'Sunset Music Festival',
        'description':  (
            'An unforgettable evening of live music, food stalls, and great vibes. '
            'Featuring top indie bands, acoustic sets, and headline DJ acts.'
        ),
        'category_slug': 'live-concerts',
        'event_type':   'offline',
        'venue':        'Amphitheater Ground',
        'city':         'Pune',
        'days_from_now': 7,
        'duration_hours': 8,
        'max_capacity': 1000,
        'ticket_price': 599,
        'is_free':      False,
        'is_featured':  True,
        'status':       'published',
        'organiser':    'organiser',
    },
    {
        'title':        'Startup Pitch Day — Season 4',
        'description':  (
            'Watch 20 promising startups pitch to a panel of top investors. '
            'Networking session, fireside chats, and investor Q&A included.'
        ),
        'category_slug': 'startups',
        'event_type':   'hybrid',
        'venue':        'Innovation Hub',
        'city':         'Bangalore',
        'days_from_now': 3,
        'duration_hours': 6,
        'max_capacity': 200,
        'ticket_price': 0,
        'is_free':      True,
        'is_featured':  False,
        'status':       'published',
        'organiser':    'admin',
    },
    {
        'title':        'Street Food Carnival 2025',
        'description':  (
            'Explore cuisines from 40+ vendors across India and abroad. '
            'Live cooking demos, competitions, and prizes for food lovers.'
        ),
        'category_slug': 'street-food',
        'event_type':   'offline',
        'venue':        'City Park',
        'city':         'Delhi',
        'days_from_now': 20,
        'duration_hours': 30,
        'max_capacity': 0,
        'ticket_price': 0,
        'is_free':      True,
        'is_featured':  True,
        'status':       'published',
        'organiser':    'admin',
    },
    {
        'title':        'Modern Art Exhibition — Emerging Voices',
        'description':  (
            'A curated showcase of contemporary paintings, sculptures, '
            'and digital art from 50 emerging artists across the country.'
        ),
        'category_slug': 'painting',
        'event_type':   'offline',
        'venue':        'National Gallery of Modern Art',
        'city':         'Chennai',
        'days_from_now': 10,
        'duration_hours': 360,
        'max_capacity': 300,
        'ticket_price': 150,
        'is_free':      False,
        'is_featured':  False,
        'status':       'published',
        'organiser':    'organiser',
    },
    {
        'title':        'Cybersecurity Workshop: Ethical Hacking',
        'description':  (
            'Hands-on workshop on penetration testing, vulnerability assessment, '
            'and responsible disclosure. Bring your laptop.'
        ),
        'category_slug': 'cybersecurity',
        'event_type':   'online',
        'venue':        '',
        'city':         'Online',
        'online_link':  'https://meet.example.com/cybersec-workshop',
        'days_from_now': 5,
        'duration_hours': 6,
        'max_capacity': 100,
        'ticket_price': 299,
        'is_free':      False,
        'is_featured':  True,
        'status':       'published',
        'organiser':    'organiser',
    },
    {
        'title':        'Yoga & Mindfulness Retreat',
        'description':  (
            'A full-day wellness retreat with morning yoga, guided meditation, '
            'breathwork sessions, and a plant-based lunch. All levels welcome.'
        ),
        'category_slug': 'yoga',
        'event_type':   'offline',
        'venue':        'Green Valley Resort',
        'city':         'Rishikesh',
        'days_from_now': 25,
        'duration_hours': 12,
        'max_capacity': 50,
        'ticket_price': 1499,
        'is_free':      False,
        'is_featured':  False,
        'status':       'published',
        'organiser':    'organiser',
    },
    {
        'title':        'IPL Watch Party — Grand Finale',
        'description':  (
            'Watch the IPL grand finale on a massive screen with fellow fans. '
            'Free snacks, lucky draws, and cricket trivia all night.'
        ),
        'category_slug': 'cricket',
        'event_type':   'offline',
        'venue':        'Sports Bar, Indiranagar',
        'city':         'Bangalore',
        'days_from_now': 12,
        'duration_hours': 5,
        'max_capacity': 150,
        'ticket_price': 199,
        'is_free':      False,
        'is_featured':  False,
        'status':       'published',
        'organiser':    'organiser',
    },
]


def run(stdout=None):
    from apps.accounts.models import CustomUser
    from apps.events.models import Event
    from apps.categories.models import Category

    def log(msg):
        if stdout:
            stdout.write(msg)

    # get organiser and admin users
    try:
        organiser = CustomUser.objects.get(email='organiser@eventnest.com')
    except CustomUser.DoesNotExist:
        organiser = CustomUser.objects.filter(account_type='platform').first()

    try:
        admin_user = CustomUser.objects.get(email='admin@eventnest.com')
    except CustomUser.DoesNotExist:
        admin_user = CustomUser.objects.filter(is_superuser=True).first()

    if not organiser or not admin_user:
        log('  [skip] No organiser or admin found — run users seeder first')
        return

    for data in EVENTS_DATA:
        owner        = admin_user if data.pop('organiser') == 'admin' else organiser
        cat_slug     = data.pop('category_slug')
        days         = data.pop('days_from_now')
        hours        = data.pop('duration_hours')
        online_link  = data.pop('online_link', '')

        category = Category.objects.filter(slug=cat_slug).first()
        start    = timezone.now() + timedelta(days=days)
        end      = start + timedelta(hours=hours)
        slug     = slugify(data['title']) + '-' + uuid.uuid4().hex[:4]

        event = Event.objects.create(
            organiser   = owner,
            category    = category,
            slug        = slug,
            start_date  = start,
            end_date    = end,
            online_link = online_link,
            created_by  = owner,
            updated_by  = owner,
            **data,
        )
        log(f'  Created event: {event.title}')
