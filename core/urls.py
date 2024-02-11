from django.urls import path
from . import views

urlpatterns = [
    path("login/", views.loginPage, name="login"),
    path("register/", views.registerUser, name="register"),
    path("", views.home, name="home"),
    path("room/<int:roomId>/", views.room, name="room"),
    path("profile/<int:Id>/", views.userProfile, name="profile"),
    path("create-room/", views.createRoom, name="create-room"),
    path("update-room/<int:roomId>/", views.updateRoom, name="update-room"),
    path("delete-room/<int:Id>/", views.deleteRoom, name="delete-room"),
    path("logout/", views.userLogout, name="logout"),
        path("delete-message/<int:Id>/", views.deleteMessage, name="delete-message"),

]
