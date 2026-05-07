"""
Master seed command — calls individual seeder files.

Usage:
  python manage.py seed                  # run all seeders
  python manage.py seed --groups         # groups & permissions only
  python manage.py seed --users          # test users only
  python manage.py seed --categories     # categories only
  python manage.py seed --events         # events only
  python manage.py seed --flush          # wipe data, then seed everything
"""
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = 'Seed the database using individual seeder files in apps/database/seeders/'

    def add_arguments(self, parser):
        parser.add_argument('--groups',     action='store_true', help='Seed groups & permissions')
        parser.add_argument('--users',      action='store_true', help='Seed test users')
        parser.add_argument('--categories', action='store_true', help='Seed categories')
        parser.add_argument('--events',     action='store_true', help='Seed sample events')
        parser.add_argument('--flush',      action='store_true', help='Flush data before seeding')

    def handle(self, *args, **options):
        run_all = not any([
            options['groups'],
            options['users'],
            options['categories'],
            options['events'],
        ])

        if options['flush']:
            self._flush()

        if run_all or options['groups']:
            self.stdout.write(self.style.MIGRATE_HEADING('── Groups & Permissions ──'))
            from apps.database.seeders import groups_seeder
            groups_seeder.run(stdout=self.stdout)

        if run_all or options['users']:
            self.stdout.write(self.style.MIGRATE_HEADING('── Users ──'))
            from apps.database.seeders import users_seeder
            users_seeder.run(stdout=self.stdout)

        if run_all or options['categories']:
            self.stdout.write(self.style.MIGRATE_HEADING('── Categories ──'))
            from apps.database.seeders import categories_seeder
            categories_seeder.run(stdout=self.stdout)

        if run_all or options['events']:
            self.stdout.write(self.style.MIGRATE_HEADING('── Events ──'))
            from apps.database.seeders import events_seeder
            events_seeder.run(stdout=self.stdout)

        self.stdout.write(self.style.SUCCESS('\n✅  Seeding complete!'))

    def _flush(self):
        from apps.accounts.models import CustomUser
        from apps.events.models import Event, Ticket
        from apps.categories.models import Category
        from django.contrib.auth.models import Group

        self.stdout.write(self.style.WARNING('Flushing existing data...'))
        Ticket.all_objects.all().delete()
        Event.all_objects.all().delete()
        Category.all_objects.all().delete()
        CustomUser.objects.filter(is_superuser=False).delete()
        Group.objects.all().delete()
        self.stdout.write('  Done.\n')
