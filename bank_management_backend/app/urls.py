from django.urls import path
from .views import UserView, CreateUserView, LoginUserView
from .views import book

urlpatterns = [
    path("book", book),
    path("registration", CreateUserView.as_view()),
    path("login", LoginUserView.as_view()),
]