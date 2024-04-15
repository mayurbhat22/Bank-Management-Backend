from django.urls import path
from .views import CreateUserView, LoginView, GetUsersView, LogoutView, CheckAuthenticatedView, UpdateTransactionDetailsView, AccountView, DeleteUserView, GetCSRFToken, TransferMoneyView, TransactionDetailsView, UpdateUserDetailsView, UpdateAccountPinView, GetIsAccountPinSetView
from django.urls import path


urlpatterns = [
    path("registration", CreateUserView.as_view()),
    path("login", LoginView.as_view()),
    path("viewuserprofiles", AccountView.as_view()),
    path("viewalluserprofiles", GetUsersView.as_view()),
    path("authenticated", CheckAuthenticatedView.as_view()),
    path('internaluser/deleteaccount/<int:pk>/', DeleteUserView.as_view()),
    path('internaluser/authorizetransaction/<int:pk>', UpdateTransactionDetailsView.as_view()),
    path("externaluser/transferfunds", TransferMoneyView.as_view()),
    path("externaluser/transactionhistory", TransactionDetailsView.as_view()),
    path("externaluser/updateprofile", UpdateUserDetailsView.as_view()),
    path("externaluser/setaccountpin", UpdateAccountPinView.as_view()),
    path("externaluser/viewaccountpin", GetIsAccountPinSetView.as_view()),
    path('csrf_cookie', GetCSRFToken.as_view()),
    path('logout', LogoutView.as_view()),
]