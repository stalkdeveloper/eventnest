"""
Mailer — all transactional emails for EventNest.
Usage:
    from apps.core.email.mailer import Mailer
    Mailer.send_welcome(user)
    Mailer.send_ticket_confirmation(ticket)
    Mailer.send_event_reminder(ticket)
    Mailer.send_ticket_cancelled(ticket)
    Mailer.send_verification_email(user, token)
"""
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class Mailer:
    FROM_EMAIL = settings.DEFAULT_FROM_EMAIL
    SITE_URL   = getattr(settings, 'SITE_URL', 'http://localhost:8000')

    @classmethod
    def _send(cls, subject, to_email, template_txt, template_html, context):
        context.update({'site_url': cls.SITE_URL, 'site_name': 'EventNest'})
        text_body = render_to_string(template_txt,  context)
        html_body = render_to_string(template_html, context)
        msg = EmailMultiAlternatives(subject=subject, body=text_body,
                                     from_email=cls.FROM_EMAIL, to=[to_email])
        msg.attach_alternative(html_body, 'text/html')
        try:
            msg.send(fail_silently=False)
            logger.info(f'Email sent: {subject} → {to_email}')
        except Exception as exc:
            logger.error(f'Email failed: {subject} → {to_email} | {exc}')
            raise

    @classmethod
    def send_welcome(cls, user):
        cls._send('Welcome to EventNest! 🎉', user.email,
                  'emails/welcome.txt', 'emails/welcome.html', {'user': user})

    @classmethod
    def send_verification_email(cls, user, token):
        verify_url = f'{cls.SITE_URL}/verify-email/{token}/'
        cls._send('Verify your EventNest email address', user.email,
                  'emails/verify_email.txt', 'emails/verify_email.html',
                  {'user': user, 'verify_url': verify_url})

    @classmethod
    def send_ticket_confirmation(cls, ticket):
        qr = ticket.get_qr() if hasattr(ticket, 'get_qr') else None
        cls._send(f'Your ticket for {ticket.event.title} — {ticket.ticket_code}',
                  ticket.attendee.email,
                  'emails/ticket_confirmation.txt', 'emails/ticket_confirmation.html',
                  {'ticket': ticket, 'event': ticket.event, 'qr': qr})

    @classmethod
    def send_event_reminder(cls, ticket):
        cls._send(f'Reminder: {ticket.event.title} is tomorrow!', ticket.attendee.email,
                  'emails/event_reminder.txt', 'emails/event_reminder.html',
                  {'ticket': ticket, 'event': ticket.event})

    @classmethod
    def send_ticket_cancelled(cls, ticket):
        cls._send(f'Ticket cancelled — {ticket.event.title}', ticket.attendee.email,
                  'emails/ticket_cancelled.txt', 'emails/ticket_cancelled.html',
                  {'ticket': ticket, 'event': ticket.event})
