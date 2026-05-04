import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import Group, Permission
from django.db.models import Count, Q
from django.utils import timezone
from django.utils.text import slugify
from django.views.decorators.http import require_POST

from apps.accounts.models import CustomUser
from apps.categories.models import Category
from apps.events.models import Event, Ticket
from .decorators import system_required, superadmin_required
from .forms import (
    UserCreateForm, UserEditForm, AssignRoleForm,
    CategoryForm, PanelEventForm, EventStatusForm, RoleForm,
)


# ══════════════════════════════════════════════════════
#  DASHBOARD
# ══════════════════════════════════════════════════════

@system_required
def dashboard(request):
    return render(request, 'panel/dashboard.html', {
        'total_users':   CustomUser.objects.count(),
        'total_events':  Event.all_objects.count(),
        'total_tickets': Ticket.objects.filter(status='confirmed').count(),
        'total_cats':    Category.objects.count(),
        'recent_events': Event.all_objects.order_by('-created_at')
                              .select_related('organiser', 'created_by')[:10],
        'recent_users':  CustomUser.objects.order_by('-date_joined')[:8],
    })


# ══════════════════════════════════════════════════════
#  USERS
# ══════════════════════════════════════════════════════

@system_required
def user_list(request):
    q           = request.GET.get('q', '')
    role_filter = request.GET.get('role', '')
    type_filter = request.GET.get('type', '')
    users = CustomUser.objects.prefetch_related('groups').order_by('-date_joined')
    if q:
        users = users.filter(
            Q(username__icontains=q) | Q(email__icontains=q) |
            Q(first_name__icontains=q) | Q(last_name__icontains=q)
        )
    if role_filter:
        users = users.filter(groups__name=role_filter)
    if type_filter:
        users = users.filter(account_type=type_filter)
    return render(request, 'panel/users/list.html', {
        'users': users, 'groups': Group.objects.all(),
        'q': q, 'role_filter': role_filter, 'type_filter': type_filter,
        'assign_form': AssignRoleForm(),
    })


@system_required
def user_create(request):
    form = UserCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        messages.success(request, f'User {user.email} created.')
        return redirect('panel:user_list')
    return render(request, 'panel/users/form.html', {
        'form': form, 'action': 'Create', 'title': 'Create User',
    })


@system_required
def user_edit(request, user_id):
    target = get_object_or_404(CustomUser, pk=user_id)
    if not request.user.is_superuser and target.is_superuser:
        messages.error(request, 'You cannot edit a superuser.')
        return redirect('panel:user_list')
    form = UserEditForm(request.POST or None, instance=target)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'User {target.email} updated.')
        return redirect('panel:user_list')
    return render(request, 'panel/users/form.html', {
        'form': form, 'action': 'Edit',
        'title': f'Edit - {target.email}', 'target': target,
    })


@system_required
@require_POST
def user_delete(request, user_id):
    target = get_object_or_404(CustomUser, pk=user_id)
    if target.is_superuser:
        messages.error(request, 'Cannot delete a superuser.')
        return redirect('panel:user_list')
    if target == request.user:
        messages.error(request, 'Cannot delete your own account.')
        return redirect('panel:user_list')
    target.is_active = False
    target.save(update_fields=['is_active'])
    messages.success(request, f'User {target.email} deactivated.')
    return redirect('panel:user_list')


@system_required
@require_POST
def user_assign_role(request, user_id):
    target = get_object_or_404(CustomUser, pk=user_id)
    if not request.user.is_superuser and target.is_superuser:
        messages.error(request, 'Cannot reassign a superuser.')
        return redirect('panel:user_list')
    form = AssignRoleForm(request.POST)
    if form.is_valid():
        group = form.cleaned_data['group']
        target.groups.set([group])
        if group.name == 'Admin':
            target.account_type = CustomUser.AccountType.SYSTEM
            target.is_staff     = True
        else:
            target.account_type = CustomUser.AccountType.PLATFORM
            target.is_staff     = False
        target.save(update_fields=['account_type', 'is_staff'])
        messages.success(request, f'{target.email} assigned to {group.name}.')
    return redirect('panel:user_list')


