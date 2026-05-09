import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from apps.tickets.models import Ticket
from apps.categories.models import Category
from .models import Event, Tag


def _is_organiser(user):
    return user.is_authenticated and (
        user.groups.filter(name='Organiser').exists() or user.is_system_user
    )


def event_list(request):
    events = Event.objects.filter(status='published').select_related('category').prefetch_related('tags')
    q = request.GET.get('q', '')
    cat_slug = request.GET.get('category', '')
    event_type = request.GET.get('type', '')
    tag_slug = request.GET.get('tag', '')

    if q:
        events = events.filter(
            Q(title__icontains=q) | Q(description__icontains=q) | Q(city__icontains=q)
        )
    if cat_slug:
        # Include the selected category AND all its descendants
        # so picking "Technology" also shows AI, Web Dev, Cybersecurity events
        try:
            selected_cat = Category.objects.get(slug=cat_slug)
            all_cat_ids = [selected_cat.id] + [c.id for c in selected_cat.get_descendants()]
            events = events.filter(category_id__in=all_cat_ids)
        except Category.DoesNotExist:
            events = events.none()
    if event_type:
        events = events.filter(event_type=event_type)
    if tag_slug:
        events = events.filter(tags__slug=tag_slug)

    paginator = Paginator(events, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'events/web/list.html', {
        'events': page_obj, 'page_obj': page_obj,
        'categories': Category.objects.filter(parent=None),
        'all_tags': Tag.objects.filter(deleted_at__isnull=True),
        'current_category': cat_slug,
        'current_type': event_type,
        'current_tag': tag_slug,
        'query': q,
    })


def event_detail(request, slug):
    event = get_object_or_404(Event, slug=slug, status='published')
    user_ticket = None
    
    if request.user.is_authenticated:
        user_ticket = Ticket.objects.filter(event=event, attendee=request.user).first()
    
    return render(request, 'events/web/detail.html', {
        'event': event, 
        'user_ticket': user_ticket, 
        'banner': event.get_banner(),
        'tags': event.tags.filter(deleted_at__isnull=True),
    })


@login_required
@require_POST
def register_for_event(request, slug):
    event = get_object_or_404(Event, slug=slug, status='published')
    
    if Ticket.objects.filter(event=event, attendee=request.user).exists():
        messages.warning(request, 'Already registered.')
        return redirect('web_events:event_detail', slug=slug)
    
    if event.spots_left == 0:
        messages.error(request, 'Event is fully booked.')
        return redirect('web_events:event_detail', slug=slug)
    
    Ticket.objects.create(
        event=event, 
        attendee=request.user,
        ticket_code=f'TKT-{uuid.uuid4().hex[:8].upper()}',
        status='confirmed', 
        amount_paid=event.ticket_price,
        created_by=request.user,
    )
    
    messages.success(request, 'Registered! Check My Tickets.')
    return redirect('web_tickets:my_tickets')


@login_required
def organiser_events(request):
    if not _is_organiser(request.user):
        return redirect('web_events:event_list')
    
    events = Event.objects.filter(organiser=request.user).annotate(
        confirmed_tickets=Count('tickets', filter=Q(tickets__status='confirmed'))
    )
    
    paginator = Paginator(events, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'events/web/organiser_events.html', {
        'events': page_obj, 'page_obj': page_obj,
        'total_events': events.count(),
        'published': events.filter(status='published').count(),
        'total_attendees': sum(e.confirmed_tickets for e in events),
    })


