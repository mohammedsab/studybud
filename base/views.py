from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm

from .models import Room, Topic, Message
from .forms import RoomForm, LoginForm


# Create your views here.

# def loginPage(request):
#     if request.method == 'POST':
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             cd = form.cleaned_data
#             # print(cd)
#             user = authenticate(request, username= cd['user'], password=cd['password'])
#             if user is not None:
#                 if user.is_active:
#                     login(request, user)
#                     return redirect('home')
#                 else:
#                     messages.error(request, 'Disabled account')
#                     # return HttpResponse('Disabled account')
#             else:
#                 messages.error(request, 'Invalid username or password')
#                 # return HttpResponse('Invalid username or password')
#     else:
#         form = LoginForm()
#     return render(request, 'base/login_register.html',{'form':form})

def loginPage(request):
    page = 'login'
    
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST.get('username').lower()
        password = request.POST.get('password')
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            messages.error(request,'User does not exist')
            
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request,'Username OR Password mismatch')
            
    context = {'page': page}
    return render(request, 'base/login_register.html', context)

def registerPage(request):
    form = UserCreationForm()
    context = {'form': form}
    
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
        
        messages.success(request, 'Account created successfully')
        login(request, user)
        return redirect('home')
    
    else:
        messages.error(request, 'An error occurred during registration')
        
    return render(request, 'base/login_register.html', context)

def logoutUser(request):
    logout(request)
    return redirect('home')

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''   
    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
        )
    
    room_count = rooms.count()
    topics = Topic.objects.all()
    messages = Message.objects.filter(Q(room__topic__name__icontains=q))
        
    context = {'rooms': rooms, 'topics': topics, 'room_count': room_count,
               'recent_messages': messages}
    return render(request, 'base/home.html', context)

def room(request, pk):
    room = Room.objects.get(pk=pk)
    room_messages = room.message_set.all().order_by('-created')
    participants = room.participants.all()
    print(participants)
    
    if request.method == 'POST':
        message = Message.objects.create(
            user = request.user,
            room = room,
            body = request.POST.get('body'),
        )
        room.participants.add(request.user)
        return redirect('room', pk = room.pk)
    
    context = {'room': room, 'room_messages': room_messages, 'participants': participants}
    return render(request, 'base/room.html', context)

@login_required(login_url='login')
def createRoom(request):
    
    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('home')
    
    form = RoomForm()
    context = {'form' : form}
    return render(request, 'base/room_form.html', context)
    

@login_required(login_url='login')
def updateRoom(request, pk):
    
    room = Room.objects.get(pk=pk)
    if request.user != room.host:
        return HttpResponse('Not allowed to update')
    form = RoomForm(instance=room)
    
    if request.POST:
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
        return redirect('home')
    
    context = {'form': form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(pk=pk)
    if request.user != room.host:
        return HttpResponse('Not allowed to delete a room')
    if request.method == 'POST':
        room.delete()
        return redirect('home')
    return render(request, 'base/delete.html',{'obj':room.name})


@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(pk=pk)
    if request.user != message.user:
        return HttpResponse('Not allowed to delete a room')
    if request.method == 'POST':
        message.delete()
        return redirect('home')
    return render(request, 'base/delete.html',{'obj':message.body})