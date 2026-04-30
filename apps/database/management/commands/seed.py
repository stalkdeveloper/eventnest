"""
Usage:
  python manage.py seed                  # seed everything
  python manage.py seed --groups         # seed groups/permissions only
  python manage.py seed --users          # seed test users
  python manage.py seed --events         # seed sample events
  python manage.py seed --flush          # wipe and re-seed everything
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.text import slugify
import uuid
from datetime import timedelta


class Command(BaseCommand):
    help = 'Seed database with groups, permissions and sample data'

    def add_arguments(self, parser):
        parser.add_argument('--groups', action='store_true', help='Seed groups & permissions')
        parser.add_argument('--users',  action='store_true', help='Seed test users')
        parser.add_argument('--events', action='store_true', help='Seed sample events')
        parser.add_argument('--flush',  action='store_true', help='Flush & re-seed everything')

    def handle(self, *args, **options):
        run_all = not any([options['groups'], options['users'], options['events']])

        if options['flush']:
            self.stdout.write(self.style.WARNING('Flushing data...'))
            self._flush()

        if run_all or options['groups']:
            self._seed_groups()

        if run_all or options['users']:
            self._seed_users()

        if run_all or options['events']:
            self._seed_events()

        self.stdout.write(self.style.SUCCESS('✅ Seeding complete!'))

    def _flush(self):
        from apps.accounts.models import CustomUser
        from apps.core.models import Event, Ticket, Category
        Ticket.objects.all().delete()
        Event.objects.all().delete()
        Category.objects.all().delete()
        CustomUser.objects.filter(is_superuser=False).delete()
        Group.objects.all().delete()

    def _seed_groups(self):
        from apps.core.models import Event, Ticket

        # Define permission codenames per group
        group_perms = {
            'Admin': [
                ('view_event', Event), ('add_event', Event), ('change_event', Event), ('delete_event', Event),
                ('view_ticket', Ticket), ('add_ticket', Ticket), ('change_ticket', Ticket), ('delete_ticket', Ticket),
            ],
            'Organiser': [
                ('view_event', Event), ('add_event', Event), ('change_event', Event),
                ('view_ticket', Ticket),
            ],
            'Guest': [
                ('view_event', Event),
                ('add_ticket', Ticket),
            ],
        }

        for group_name, perms in group_perms.items():
            group, created = Group.objects.get_or_create(name=group_name)
            group.permissions.clear()
            for codename, model in perms:
                ct = ContentType.objects.get_for_model(model)
                try:
                    perm = Permission.objects.get(codename=codename, content_type=ct)
                    group.permissions.add(perm)
                except Permission.DoesNotExist:
                    pass
            action = 'Created' if created else 'Updated'
            self.stdout.write(f'  {action} group: {group_name}')

    def _seed_users(self):
        from apps.accounts.models import CustomUser

        users_data = [
            {'username': 'admin_user', 'email': 'admin@eventnest.com',
             'password': 'Admin@1234', 'is_staff': True, 'is_superuser': True, 'group': 'Admin'},
            {'username': 'organiser1', 'email': 'organiser@eventnest.com',
             'password': 'Org@12345', 'group': 'Organiser'},
            {'username': 'guest_user', 'email': 'guest@eventnest.com',
             'password': 'Guest@123', 'group': 'Guest'},
            {'username': 'subadmin1', 'email': 'subadmin@eventnest.com',
             'password': 'Sub@12345', 'is_staff': True, 'group': 'Admin'},
        ]

        for data in users_data:
            group_name = data.pop('group', 'Guest')
            if CustomUser.objects.filter(email=data['email']).exists():
                self.stdout.write(f"  Skipped (exists): {data['email']}")
                continue
            password = data.pop('password')
            user = CustomUser(**data)
            user.set_password(password)
            user.save()
            # Assign group (override auto-assigned Guest)
            user.groups.clear()
            group, _ = Group.objects.get_or_create(name=group_name)
            user.groups.add(group)
            self.stdout.write(f"  Created user: {user.email} [{group_name}]")

    def _seed_events(self):
        from apps.accounts.models import CustomUser
        from apps.core.models import Event, Category

        categories_data = [
            {'name': 'Music', 'slug': 'music', 'color': '#ec4899'},
            {'name': 'Tech', 'slug': 'tech', 'color': '#6366f1'},
            {'name': 'Business', 'slug': 'business', 'color': '#f59e0b'},
            {'name': 'Art & Culture', 'slug': 'art-culture', 'color': '#10b981'},
            {'name': 'Sports', 'slug': 'sports', 'color': '#ef4444'},
            {'name': 'Food & Drink', 'slug': 'food-drink', 'color': '#f97316'},
        ]

        cats = {}
        for c in categories_data:
            obj, _ = Category.objects.get_or_create(slug=c['slug'], defaults=c)
            cats[c['slug']] = obj

        try:
            organiser = CustomUser.objects.get(email='organiser@eventnest.com')
        except CustomUser.DoesNotExist:
            organiser = CustomUser.objects.filter(is_staff=True).first()
            if not organiser:
                self.stdout.write(self.style.WARNING('No organiser found, skipping events'))
                return

        events_data = [
            {
                'title': 'TechFest 2025 - AI & Beyond',
                'description': 'Join us for the biggest tech conference in the region. Speakers from Google, Microsoft, and leading AI startups.',
                'category': cats['tech'],
                'event_type': 'offline',
                'venue': 'Convention Center',
                'city': 'Mumbai',
                'start_date': timezone.now() + timedelta(days=15),
                'end_date': timezone.now() + timedelta(days=16),
                'max_capacity': 500,
                'ticket_price': 999,
                'is_free': False,
                'is_featured': True,
                'status': 'published',
            },
            {
                'title': 'Sunset Music Festival',
                'description': 'An evening of live music, food stalls, and great vibes. Featuring top indie bands and DJs.',
                'category': cats['music'],
                'event_type': 'offline',
                'venue': 'Amphitheater Ground',
                'city': 'Pune',
                'start_date': timezone.now() + timedelta(days=7),
                'end_date': timezone.now() + timedelta(days=7, hours=8),
                'max_capacity': 1000,
                'ticket_price': 599,
                'is_free': False,
                'is_featured': True,
                'status': 'published',
            },
            {
                'title': 'Startup Pitch Day',
                'description': 'Watch 20 promising startups pitch to a panel of top investors. Networking session included.',
                'category': cats['business'],
                'event_type': 'hybrid',
                'venue': 'Innovation Hub',
                'city': 'Bangalore',
                'start_date': timezone.now() + timedelta(days=3),
                'end_date': timezone.now() + timedelta(days=3, hours=6),
                'max_capacity': 200,
                'ticket_price': 0,
                'is_free': True,
                'is_featured': False,
                'status': 'published',
            },
            {
                'title': 'Street Food Carnival',
                'description': 'Explore cuisines from 30+ vendors. Live cooking demos, competitions, and prizes.',
                'category': cats['food-drink'],
                'event_type': 'offline',
                'venue': 'City Park',
                'city': 'Delhi',
                'start_date': timezone.now() + timedelta(days=20),
                'end_date': timezone.now() + timedelta(days=21),
                'max_capacity': 0,
                'ticket_price': 0,
                'is_free': True,
                'is_featured': True,
                'status': 'published',
            },
            {
                'title': 'Modern Art Exhibition',
                'description': 'A curated showcase of contemporary paintings, sculptures, and digital art from 50 emerging artists.',
                'category': cats['art-culture'],
                'event_type': 'offline',
                'venue': 'National Gallery',
                'city': 'Chennai',
                'start_date': timezone.now() + timedelta(days=10),
                'end_date': timezone.now() + timedelta(days=25),
                'max_capacity': 300,
                'ticket_price': 150,
                'is_free': False,
                'is_featured': False,
                'status': 'published',
            },
        ]

        for data in events_data:
            slug = slugify(data['title']) + '-' + uuid.uuid4().hex[:4]
            data['slug'] = slug
            data['organiser'] = organiser
            event = Event.objects.create(**data)
            self.stdout.write(f"  Created event: {event.title}")
