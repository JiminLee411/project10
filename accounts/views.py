from django.shortcuts import render, redirect, get_object_or_404
from .forms import CustomUserCreationForm, CustomUserChangeForm

# Create your views here.
def signup(request):
    form = CustomUserCreationForm
    context = {
        'form': form
    }
    return render(request, 'accounts/form.html', context)

def login(request):
    pass

def logout(request):
    pass