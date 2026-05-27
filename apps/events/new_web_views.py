"""
New views for Features 3, 4, 5, 7, 8.
Append / merge these into apps/events/web_views.py
"""
import uuid, json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import Event


# ── Feature 3: Analytics ──────────────────────────────────────────────────────
@login_required
def event_analytics(request, slug):
    from django.db.models.functions import TruncDay
    from django.db.models import Count, Sum
    from apps.tickets.models import Ticket
    event = get_object_or_404(Event, slug=slug, organiser=request.user)
    tickets_qs = Ticket.all_objects.filter(event=event)
    daily_sales = (tickets_qs.filter(status='confirmed')
        .annotate(day=TruncDay('created_at')).values('day')
        .annotate(count=Count('id'), revenue=Sum('amount_paid')).order_by('day'))
    status_counts = {
        'confirmed': tickets_qs.filter(status='confirmed').count(),
        'cancelled':  tickets_qs.filter(status='cancelled').count(),
        'attended':   tickets_qs.filter(status='attended').count(),
        'pending':    tickets_qs.filter(status='pending').count(),
    }
    total_tickets = sum(status_counts.values())
    total_revenue = tickets_qs.filter(status='confirmed').aggregate(t=Sum('amount_paid'))['t'] or 0
    confirmed_attended = status_counts['confirmed'] + status_counts['attended']
    attendance_rate = round((status_counts['attended'] / confirmed_attended * 100) if confirmed_attended else 0, 1)
    return render(request, 'events/web/analytics.html', {
        'event': event,
        'status_counts':   status_counts,
        'total_tickets':   total_tickets,
        'total_revenue':   total_revenue,
        'attendance_rate': attendance_rate,
        'capacity_pct':    round(event.tickets_sold / event.max_capacity * 100, 1) if event.max_capacity else None,
        'chart_labels':    json.dumps([str(d['day'].date()) for d in daily_sales]),
        'chart_sales':     json.dumps([d['count'] for d in daily_sales]),
        'chart_revenue':   json.dumps([float(d['revenue'] or 0) for d in daily_sales]),
    })


# ── Feature 4: Wishlist ───────────────────────────────────────────────────────
@login_required
@require_POST
def toggle_wishlist(request, slug):
    from .models import Wishlist
    from django.contrib import messages
    event = get_object_or_404(Event, slug=slug)
    obj, created = Wishlist.objects.get_or_create(user=request.user, event=event)
    if not created:
        obj.delete()
        messages.info(request, f'Removed from wishlist.')
    else:
        messages.success(request, f'Saved to wishlist!')
    return redirect('web_events:event_detail', slug=slug)


@login_required
def my_wishlist(request):
    from .models import Wishlist
    items = Wishlist.objects.filter(user=request.user).select_related('event', 'event__category')
    return render(request, 'events/web/wishlist.html', {'items': items})


# ── Feature 5: Reviews ────────────────────────────────────────────────────────
@login_required
@require_POST
def submit_review(request, slug):
    from .models import Review
    from apps.tickets.models import Ticket
    event  = get_object_or_404(Event, slug=slug)
    ticket = Ticket.objects.filter(event=event, attendee=request.user, status__in=['confirmed','attended']).first()
    if not ticket:
        messages.error(request, 'Only attendees can leave a review.')
        return redirect('web_events:event_detail', slug=slug)
    if event.is_upcoming:
        messages.error(request, 'Reviews open after the event ends.')
        return redirect('web_events:event_detail', slug=slug)
    rating = int(request.POST.get('rating', 0))
    body   = request.POST.get('body', '').strip()
    if not (1 <= rating <= 5):
        messages.error(request, 'Please choose a rating 1–5.')
        return redirect('web_events:event_detail', slug=slug)
    Review.objects.update_or_create(event=event, reviewer=request.user, defaults={'rating': rating, 'body': body})
    messages.success(request, 'Review submitted!')
    return redirect('web_events:event_detail', slug=slug)


@login_required
@require_POST
def delete_review(request, slug):
    from .models import Review
    review = get_object_or_404(Review, event__slug=slug, reviewer=request.user)
    review.delete()
    messages.success(request, 'Review deleted.')
    return redirect('web_events:event_detail', slug=slug)


# ── Feature 8: Tier management ────────────────────────────────────────────────
@login_required
def manage_tiers(request, slug):
    from apps.tickets.models import TicketTier
    event = get_object_or_404(Event, slug=slug, organiser=request.user)
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'add':
            TicketTier.objects.create(
                event=event,
                name=request.POST.get('name','General'),
                description=request.POST.get('description',''),
                price=float(request.POST.get('price',0) or 0),
                total_slots=int(request.POST.get('total_slots',0) or 0),
                sale_start=request.POST.get('sale_start') or None,
                sale_end=request.POST.get('sale_end') or None,
                sort_order=TicketTier.objects.filter(event=event).count(),
            )
            messages.success(request, 'Tier added.')
        elif action == 'delete':
            TicketTier.objects.filter(pk=request.POST.get('tier_id'), event=event).delete()
            messages.success(request, 'Tier deleted.')
        return redirect('web_events:manage_tiers', slug=slug)
    return render(request, 'events/web/tiers.html', {
        'event': event,
        'tiers': event.tiers.all(),
    })