@superadmin_required
@require_POST
def user_make_subadmin(request, user_id):
    target = get_object_or_404(CustomUser, pk=user_id)
    admin_group, _ = Group.objects.get_or_create(name='Admin')
    target.account_type = CustomUser.AccountType.SYSTEM
    target.is_staff     = True
    target.groups.set([admin_group])
    target.save(update_fields=['account_type', 'is_staff'])
    messages.success(request, f'{target.email} is now a Sub-Admin.')
    return redirect('panel:user_list')


@superadmin_required
@require_POST
def user_make_organiser(request, user_id):
    target = get_object_or_404(CustomUser, pk=user_id)
    org_group, _ = Group.objects.get_or_create(name='Organiser')
    target.account_type = CustomUser.AccountType.PLATFORM
    target.is_staff     = False
    target.groups.set([org_group])
    target.save(update_fields=['account_type', 'is_staff'])
    messages.success(request, f'{target.email} is now an Organiser.')
    return redirect('panel:user_list')


# ══════════════════════════════════════════════════════
#  CATEGORIES
# ══════════════════════════════════════════════════════

@system_required
def category_list(request):
    cats = Category.all_objects.select_related('parent', 'created_by').order_by('parent__title', 'title')
    return render(request, 'panel/categories/list.html', {'categories': cats})


@system_required
def category_detail(request, cat_id):
    cat      = get_object_or_404(Category.all_objects, pk=cat_id)
    children = Category.all_objects.filter(parent=cat)
    events   = Event.all_objects.filter(category=cat).order_by('-created_at')[:10]
    return render(request, 'panel/categories/detail.html', {
        'cat': cat, 'children': children, 'events': events,
    })


@system_required
def category_create(request):
    form = CategoryForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        d    = form.cleaned_data
        slug = d.get('slug') or slugify(d['title'])
        parent = None
        if d.get('parent'):
            parent = Category.all_objects.filter(pk=d['parent']).first()
        cat = Category.objects.create(
            title=d['title'], slug=slug,
            description=d.get('description', ''),
            color=d.get('color', '#6366f1'),
            parent=parent, created_by=request.user,
        )
        messages.success(request, f'Category "{cat.title}" created.')
        return redirect('panel:category_list')
    return render(request, 'panel/categories/form.html', {
        'form': form, 'action': 'Create', 'title': 'Create Category',
        'root_cats': Category.objects.filter(parent=None),
    })


@system_required
def category_edit(request, cat_id):
    cat     = get_object_or_404(Category.all_objects, pk=cat_id)
    initial = {
        'title': cat.title, 'slug': cat.slug,
        'description': cat.description, 'color': cat.color,
        'parent': cat.parent_id,
    }
    form = CategoryForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        d           = form.cleaned_data
        cat.title   = d['title']
        cat.slug    = d.get('slug') or slugify(d['title'])
        cat.description = d.get('description', '')
        cat.color   = d.get('color', '#6366f1')
        cat.updated_by = request.user
        cat.parent  = Category.all_objects.filter(pk=d['parent']).first() if d.get('parent') else None
        cat.save()
        messages.success(request, f'Category "{cat.title}" updated.')
        return redirect('panel:category_list')
    return render(request, 'panel/categories/form.html', {
        'form': form, 'action': 'Edit', 'title': f'Edit - {cat.title}',
        'cat': cat,
        'root_cats': Category.objects.filter(parent=None).exclude(pk=cat.pk),
    })


@system_required
@require_POST
def category_delete(request, cat_id):
    cat = get_object_or_404(Category.all_objects, pk=cat_id)
    if cat.deleted_at:
        cat.restore()
        messages.success(request, f'Category "{cat.title}" restored.')
    else:
        cat.soft_delete(user=request.user)
        messages.success(request, f'Category "{cat.title}" deleted.')
    return redirect('panel:category_list')


# ══════════════════════════════════════════════════════
#  EVENTS  (full CRUD inside the panel)
# ══════════════════════════════════════════════════════

