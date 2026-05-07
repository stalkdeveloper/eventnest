import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import Group, Permission
from django.db.models import Count
from django.views.decorators.http import require_POST
from apps.core.decorators import system_required


@system_required
def role_list(request):
    groups = Group.objects.prefetch_related('permissions__content_type').annotate(
        user_count=Count('user')
    ).order_by('name')
    return render(request, 'roles/admin/list.html', {'groups': groups})


@system_required
def role_create(request):
    all_perms = Permission.objects.select_related('content_type').order_by(
        'content_type__app_label', 'codename'
    )
    selected_ids = (
        [int(x) for x in request.POST.getlist('permissions') if x.isdigit()]
        if request.method == 'POST' else []
    )
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, 'Role name is required.')
        elif Group.objects.filter(name=name).exists():
            messages.error(request, f'Role "{name}" already exists.')
        else:
            group = Group.objects.create(name=name)
            group.permissions.set(Permission.objects.filter(pk__in=selected_ids))
            messages.success(request, f'Role "{group.name}" created.')
            return redirect('admin_roles:role_list')
    return render(request, 'roles/admin/form.html', {
        'action': 'Create', 'title': 'Create Role',
        'all_perms': all_perms,
        'selected_perm_ids': json.dumps(selected_ids),
    })


@system_required
def role_edit(request, role_id):
    group     = get_object_or_404(Group, pk=role_id)
    all_perms = Permission.objects.select_related('content_type').order_by(
        'content_type__app_label', 'codename'
    )
    selected_ids = (
        [int(x) for x in request.POST.getlist('permissions') if x.isdigit()]
        if request.method == 'POST'
        else list(group.permissions.values_list('pk', flat=True))
    )
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if not name:
            messages.error(request, 'Role name is required.')
        elif Group.objects.filter(name=name).exclude(pk=role_id).exists():
            messages.error(request, f'Role "{name}" already exists.')
        else:
            group.name = name
            group.save()
            group.permissions.set(Permission.objects.filter(pk__in=selected_ids))
            messages.success(request, f'Role "{group.name}" updated.')
            return redirect('admin_roles:role_list')
    return render(request, 'roles/admin/form.html', {
        'action': 'Edit', 'title': f'Edit Role — {group.name}',
        'group': group, 'all_perms': all_perms,
        'selected_perm_ids': json.dumps(selected_ids),
    })


@system_required
@require_POST
def role_delete(request, role_id):
    group = get_object_or_404(Group, pk=role_id)
    if group.name in ('Admin', 'Organiser', 'Guest'):
        messages.error(request, f'Built-in role "{group.name}" cannot be deleted.')
        return redirect('admin_roles:role_list')
    name = group.name
    group.delete()
    messages.success(request, f'Role "{name}" deleted.')
    return redirect('admin_roles:role_list')
