# apps/tickets/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.core.mixins import TimeStampedModel, ActiveManager, AllObjectsManager
from apps.events.models import Event  # <-- import from events now


class Ticket(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        CONFIRMED = "confirmed", "Confirmed"
        CANCELLED = "cancelled", "Cancelled"
        ATTENDED = "attended", "Attended"

    event = models.ForeignKey(
        Event,
        on_delete=models.CASCADE,
        related_name="tickets",
    )
    attendee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="tickets",
    )
    ticket_code = models.CharField(max_length=20, unique=True)
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.CONFIRMED)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    notes = models.TextField(blank=True)

    objects = ActiveManager()
    all_objects = AllObjectsManager()

    class Meta:
        unique_together = ["event", "attendee"]
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.ticket_code} - {self.attendee.email} @ {self.event.title}"

    def get_qr(self):
        from apps.media.models import Media
        return Media.objects.filter(
            mediable_type="events.Ticket",
            mediable_id=self.pk,
            source_type="ticket_qr",
        ).first()