@system_required
def event_list(request):
    q         = request.GET.get('q', '')
    status_f  = request.GET.get('status', '')
    deleted_f = request.GET.get('deleted', '')
    events    = Event.all_objects.select_related(
        'organiser', 'category', 'created_by', 'updated_by'
    ).order_by('-created_at')
    if q:
        events = events.filter(Q(title__icontains=q) | Q(city__icontains=q) |
                               Q(organiser__username__icontains=q))
    if status_f:
        events = events.filter(status=status_f)
    if deleted_f == '1':
        events = events.filter(deleted_at__isnull=False)
    else:
        events = events.filter(deleted_at__isnull=True)
    return render(request, 'panel/events/list.html', {
        'events': events, 'q': q,
        'status_filter': status_f, 'deleted_filter': deleted_f,
    })


@system_required
def event_detail(request, event_id):
    event   = get_object_or_404(Event.all_objects, pk=event_id)
    tickets = Ticket.objects.filter(event=event).select_related('attendee').order_by('-created_at')
    return render(request, 'panel/events/detail.html', {
        'event': event, 'tickets': tickets,
    })


@system_required
def event_create(request):
    categories = Category.objects.filter(parent=None)
    all_cats   = Category.objects.all()
    form       = PanelEventForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        d     = form.cleaned_data
        slug  = slugify(d['title']) + '-' + uuid.uuid4().hex[:4]

        # resolve organiser
        organiser = request.user
        if d.get('organiser_id'):
            try:
                organiser = CustomUser.objects.get(pk=d['organiser_id'])
            except CustomUser.DoesNotExist:
                pass

        # resolve category
        category = None
        if d.get('category'):
            category = Category.objects.filter(pk=d['category']).first()

        event = Event.objects.create(
            title=d['title'], slug=slug, description=d['description'],
            category=category, event_type=d['event_type'], status=d['status'],
            start_date=d['start_date'], end_date=d['end_date'],
            venue=d.get('venue', ''), city=d.get('city', ''),
            address=d.get('address', ''), online_link=d.get('online_link', ''),
            max_capacity=d.get('max_capacity', 0),
            ticket_price=d.get('ticket_price', 0),
            is_free=d.get('is_free', True),
            is_featured=d.get('is_featured', False),
            organiser=organiser,
            created_by=request.user, updated_by=request.user,
        )
        if 'banner' in request.FILES:
            from apps.media.utils import save_uploaded_file
            save_uploaded_file(request.FILES['banner'], event, 'event_banner')

        messages.success(request, f'Event "{event.title}" created.')
        return redirect('panel:event_list')

    return render(request, 'panel/events/form.html', {
        'form': form, 'action': 'Create', 'title': 'Create Event',
        'categories': categories, 'all_cats': all_cats,
    })


@system_required
def event_edit(request, event_id):
    event      = get_object_or_404(Event.all_objects, pk=event_id)
    categories = Category.objects.filter(parent=None)
    all_cats   = Category.objects.all()

    # Pre-populate form initial values
    initial = {
        'title':        event.title,
        'description':  event.description,
        'category':     event.category_id,
        'event_type':   event.event_type,
        'status':       event.status,
        'start_date':   event.start_date.strftime('%Y-%m-%dT%H:%M') if event.start_date else '',
        'end_date':     event.end_date.strftime('%Y-%m-%dT%H:%M')   if event.end_date   else '',
        'venue':        event.venue,
        'city':         event.city,
        'address':      event.address,
        'online_link':  event.online_link,
        'max_capacity': event.max_capacity,
        'ticket_price': event.ticket_price,
        'is_free':      event.is_free,
        'is_featured':  event.is_featured,
        'organiser_id': event.organiser_id,
    }
    form = PanelEventForm(request.POST or None, initial=initial)

    if request.method == 'POST' and form.is_valid():
        d = form.cleaned_data
        event.title        = d['title']
        event.description  = d['description']
        event.event_type   = d['event_type']
        event.status       = d['status']
        event.start_date   = d['start_date']
        event.end_date     = d['end_date']
        event.venue        = d.get('venue', '')
        event.city         = d.get('city', '')
        event.address      = d.get('address', '')
        event.online_link  = d.get('online_link', '')
        event.max_capacity = d.get('max_capacity', 0)
        event.ticket_price = d.get('ticket_price', 0)
        event.is_free      = d.get('is_free', True)
        event.is_featured  = d.get('is_featured', False)
        event.updated_by   = request.user
        event.category     = Category.objects.filter(pk=d['category']).first() if d.get('category') else None
        if d.get('organiser_id'):
            try:
                event.organiser = CustomUser.objects.get(pk=d['organiser_id'])
            except CustomUser.DoesNotExist:
                pass
        event.save()

        if 'banner' in request.FILES:
            from apps.media.utils import save_uploaded_file
            save_uploaded_file(request.FILES['banner'], event, 'event_banner')

        messages.success(request, f'Event "{event.title}" updated.')
        return redirect('panel:event_list')

    return render(request, 'panel/events/form.html', {
        'form': form, 'action': 'Edit', 'title': f'Edit - {event.title}',
        'event': event, 'categories': categories, 'all_cats': all_cats,
    })


