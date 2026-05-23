"""
MANUAL STEP REQUIRED:
Add this field to the Ticket model class in apps/tickets/models.py:

    tier = models.ForeignKey(
        'TicketTier',
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='tickets',
    )

Then run:
    python manage.py makemigrations tickets
    python manage.py migrate
"""
