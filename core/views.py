from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db.models import Q
from .models import Room, Topic, Message
from .forms import RoomForm
from django.contrib import messages


# Create your views here.


def loginPage(request):
    page = "login"

    if request.user.is_authenticated:
        return redirect("home")

    if request.method == "POST":
        username = request.POST.get("username").lower()
        password = request.POST.get("password")

        try:
            user = User.objects.get(username=username)
        except:
            messages.error(request, "User dosenot exists")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("home")

        else:
            messages.error(request, "Username Or Password Incorrect!")
    context = {"page": page}
    return render(request, "core/login_register.html", context)


def home(request):
    query = request.GET.get("q") if request.GET.get("q") is not None else ""
    print(query)
    rooms = Room.objects.filter(
        Q(topic__name__icontains=query)
        | Q(name__icontains=query)
        | Q(description__icontains=query)
    )
    room_count = rooms.count()
    topics = Topic.objects.all()
    room_message = Message.objects.filter(
        Q(room__topic__name__icontains=query)
    ).order_by("-created")
    context = {
        "rooms": rooms,
        "topics": topics,
        "room_count": room_count,
        "room_message": room_message,
    }
    return render(request, "core/home.html", context)


def room(request, roomId):
    room = Room.objects.get(id=roomId)
    roomMessages = room.message_set.all().order_by("-created")
    participants = room.participants.all()

    if request.method == "POST":
        message = Message.objects.create(
            user=request.user, room=room, body=request.POST.get("body")
        )
        room.participants.add(request.user)
        return redirect("room", roomId=room.id)
    return render(
        request,
        "core/room.html",
        {"room": room, "roomMessages": roomMessages, "participants": participants},
    )


def userProfile(request, Id):
    user = User.objects.get(id=Id)

    rooms = user.room_set.all()
    room_message = user.message_set.all()
    topics = Topic.objects.all()
    context = {
        "user": user,
        "rooms": rooms,
        "room_message": room_message,
        "topics": topics,
    }

    return render(request, "core/profile.html", context)


@login_required(login_url="login")
def createRoom(request):
    form = RoomForm()

    if request.method == "POST":
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect("home")

    context = {"form": form}
    return render(request, "core/room_form.html", context)


@login_required(login_url="login")
def updateRoom(request, roomId):
    room = Room.objects.get(id=roomId)
    form = RoomForm(instance=room)
    if request.user != room.host:
        return HttpResponse("Action not allowed!")

    if request.method == "POST":
        form = RoomForm(request.POST, instance=room)
        if form.is_valid:
            form.save()
            return redirect("home")

    context = {"form": form}
    return render(request, "core/room_form.html", context)


@login_required(login_url="login")
def deleteRoom(request, Id):
    room = Room.objects.get(id=Id)

    if request.user != room.host:
        return HttpResponse("Action not allowed!")

    if request.method == "POST":
        room.delete()
        return redirect("home")
    return render(request, "core/delete.html", {"obj": room})


def userLogout(request):
    logout(request)
    return redirect("home")


def registerUser(request):
    form = UserCreationForm()
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect("home")
        else:
            messages.error(request, "An error occurred during registration!")

    context = {"form": form}
    return render(request, "core/login_register.html", context)


@login_required(login_url="login")
def deleteMessage(request, Id):
    message = Message.objects.get(id=Id)

    if request.user != message.user:
        return HttpResponse("Action not allowed!")

    if request.method == "POST":
        message.delete()
        return redirect("home")
    return render(request, "core/delete.html", {"obj": message})
