from django.urls import path
from .views import UserView, CreateUserView, LoginUserView, AccountView, DeleteUserView
from .views import book

urlpatterns = [
    path("book", book),
    path("registration", CreateUserView.as_view()),
    path("login", LoginUserView.as_view()),
    path("internaluser/viewuserprofiles", AccountView.as_view()),
    path('internaluser/deleteaccount/<int:pk>/', DeleteUserView.as_view()),
]