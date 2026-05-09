import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.utils.text import slugify
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from apps.core.decorators import system_required
from apps.accounts.models import CustomUser
from apps.categories.models import Category
from apps.tickets.models import Ticket
from .models import Event, Tag


@system_required
def event_list(request):
    q = request.GET.get('q', '')
    status_f = request.GET.get('status', '')
    deleted_f = request.GET.get('deleted', '')
    tag_f = request.GET.get('tag', '')
    events = Event.all_objects.select_related('organiser', 'category', 'created_by').prefetch_related('tags').order_by('-created_at')
    
    if q:
        events = events.filter(Q(title__icontains=q) | Q(city__icontains=q) | Q(organiser__username__icontains=q))
    if status_f:
        events = events.filter(status=status_f)
    if tag_f:
        events = events.filter(tags__slug=tag_f)
    events = events.filter(deleted_at__isnull=(deleted_f != '1'))
    
    paginator = Paginator(events, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'events/admin/list.html', {
        'events': page_obj, 'page_obj': page_obj,
        'q': q, 'status_filter': status_f, 'deleted_filter': deleted_f, 'tag_filter': tag_f,
        'all_tags': Tag.objects.filter(deleted_at__isnull=True),
    })


@system_required
def event_detail(request, event_id):
    event = get_object_or_404(Event.all_objects, pk=event_id)
    tickets = Ticket.objects.filter(event=event).select_related('attendee').order_by('-created_at')
    return render(request, 'events/admin/detail.html', {'event': event, 'tickets': tickets})


@system_required
def event_create(request):
    categories = Category.objects.filter(parent=None)
    all_tags = Tag.objects.filter(deleted_at__isnull=True)
    
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        organiser = request.user
        org_id = request.POST.get('organiser_id')
        
        if org_id:
            try:
                organiser = CustomUser.objects.get(pk=org_id)
            except CustomUser.DoesNotExist:
                pass
        
        cat_id = request.POST.get('category')
        category = Category.objects.filter(pk=cat_id).first() if cat_id else None
        
        event = Event.objects.create(
            title=title,
            slug=slugify(title) + '-' + uuid.uuid4().hex[:4],
            description=request.POST.get('description', ''),
            category=category,
            event_type=request.POST.get('event_type', 'offline'),
            status=request.POST.get('status', 'draft'),
            start_date=request.POST.get('start_date'),
            end_date=request.POST.get('end_date'),
            venue=request.POST.get('venue', ''),
            city=request.POST.get('city', ''),
            address=request.POST.get('address', ''),
            online_link=request.POST.get('online_link', ''),
            max_capacity=int(request.POST.get('max_capacity', 0) or 0),
            ticket_price=float(request.POST.get('ticket_price', 0) or 0),
            is_free=request.POST.get('is_free') == 'on',
            is_featured=request.POST.get('is_featured') == 'on',
            organiser=organiser,
            created_by=request.user,
            updated_by=request.user,
        )
        
        tag_ids = request.POST.getlist('tags')
        if tag_ids:
            event.tags.set(Tag.objects.filter(pk__in=tag_ids))
        
        if 'banner' in request.FILES:
            from apps.media.utils import save_uploaded_file
            save_uploaded_file(request.FILES['banner'], event, 'event_banner')
        
        messages.success(request, f'Event "{event.title}" created.')
        return redirect('admin_events:event_list')
    
    return render(request, 'events/admin/form.html', {
        'action': 'Create', 'title': 'Create Event',
        'categories': categories, 'all_tags': all_tags,
    })