@system_required
@require_POST
def event_change_status(request, event_id):
    event = get_object_or_404(Event.all_objects, pk=event_id)
    form  = EventStatusForm(request.POST)
    if form.is_valid():
        event.status     = form.cleaned_data['status']
        event.updated_by = request.user
        event.save(update_fields=['status', 'updated_by', 'updated_at'])
        messages.success(request, f'Status set to {event.status}.')
    return redirect('panel:event_list')


@system_required
@require_POST
def event_delete(request, event_id):
    event = get_object_or_404(Event.all_objects, pk=event_id)
    if event.deleted_at:
        event.restore()
        messages.success(request, f'Event "{event.title}" restored.')
    else:
        event.soft_delete(user=request.user)
        messages.success(request, f'Event "{event.title}" deleted.')
    return redirect('panel:event_list')


@system_required
def event_attendees(request, event_id):
    event   = get_object_or_404(Event.all_objects, pk=event_id)
    tickets = Ticket.objects.filter(event=event).select_related('attendee').order_by('-created_at')
    return render(request, 'panel/events/attendees.html', {
        'event': event, 'tickets': tickets,
    })


# ══════════════════════════════════════════════════════
#  ROLES / GROUPS  (full CRUD)
# ══════════════════════════════════════════════════════

@system_required
def role_list(request):
    groups = Group.objects.prefetch_related('permissions__content_type').annotate(
        user_count=Count('user')
    ).order_by('name')
    return render(request, 'panel/roles/list.html', {'groups': groups})


@system_required
def role_create(request):
    form = RoleForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        d = form.cleaned_data
        if Group.objects.filter(name=d['name']).exists():
            form.add_error('name', 'A role with this name already exists.')
        else:
            group = Group.objects.create(name=d['name'])
            group.permissions.set(d['permissions'])
            messages.success(request, f'Role "{group.name}" created.')
            return redirect('panel:role_list')
    return render(request, 'panel/roles/form.html', {
        'form': form, 'action': 'Create', 'title': 'Create Role',
    })


@system_required
def role_edit(request, role_id):
    group   = get_object_or_404(Group, pk=role_id)
    initial = {
        'name':        group.name,
        'permissions': group.permissions.all(),
    }
    form = RoleForm(request.POST or None, initial=initial)
    if request.method == 'POST' and form.is_valid():
        d = form.cleaned_data
        # check name conflict (exclude self)
        if Group.objects.filter(name=d['name']).exclude(pk=role_id).exists():
            form.add_error('name', 'A role with this name already exists.')
        else:
            group.name = d['name']
            group.save()
            group.permissions.set(d['permissions'])
            messages.success(request, f'Role "{group.name}" updated.')
            return redirect('panel:role_list')
    return render(request, 'panel/roles/form.html', {
        'form': form, 'action': 'Edit', 'title': f'Edit Role - {group.name}',
        'group': group,
    })


@system_required
@require_POST
def role_delete(request, role_id):
    group = get_object_or_404(Group, pk=role_id)
    # prevent deleting the three built-in groups
    if group.name in ('Admin', 'Organiser', 'Guest'):
        messages.error(request, f'The built-in role "{group.name}" cannot be deleted.')
        return redirect('panel:role_list')
    name = group.name
    group.delete()
    messages.success(request, f'Role "{name}" deleted.')
    return redirect('panel:role_list')
