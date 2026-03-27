from django.shortcuts import render, redirect, get_object_or_404
from .models import Note
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate 

@login_required
def home(request):
    query = request.GET.get('q')

    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')

        if title and content:
            Note.objects.create(user=request.user,title=title, content=content)

    notes = Note.objects.filter(user=request.user)

    if query:
        notes = notes.filter(
            Q(title__icontains=query) |
            Q(content__icontains=query)
        )
    notes = notes.order_by('-created_at')    

    return render(request, 'home.html', {'notes': notes})

@login_required
def delete_note(request, id):
    note = get_object_or_404(Note, id=id, user=request.user)
    note.delete()
    return redirect('/')

@login_required
def edit_note(request, id):
    note = get_object_or_404(Note, id=id, user=request.user)

    if request.method == "POST":
        title = request.POST.get('title')
        content = request.POST.get('content')

        if title and content:
            note.title = title
            note.content = content
            note.save()
            return redirect('/')

    return render(request, 'edit_note.html', {'note': note})

def signup(request):
    error = None
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if username and password:
            if User.objects.filter(username=username).exists():
                error = "Username already taken."
            else:
                user = User.objects.create_user(username=username, password=password)
                login(request, user)
                return redirect('/')  # success → redirect home
        else:
            error = "Please fill out all fields."

    return render(request, 'signup.html', {'error': error})

def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('/')
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials'})

    return render(request, 'login.html')

def logout_view(request):
    logout(request)
    return redirect('/login/')