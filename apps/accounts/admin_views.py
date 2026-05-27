from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import Group
from django.db.models import Q
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from apps.core.decorators import system_required, superadmin_required
from .models import CustomUser
from .forms import AdminUserCreateForm, AdminUserEditForm, AssignRoleForm


@system_required
def user_list(request):
    q           = request.GET.get('q', '')
    role_filter = request.GET.get('role', '')
    type_filter = request.GET.get('type', '')
    active_f    = request.GET.get('active', '1')

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
    if active_f == '0':
        users = users.filter(is_active=False)
    else:
        users = users.filter(is_active=True)

    paginator = Paginator(users, 20)
    page_obj  = paginator.get_page(request.GET.get('page'))

    return render(request, 'accounts/admin/list.html', {
        'users':        page_obj,
        'page_obj':     page_obj,
        'groups':       Group.objects.all(),
        'q':            q,
        'role_filter':  role_filter,
        'type_filter':  type_filter,
        'active_filter': active_f,
        'account_types': CustomUser.AccountType.choices,
    })


@system_required
def user_create(request):
    form = AdminUserCreateForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        messages.success(request, f'User {user.email} created.')
        return redirect('admin_accounts:user_list')
    return render(request, 'accounts/admin/form.html', {
        'form': form, 'action': 'Create', 'title': 'Create User',
    })


@system_required
def user_edit(request, user_id):
    target = get_object_or_404(CustomUser.objects.prefetch_related('groups'), pk=user_id)
    if not request.user.is_superuser and target.is_superuser:
        messages.error(request, 'Cannot edit a superuser.')
        return redirect('admin_accounts:user_list')
    form = AdminUserEditForm(request.POST or None, instance=target)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, f'User {target.email} updated.')
        return redirect('admin_accounts:user_list')
    return render(request, 'accounts/admin/form.html', {
        'form': form, 'action': 'Edit',
        'title': f'Edit - {target.email}', 'target': target,
    })


@system_required
@require_POST
def user_delete(request, user_id):
    target = get_object_or_404(CustomUser, pk=user_id)
    if target.is_superuser or target == request.user:
        messages.error(request, 'Cannot deactivate this account.')
        return redirect('admin_accounts:user_list')
    target.is_active = False
    target.save(update_fields=['is_active'])
    messages.success(request, f'{target.email} deactivated.')
    return redirect('admin_accounts:user_list')


@system_required
@require_POST
def user_assign_role(request, user_id):
    target = get_object_or_404(CustomUser, pk=user_id)
    if not request.user.is_superuser and target.is_superuser:
        messages.error(request, 'Cannot reassign a superuser.')
        return redirect('admin_accounts:user_list')
    form = AssignRoleForm(request.POST)
    if form.is_valid():
        group = form.cleaned_data['group']
        target.groups.set([group])
        target.account_type = (
            CustomUser.AccountType.SYSTEM if group.name == 'Admin'
            else CustomUser.AccountType.PLATFORM
        )
        target.is_staff = (group.name == 'Admin')
        target.save(update_fields=['account_type', 'is_staff'])
        messages.success(request, f'{target.email} → {group.name}')
    return redirect('admin_accounts:user_list')


@superadmin_required
@require_POST
def user_make_subadmin(request, user_id):
    target = get_object_or_404(CustomUser, pk=user_id)
    group, _ = Group.objects.get_or_create(name='Admin')
    target.account_type = CustomUser.AccountType.SYSTEM
    target.is_staff     = True
    target.groups.set([group])
    target.save(update_fields=['account_type', 'is_staff'])
    messages.success(request, f'{target.email} is now a Sub-Admin.')
    return redirect('admin_accounts:user_list')


@superadmin_required
@require_POST
def user_make_organiser(request, user_id):
    target = get_object_or_404(CustomUser, pk=user_id)
    group, _ = Group.objects.get_or_create(name='Organiser')
    target.account_type = CustomUser.AccountType.PLATFORM
    target.is_staff     = False
    target.groups.set([group])
    target.save(update_fields=['account_type', 'is_staff'])
    messages.success(request, f'{target.email} is now an Organiser.')
    return redirect('admin_accounts:user_list')
