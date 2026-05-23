"""
Extra computed properties injected into Event at import time.
Import this in apps/events/apps.py ready() or directly in models.py at the bottom.
"""
from django.db.models import Avg

def _avg_rating(self):
    agg = self.reviews.aggregate(avg=Avg('rating'))
    return round(agg['avg'], 1) if agg['avg'] else None

def _review_count(self):
    return self.reviews.count()

from apps.events.models import Event
Event.avg_rating   = property(_avg_rating)
Event.review_count = property(_review_count)
