import requests as http_requests

from django.conf import settings
from django.contrib import messages
from django.core.mail import send_mail
from django.shortcuts import redirect, render

from .forms import ContactForm
from .models import ContactSubmission


def home(request):
    return render(request, 'business_page/home.html')

def about(request):
    return render(request, 'business_page/about.html')

def services(request):
    return render(request, 'business_page/services.html')

def projects(request):
    return render(request, 'business_page/projects.html')

def privacy(request):
    return render(request, 'business_page/privacy.html')

def custom_404(request, exception=None):
    return render(request, '404.html', status=404)


def _verify_turnstile(token, ip):
    """Verify Cloudflare Turnstile token server-side. Returns True if valid."""
    secret = settings.TURNSTILE_SECRET_KEY
    if not secret:
        return True  # Skip verification if key not configured
    try:
        resp = http_requests.post(
            'https://challenges.cloudflare.com/turnstile/v0/siteverify',
            data={'secret': secret, 'response': token, 'remoteip': ip},
            timeout=5,
        )
        return resp.json().get('success', False)
    except Exception:
        return True  # Fail open if Turnstile is unreachable


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Turnstile verification
            turnstile_token = request.POST.get('cf-turnstile-response', '')
            ip = request.META.get('HTTP_CF_CONNECTING_IP') or request.META.get('REMOTE_ADDR', '')
            if not _verify_turnstile(turnstile_token, ip):
                messages.error(request, "Security check failed. Please try again.")
                return render(request, 'business_page/contact.html', {'form': form})

            name    = form.cleaned_data['name']
            email   = form.cleaned_data['email']
            subject = form.cleaned_data.get('subject') or 'New contact form submission'
            message = form.cleaned_data['message']

            ContactSubmission.objects.create(
                name=name, email=email, subject=subject, message=message,
            )

            try:
                send_mail(
                    subject=f"[HZORTECH] {subject}",
                    message=f"From: {name} <{email}>\n\n{message}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.CONTACT_EMAIL],
                    fail_silently=False,
                )
                # Auto-reply to sender
                send_mail(
                    subject="HZORTECH — Message Received",
                    message=(
                        f"Hello {name},\n\n"
                        "Thank you for reaching out to HZORTECH. "
                        "We have received your message and will respond within 48 hours "
                        "with a direct assessment.\n\n"
                        "— The HZORTECH Team\n"
                        "shara@hzortech.com | hzortech.com"
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=True,
                )
                messages.success(request, "sent")
            except Exception:
                messages.success(request, "received")
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, 'business_page/contact.html', {
        'form': form,
        'turnstile_site_key': settings.TURNSTILE_SITE_KEY,
    })
