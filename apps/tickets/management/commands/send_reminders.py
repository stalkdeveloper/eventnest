from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.tickets.models import Ticket
from apps.core.email.mailer import Mailer


class Command(BaseCommand):
    help = 'Send reminder emails for events happening tomorrow'

    def handle(self, *args, **options):
        tomorrow_start = timezone.now().replace(hour=0, minute=0, second=0) + timedelta(days=1)
        tomorrow_end   = tomorrow_start + timedelta(days=1)
        tickets = Ticket.objects.filter(
            status='confirmed',
            event__start_date__gte=tomorrow_start,
            event__start_date__lt=tomorrow_end,
        ).select_related('event', 'attendee')
        count = 0
        for ticket in tickets:
            try:
                Mailer.send_event_reminder(ticket)
                count += 1
            except Exception as e:
                self.stderr.write(f'Failed for {ticket.ticket_code}: {e}')
        self.stdout.write(self.style.SUCCESS(f'Sent {count} reminder emails.'))
