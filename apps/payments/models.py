from django.db import models
from django.conf import settings
from apps.core.mixins import TimeStampedModel


class Payment(TimeStampedModel):
    class Status(models.TextChoices):
        PENDING  = 'pending',  'Pending'
        SUCCESS  = 'success',  'Success'
        FAILED   = 'failed',   'Failed'
        REFUNDED = 'refunded', 'Refunded'

    ticket              = models.OneToOneField('tickets.Ticket', on_delete=models.CASCADE, related_name='payment')
    user                = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='payments')
    amount              = models.DecimalField(max_digits=10, decimal_places=2)
    currency            = models.CharField(max_length=3, default='INR')
    status              = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    razorpay_order_id   = models.CharField(max_length=100, blank=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True)
    razorpay_signature  = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.ticket.ticket_code} — {self.status} — ₹{self.amount}'
