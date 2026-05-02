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

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            name    = form.cleaned_data['name']
            email   = form.cleaned_data['email']
            subject = form.cleaned_data.get('subject') or 'New contact form submission'
            message = form.cleaned_data['message']

            ContactSubmission.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message,
            )

            try:
                send_mail(
                    subject=f"[HzorTech] {subject}",
                    message=f"From: {name} <{email}>\n\n{message}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.CONTACT_EMAIL],
                    fail_silently=False,
                )
                messages.success(request, "Message sent — we'll be back within 48 hours.")
            except Exception:
                messages.success(request, "Message received — we'll be back within 48 hours.")
            return redirect('contact')
    else:
        form = ContactForm()
    return render(request, "business_page/contact.html", {"form": form})
