from django.urls import path
from .views import UserView, CreateUserView, LoginUserView, AccountView, DeleteUserView, TransferMoneyView, TransactionDetailsView, UpdateUserDetailsView, UpdateAccountPinView
from .views import book

urlpatterns = [
    path("book", book),
    path("registration", CreateUserView.as_view()),
    path("login", LoginUserView.as_view()),
    path("viewuserprofiles", AccountView.as_view()),
    path('internaluser/deleteaccount/<int:pk>/', DeleteUserView.as_view()),
    path("externaluser/transferfunds", TransferMoneyView.as_view()),
    path("externaluser/transactionhistory", TransactionDetailsView.as_view()),
    path("externaluser/updateprofile/<int:pk>", UpdateUserDetailsView.as_view()),
    path("externaluser/setaccountpin/<int:account_number>", UpdateAccountPinView.as_view()),
]