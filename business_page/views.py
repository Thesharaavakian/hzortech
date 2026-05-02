from urllib import request

from django.shortcuts import render
from .forms import ContactForm

# Create your views here.

def home(request):
    return render(request, 'business_page/home.html')

def about(request):
    return render(request, 'business_page/about.html')

def services(request):
    return render(request, 'business_page/services.html')

def contact(request):
    form = ContactForm()
    return render(request, "business_page/contact.html", {"form": form})