@login_required
def event_create(request):
    if not _is_organiser(request.user):
        messages.error(request, 'Organisers only.')
        return redirect('web_events:event_list')
    
    categories = Category.objects.filter(parent=None)
    all_tags = Tag.objects.filter(deleted_at__isnull=True)
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        
        event = Event.objects.create(
            organiser=request.user,
            title=title,
            slug=slugify(title) + '-' + uuid.uuid4().hex[:4],
            description=request.POST.get('description', ''),
            event_type=request.POST.get('event_type', 'offline'),
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date'),
            venue=request.POST.get('venue', ''),
            city=request.POST.get('city', ''),
            address=request.POST.get('address', ''),
            online_link=request.POST.get('online_link', ''),
            max_capacity=int(request.POST.get('max_capacity', 0) or 0),
            ticket_price=float(request.POST.get('ticket_price', 0) or 0),
            is_free=request.POST.get('is_free') == 'on',
            status='draft',
            created_by=request.user, 
            updated_by=request.user,
        )
        
        cat_id = request.POST.get('category')
        if cat_id:
            event.category_id = int(cat_id)
            event.save(update_fields=['category_id'])
        
        tag_ids = request.POST.getlist('tags')
        if tag_ids:
            event.tags.set(Tag.objects.filter(pk__in=tag_ids))
        
        if 'banner' in request.FILES:
            from apps.media.utils import save_uploaded_file
            save_uploaded_file(request.FILES['banner'], event, 'event_banner')
        
        messages.success(request, f'Event "{event.title}" created as Draft.')
        return redirect('web_events:organiser_events')
    
    return render(request, 'events/web/form.html', {
        'categories': categories, 
        'all_tags': all_tags,
        'action': 'Create',
    })


@login_required
def event_edit(request, slug):
    event = get_object_or_404(Event, slug=slug, organiser=request.user)
    categories = Category.objects.filter(parent=None)
    all_tags = Tag.objects.filter(deleted_at__isnull=True)
    selected_tag_ids = list(event.tags.values_list('id', flat=True))
    
    if request.method == 'POST':
        event.title = request.POST.get('title', event.title)
        event.description = request.POST.get('description', event.description)
        event.event_type = request.POST.get('event_type', event.event_type)
        event.start_date = request.POST.get('start_date', event.start_date)
        event.end_date = request.POST.get('end_date', event.end_date)
        event.venue = request.POST.get('venue', event.venue)
        event.city = request.POST.get('city', event.city)
        event.status = request.POST.get('status', event.status)
        event.max_capacity = int(request.POST.get('max_capacity', event.max_capacity) or 0)
        event.ticket_price = float(request.POST.get('ticket_price', event.ticket_price) or 0)
        event.is_free = request.POST.get('is_free') == 'on'
        event.updated_by = request.user
        
        cat_id = request.POST.get('category')
        event.category_id = int(cat_id) if cat_id else None
        event.save()
        
        tag_ids = request.POST.getlist('tags')
        event.tags.set(Tag.objects.filter(pk__in=tag_ids))
        
        messages.success(request, 'Event updated.')
        return redirect('web_events:organiser_events')
    
    return render(request, 'events/web/form.html', {
        'event': event, 
        'categories': categories, 
        'all_tags': all_tags,
        'selected_tag_ids': selected_tag_ids,
        'action': 'Edit',
    })


@login_required
def event_attendees(request, slug):
    event = get_object_or_404(Event, slug=slug, organiser=request.user)
    tickets = Ticket.objects.filter(event=event).select_related('attendee').order_by('-created_at')
    
    paginator = Paginator(tickets, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'events/web/attendees.html', {
        'event': event, 'tickets': page_obj, 'page_obj': page_obj,
    })


def tag_events(request, slug):
    from django.shortcuts import get_object_or_404
    tag = get_object_or_404(Tag, slug=slug, deleted_at__isnull=True)
    events_qs = Event.objects.filter(
        tags=tag, status='published'
    ).order_by('-start_date').prefetch_related('tags').select_related('category')

    paginator = Paginator(events_qs, 12)
    page_obj = paginator.get_page(request.GET.get('page'))

    return render(request, 'events/web/tag_events.html', {
        'tag': tag,
        'events': page_obj,
        'page_obj': page_obj,
        'total_events': events_qs.count(),
        'all_tags': Tag.objects.filter(deleted_at__isnull=True),
    })