@system_required
def event_edit(request, event_id):
    event = get_object_or_404(Event.all_objects, pk=event_id)
    categories = Category.objects.filter(parent=None)
    all_tags = Tag.objects.filter(deleted_at__isnull=True)
    selected_tag_ids = list(event.tags.values_list('id', flat=True))
    
    if request.method == 'POST':
        event.title = request.POST.get('title', event.title)
        event.description = request.POST.get('description', event.description)
        event.event_type = request.POST.get('event_type', event.event_type)
        event.status = request.POST.get('status', event.status)
        event.start_date = request.POST.get('start_date', event.start_date)
        event.end_date = request.POST.get('end_date', event.end_date)
        event.venue = request.POST.get('venue', '')
        event.city = request.POST.get('city', '')
        event.address = request.POST.get('address', '')
        event.online_link = request.POST.get('online_link', '')
        event.max_capacity = int(request.POST.get('max_capacity', 0) or 0)
        event.ticket_price = float(request.POST.get('ticket_price', 0) or 0)
        event.is_free = request.POST.get('is_free') == 'on'
        event.is_featured = request.POST.get('is_featured') == 'on'
        event.updated_by = request.user
        
        cat_id = request.POST.get('category')
        event.category = Category.objects.filter(pk=cat_id).first() if cat_id else None
        
        org_id = request.POST.get('organiser_id')
        if org_id:
            try:
                event.organiser = CustomUser.objects.get(pk=org_id)
            except CustomUser.DoesNotExist:
                pass
        
        event.save()
        
        tag_ids = request.POST.getlist('tags')
        event.tags.set(Tag.objects.filter(pk__in=tag_ids))
        
        if 'banner' in request.FILES:
            from apps.media.utils import save_uploaded_file
            save_uploaded_file(request.FILES['banner'], event, 'event_banner')
        
        messages.success(request, f'Event "{event.title}" updated.')
        return redirect('admin_events:event_list')
    
    return render(request, 'events/admin/form.html', {
        'action': 'Edit', 'title': f'Edit - {event.title}',
        'event': event, 'categories': categories,
        'all_tags': all_tags, 'selected_tag_ids': selected_tag_ids,
    })


@system_required
@require_POST
def event_change_status(request, event_id):
    event = get_object_or_404(Event.all_objects, pk=event_id)
    status = request.POST.get('status')
    
    if status in dict(Event.Status.choices):
        event.status = status
        event.updated_by = request.user
        event.save(update_fields=['status', 'updated_by', 'updated_at'])
        messages.success(request, f'Status → {event.status}')
    
    return redirect('admin_events:event_list')


@system_required
@require_POST
def event_delete(request, event_id):
    event = get_object_or_404(Event.all_objects, pk=event_id)
    
    if event.deleted_at:
        event.restore()
        messages.success(request, f'"{event.title}" restored.')
    else:
        event.soft_delete(user=request.user)
        messages.success(request, f'"{event.title}" deleted.')
    
    return redirect('admin_events:event_list')


@system_required
def event_attendees(request, event_id):
    event = get_object_or_404(Event.all_objects, pk=event_id)
    tickets = Ticket.objects.filter(event=event).select_related('attendee').order_by('-created_at')
    
    paginator = Paginator(tickets, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'events/admin/attendees.html', {
        'event': event, 'tickets': page_obj, 'page_obj': page_obj,
    })


# ── Tag CRUD ─────────────────────────────────────────────────────────────────

@system_required
def tag_list(request):
    q = request.GET.get('q', '')
    tags = Tag.objects.all()
    if q:
        tags = tags.filter(name__icontains=q)
    
    paginator = Paginator(tags, 20)
    page_obj = paginator.get_page(request.GET.get('page'))
    
    return render(request, 'events/admin/tags.html', {
        'tags': page_obj, 'page_obj': page_obj, 'q': q,
    })


@system_required
def tag_create(request):
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        color = request.POST.get('color', '#6366f1')
        slug = slugify(name)
        
        if not name:
            messages.error(request, 'Tag name is required.')
        elif Tag.objects.filter(slug=slug).exists():
            messages.error(request, f'Tag "{name}" already exists.')
        else:
            Tag.objects.create(name=name, slug=slug, color=color, created_by=request.user)
            messages.success(request, f'Tag "{name}" created.')
            return redirect('admin_events:tag_list')
    
    return render(request, 'events/admin/tag_form.html', {'action': 'Create', 'title': 'Create Tag'})


@system_required
def tag_edit(request, tag_id):
    tag = get_object_or_404(Tag, pk=tag_id)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        tag.name = name
        tag.color = request.POST.get('color', tag.color)
        tag.slug = slugify(name)
        tag.updated_by = request.user
        tag.save()
        messages.success(request, f'Tag "{tag.name}" updated.')
        return redirect('admin_events:tag_list')
    
    return render(request, 'events/admin/tag_form.html', {
        'action': 'Edit', 'title': f'Edit Tag - {tag.name}', 'tag': tag,
    })


@system_required
@require_POST
def tag_delete(request, tag_id):
    tag = get_object_or_404(Tag, pk=tag_id)
    if tag.deleted_at:
        tag.restore()
        messages.success(request, f'Tag "{tag.name}" restored.')
    else:
        tag.soft_delete(user=request.user)
        messages.success(request, f'Tag "{tag.name}" deleted.')
    return redirect('admin_events:tag_list')
