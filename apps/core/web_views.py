"""Public home page."""
from django.shortcuts import render
from django.db.models import Count
from django.utils import timezone
from apps.events.models import Event
from apps.categories.models import Category


def home(request):
    featured   = Event.objects.filter(status='published', is_featured=True)[:6]
    upcoming   = Event.objects.filter(
        status='published', start_date__gte=timezone.now()
    ).order_by('start_date')[:8]
    categories = Category.objects.filter(parent=None).annotate(
        event_count=Count('events')
    ).order_by('-event_count')[:8]
    return render(request, 'core/home.html', {
        'featured_events': featured,
        'upcoming_events': upcoming,
        'categories': categories,
    })
