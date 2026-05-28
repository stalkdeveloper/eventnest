"""
apps/payments/views.py  Razorpay payment flow (optimized).
"""
import uuid, razorpay, hmac, hashlib, json
from django.conf import settings
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.http import HttpResponse
from apps.events.models import Event
from apps.tickets.models import Ticket
from .models import Payment


def _client():
    return razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))


@login_required
def initiate_checkout(request, slug):
    event = get_object_or_404(
        Event.objects.select_related('category'),
        slug=slug, status='published',
    )

    if Ticket.objects.filter(event=event, attendee=request.user).exclude(status='cancelled').exists():
        messages.warning(request, 'Already registered for this event.')
        return redirect('web_events:event_detail', slug=slug)

    if event.spots_left == 0:
        messages.error(request, 'Event is fully booked.')
        return redirect('web_events:event_detail', slug=slug)

    if event.is_free or event.ticket_price == 0:
        return _create_free_ticket(request, event)

    amount_paise = int(event.ticket_price * 100)
    order = _client().order.create({
        'amount':          amount_paise,
        'currency':        'INR',
        'payment_capture': 1,
    })

    return render(request, 'payments/checkout.html', {
        'event':              event,
        'razorpay_order_id':  order['id'],
        'razorpay_key_id':    settings.RAZORPAY_KEY_ID,
        'amount_paise':       amount_paise,
        'amount_display':     event.ticket_price,
        'user_name':          request.user.get_full_name() or request.user.username,
        'user_email':         request.user.email,
        'user_phone':         getattr(request.user, 'phone', '') or '',
    })


@login_required
@require_POST
def payment_success(request):
    order_id   = request.POST.get('razorpay_order_id', '')
    payment_id = request.POST.get('razorpay_payment_id', '')
    signature  = request.POST.get('razorpay_signature', '')
    event_slug = request.POST.get('event_slug', '')

    event = get_object_or_404(
        Event.objects.select_related('category'),
        slug=event_slug,
    )

    # Verify Razorpay signature
    body     = f'{order_id}|{payment_id}'.encode()
    expected = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(), body, hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, signature):
        messages.error(request, 'Payment verification failed. Please contact support.')
        return redirect('web_events:event_detail', slug=event_slug)

    # Guard against duplicate ticket
    if Ticket.objects.filter(event=event, attendee=request.user).exclude(status='cancelled').exists():
        messages.info(request, 'You are already registered for this event.')
        return redirect('web_tickets:my_tickets')

    ticket = Ticket.objects.create(
        event=event,
        attendee=request.user,
        ticket_code=f'TKT-{uuid.uuid4().hex[:8].upper()}',
        status='confirmed',
        amount_paid=event.ticket_price,
        created_by=request.user,
    )
    Payment.objects.create(
        ticket=ticket,
        user=request.user,
        amount=event.ticket_price,
        status=Payment.Status.SUCCESS,
        razorpay_order_id=order_id,
        razorpay_payment_id=payment_id,
        razorpay_signature=signature,
        created_by=request.user,
    )
    # Auto-generate QR code
    try:
        from apps.media.utils import generate_ticket_qr
        generate_ticket_qr(ticket)
    except Exception:
        pass
    try:
        from apps.core.email.mailer import Mailer
        Mailer.send_ticket_confirmation(ticket)
    except Exception:
        pass

    messages.success(request, f'Payment successful! Ticket: {ticket.ticket_code}')
    return redirect('web_tickets:ticket_detail', ticket_id=ticket.pk)


@csrf_exempt
@require_POST
def razorpay_webhook(request):
    sig      = request.META.get('HTTP_X_RAZORPAY_SIGNATURE', '')
    expected = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(), request.body, hashlib.sha256
    ).hexdigest()

    if not hmac.compare_digest(expected, sig):
        return HttpResponse(status=400)

    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return HttpResponse(status=400)

    if payload.get('event') == 'payment.failed':
        pid = payload['payload']['payment']['entity']['id']
        Payment.objects.filter(razorpay_payment_id=pid).update(status=Payment.Status.FAILED)

    return HttpResponse(status=200)


def _create_free_ticket(request, event):
    ticket = Ticket.objects.create(
        event=event,
        attendee=request.user,
        ticket_code=f'TKT-{uuid.uuid4().hex[:8].upper()}',
        status='confirmed',
        amount_paid=0,
        created_by=request.user,
    )
    try:
        from apps.media.utils import generate_ticket_qr
        generate_ticket_qr(ticket)
    except Exception:
        pass
    try:
        from apps.core.email.mailer import Mailer
        Mailer.send_ticket_confirmation(ticket)
    except Exception:
        pass
    messages.success(request, f'Registered! Ticket: {ticket.ticket_code}')
    return redirect('web_tickets:ticket_detail', ticket_id=ticket.pk)
