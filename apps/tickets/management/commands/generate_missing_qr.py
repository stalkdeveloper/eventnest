"""
Management command to generate QR codes for existing confirmed tickets
that were created before QR auto-generation was added.

Usage:
    python manage.py generate_missing_qr
    python manage.py generate_missing_qr --dry-run
"""
from django.core.management.base import BaseCommand
from apps.tickets.models import Ticket


class Command(BaseCommand):
    help = 'Generate QR codes for confirmed tickets that are missing one'

    def add_arguments(self, parser):
        parser.add_argument('--dry-run', action='store_true', help='Preview only, no changes')

    def handle(self, *args, **options):
        from apps.media.utils import generate_ticket_qr

        tickets = Ticket.objects.filter(status__in=['confirmed', 'attended'])
        missing = [t for t in tickets if not t.get_qr()]

        self.stdout.write(f'Found {len(missing)} ticket(s) missing QR codes.')

        if options['dry_run']:
            for t in missing:
                self.stdout.write(f'  Would generate: {t.ticket_code}')
            return

        ok, fail = 0, 0
        for ticket in missing:
            try:
                generate_ticket_qr(ticket)
                ok += 1
                self.stdout.write(self.style.SUCCESS(f'  ✓ {ticket.ticket_code}'))
            except Exception as e:
                fail += 1
                self.stdout.write(self.style.ERROR(f'  ✗ {ticket.ticket_code}: {e}'))

        self.stdout.write(f'\nDone. Generated: {ok}, Failed: {fail}')
