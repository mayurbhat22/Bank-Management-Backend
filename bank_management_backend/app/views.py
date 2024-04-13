from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.http import Http404
from .models import Account, TransactionDetails, UserProfile, AccountModel, TransactionDetailsModel
from .serializers import UserSerializer, UserProfileSerializer, CreateUserSerializer, LoginUserSerializer, UserDetailsSerializer, UserLoginSerializer, CreateAccountSerializer, TransferMoneySerializer, UpdateAccountPinSerializer
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password, check_password
from decimal import Decimal
from django.contrib.auth.models import User
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from rest_framework import permissions
# Create your views here.

@method_decorator(ensure_csrf_cookie, name='dispatch')
class GetCSRFToken(APIView):
    permission_classes = (permissions.AllowAny, )
    def get(self, request, format=None):
        return Response({ 'success': 'CSRF cookie set' })
    
@method_decorator(csrf_protect, name='dispatch')
class LoginView(APIView):
    permission_classes = (permissions.AllowAny, )
    serializer_class = LoginUserSerializer
    def post(self, request, format=None):
        serializer = self.serializer_class(data=request.data)
        data = self.request.data
        password = data['password']

        if serializer.is_valid():
            username = serializer.validated_data['user_name']
            user_type = serializer.validated_data['user_type']
            user_role = serializer.validated_data['user_role']
            try:
                user = authenticate(request, username=username, password=password)
                user_profile = UserProfile.objects.get(user=user)
                if user_profile.user_type == user_type and user_profile.user_role == user_role:
                    login(request, user)
                    response_data = {
                        "message": "Login successful.",
                        "user_details": UserProfileSerializer(user_profile).data
                    }
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    return Response({"detail": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)
            except:
                return Response({ 'error': 'Something went wrong when logging in' })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_protect, name='dispatch') 
class LogoutView(APIView):
    def post(self, request, format=None):
        try:
            logout(request)
            return Response({ 'success': 'Loggout Out' })
        except:
            return Response({ 'error': 'Something went wrong when logging out' })

@method_decorator(csrf_protect, name='dispatch')       
class CreateUserView(APIView):
    permission_classes = (permissions.AllowAny, )
    serializer_create_class = CreateUserSerializer
    serializer_account_class = CreateAccountSerializer
    def post(self, request):
        print(request.data)
        serializer_create = self.serializer_create_class(data=request.data)
        data = self.request.data
        password = data['password']
        if serializer_create.is_valid():
            user = User.objects.create_user(username=serializer_create.validated_data["user_name"], password=password)
            user = User.objects.get(id=user.id)

            user_profile = UserProfile.objects.create(user=user, name=serializer_create.validated_data["name"],
                user_name=serializer_create.validated_data["user_name"],
                email=serializer_create.validated_data["email"],
                user_type=serializer_create.validated_data["user_type"],
                user_role=serializer_create.validated_data["user_role"])
            
            user_profile.save()
            serializer_account = self.serializer_account_class(data={"user": user_profile.id, "account_type": "Savings", "balance": 100})
            if serializer_account.is_valid():
                account = serializer_account.save()
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"data": serializer_account.errors})
            
            return Response(UserProfileSerializer(user_profile).data, status=status.HTTP_201_CREATED)
        print("Invalid data", serializer_create.errors)
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"data": serializer_create.errors})
    
@method_decorator(csrf_protect, name='dispatch')   
class AccountView(generics.ListCreateAPIView):
    permission_classes = (permissions.AllowAny, )
    def get(self, request, format=None):
        try:
            user = self.request.user
            username = user.username

            user_profile = UserProfile.objects.get(user=user)
            user_profile = UserProfileSerializer(user_profile)

            return Response({ 'profile': user_profile.data, 'username': str(username) })
        except:
            return Response({ 'error': 'Something went wrong when retrieving profile' })

@method_decorator(csrf_protect, name='dispatch')   
class GetUsersView(generics.ListCreateAPIView):
    permission_classes = (permissions.AllowAny, )
    def get(self, request, format=None):
        try:
            user_profile = UserProfile.objects.all()
            print("User Profile", user_profile)
            user_profiles = UserProfileSerializer(user_profile, many=True)

            return Response({ 'profile': user_profiles.data})
        except:
            return Response({ 'error': 'Something went wrong when retrieving profile' })
    
class DeleteUserView(generics.DestroyAPIView):
    queryset = User.objects.all()  
    serializer_class = UserProfileSerializer  

    def get_object(self):
        user_profile_id = self.kwargs.get('pk')
        user_profile = get_object_or_404(UserProfile, pk=user_profile_id)
        return user_profile.user

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            self.perform_destroy(instance)
            return Response({'success': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'error': f'Something went wrong when trying to delete user: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
    

@method_decorator(csrf_protect, name='dispatch') 
class TransferMoneyView(APIView):
    permission_classes = (permissions.AllowAny, )
    serializer_class = TransferMoneySerializer

    def post(self, request):
        user = self.request.user

        username = user.username
        user_profile = UserProfile.objects.get(user=user)
        account = AccountModel.objects.filter(user=user_profile).first()

        from_user_id = user_profile.id
        from_account_number = account.account_number
        to_account_number = request.data["to_account"]
        from_account_pin = request.data["account_pin"]
        isAuthoriseRequired = request.data["isAuthoriseRequired"]

        to_user_querySet = AccountModel.objects.filter(account_number=to_account_number).first()

        to_user_id = 0
        if to_user_querySet:
            to_user_id = to_user_querySet.user_id
        if from_user_id == to_user_id:
            return Response({"message": "Cannot transfer funds to the same account"}, status=status.HTTP_400_BAD_REQUEST)

        from_account_querySet = AccountModel.objects.filter(account_number=from_account_number).first()
        from_account_id = 0
        if from_account_querySet:
            from_account_id = from_account_querySet.account_id
            if from_account_querySet.account_pin != from_account_pin:
                return Response({"message": "Invalid account pin"}, status=status.HTTP_400_BAD_REQUEST)

        to_account_querySet = AccountModel.objects.filter(account_number=to_account_number).first()
        to_account_id = 0
        if to_account_querySet:
            to_account_id = to_account_querySet.account_id
        amount = request.data["amount"]

        serializer = self.serializer_class(data={"from_user_id": from_user_id, "from_account_id": from_account_id, 
                                                 "to_account_id": to_account_id, "to_user_id": to_user_id, "from_account_number": from_account_number, 
                                                 "to_account_number": to_account_number, "amount": amount, "transaction_type": "transfer", "isAuthoriseRequired" : isAuthoriseRequired})
        if serializer.is_valid():
            if from_account_querySet.balance < int(amount):
                return Response({"message": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()

            # Update balance
            if not isAuthoriseRequired:
                from_account_querySet.balance = from_account_querySet.balance - int(amount)
                from_account_querySet.save()
                to_account_querySet.balance = to_account_querySet.balance + int(amount)
                to_account_querySet.save()
            return Response({"message": "Transaction successful"}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        pass

@method_decorator(csrf_protect, name='dispatch') 
class TransactionDetailsView(generics.ListCreateAPIView):
    permissions_classes = (permissions.AllowAny, )
    queryset = TransactionDetails.objects.all()
    serializer_class = TransferMoneySerializer

    def list(self, request, *args, **kwargs):
        user = self.request.user

        username = user.username
        user_profile = UserProfile.objects.get(user=user)
        account = AccountModel.objects.filter(user=user_profile).first()
        if user_profile.user_type == "Internal" and user_profile.user_role == "System Admin":
            isSystemAdmin = True
        else:
            isSystemAdmin = False
        if not isSystemAdmin:
            
            from_user_id = user_profile.id
            if from_user_id is not None:
                queryset = TransactionDetailsModel.objects.filter(from_user_id=from_user_id)
                serializer = self.get_serializer(queryset, many=True)
                data = []
                for transaction in serializer.data:
                    if not transaction["isAuthoriseRequired"]:
                        data.append(transaction)
                queryset = TransactionDetailsModel.objects.filter(to_user_id=from_user_id)
                serializer = self.get_serializer(queryset, many=True)
                for transaction in serializer.data:
                    if not transaction["isAuthoriseRequired"]:
                        data.append(transaction)
                return Response(data, status=status.HTTP_200_OK)
            else:
                queryset = self.get_queryset()
                serializer = self.get_serializer(queryset, many=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            queryset = TransactionDetailsModel.objects.all()
            serializer = self.get_serializer(queryset, many=True)
            data = []
            for transaction in serializer.data:
                if transaction["isAuthoriseRequired"]:
                    data.append(transaction)
            return Response(data, status=status.HTTP_200_OK)
        
@method_decorator(csrf_protect, name='dispatch') 
class UpdateUserDetailsView(generics.UpdateAPIView):
    print("UpdateUserDetailsView")
    permission_classes = (permissions.AllowAny,) 
    serializer_class = UserSerializer  

    def get_object(self):
        return self.request.user

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            updated_user = serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@method_decorator(csrf_protect, name='dispatch')    
class UpdateAccountPinView(generics.UpdateAPIView):
    permission_classes = (permissions.AllowAny, )
    serializer_class = UpdateAccountPinSerializer

    def get_object(self):
        user = self.request.user

        username = user.username
        user_profile = UserProfile.objects.get(user=user)
        account = AccountModel.objects.filter(user=user_profile).first()

        account_number = account.account_number
        try:
            return AccountModel.objects.get(account_number=account_number)
        except Account.DoesNotExist:
            raise Http404("No Account matches the given query.")

    def update(self, request, *args, **kwargs):
        try:
            return super(UpdateAccountPinView, self).update(request, *args, **kwargs)
        except Http404 as e:
            # Custom error handling for not found account
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        
@method_decorator(csrf_protect, name='dispatch')
class GetIsAccountPinSetView(APIView):
    def get(self, request, *args, **kwargs):
        user = self.request.user
        username = user.username
        user_profile = UserProfile.objects.get(user=user)
        account = AccountModel.objects.filter(user=user_profile).first()

        account_number = self.kwargs.get("account_number")
        if account:
            if account.account_pin == "0":
                return Response({"message": "Account pin is not set"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Account pin is set"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Account not found"}, status=status.HTTP_404_NOT_FOUND)

@method_decorator(csrf_protect, name='dispatch')           
class UpdateTransactionDetailsView(generics.UpdateAPIView):
    queryset = TransactionDetailsModel.objects.all()
    serializer_class = TransferMoneySerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()

            from_account_number = request.data["from_account_number"]
            to_account_number = request.data["to_account_number"]
            amount = request.data["amount"]
            from_account_querySet = AccountModel.objects.filter(account_number=from_account_number).first()
            from_account_id = 0
            if from_account_querySet:
                from_account_id = from_account_querySet.account_id

            to_account_querySet = AccountModel.objects.filter(account_number=to_account_number).first()
            to_account_id = 0
            if to_account_querySet:
                to_account_id = to_account_querySet.account_id
            
            from_account_querySet.balance = from_account_querySet.balance - Decimal(amount)
            from_account_querySet.save()
            to_account_querySet.balance = to_account_querySet.balance + Decimal(amount)
            to_account_querySet.save()
            
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

