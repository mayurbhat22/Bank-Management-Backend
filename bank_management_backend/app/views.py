from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from django.http import Http404
from .models import User, Account, TransactionDetails
from .serializers import UserSerializer, CreateUserSerializer, LoginUserSerializer, UserLoginSerializer, CreateAccountSerializer, TransferMoneySerializer, UpdateAccountPinSerializer
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth import authenticate, login
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.hashers import make_password, check_password
# Create your views here.

class UserView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer 


class CreateUserView(APIView):
    print("CreateUserView")
    serializer_create_class = CreateUserSerializer
    serializer_account_class = CreateAccountSerializer
    def post(self, request):
        print(request.data)
        serializer_create = self.serializer_create_class(data=request.data)
        if serializer_create.is_valid():
            print("Validated", serializer_create.validated_data)
            user = User(
                name=serializer_create.validated_data["name"],
                user_name=serializer_create.validated_data["user_name"],
                email=serializer_create.validated_data["email"],
                password=make_password(serializer_create.validated_data["password"]),
                user_type=serializer_create.validated_data["user_type"],
                user_role=serializer_create.validated_data["user_role"]
            )
            user.save()
            print("User saved")
            print("User_Data", UserSerializer(user).data)
            serializer_account = self.serializer_account_class(data={"user": user.user_id, "account_type": "Savings", "balance": 100})
            if serializer_account.is_valid():
                account = serializer_account.save()
                print("Account saved")
                print("Account_Data", CreateAccountSerializer(account).data)
            else:
                print("Invalid Account data", serializer_account.errors)
                return Response(status=status.HTTP_400_BAD_REQUEST, data={"data": serializer_account.errors})
            
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        print("Invalid data", serializer_create.errors)
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"data": serializer_create.errors})

class LoginUserView(APIView):
    serializer_class = LoginUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data['user_name']
            password = serializer.validated_data['password']
            user_type = serializer.validated_data['user_type']
            user_role = serializer.validated_data['user_role']

            try:
                user = User.objects.get(user_name=username)
                
                if user and check_password(password, user.password) and user.user_type == user_type and user.user_role == user_role:
                    refresh = RefreshToken.for_user(user)
                    access_token = refresh.access_token

                    response_data = {
                        "message": "Login successful.",
                        "refresh": str(refresh),
                        "access": str(access_token),
                        "user_details": UserSerializer(user).data
                    }
                    return Response(response_data, status=status.HTTP_200_OK)
                else:
                    return Response({"detail": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)
            except User.DoesNotExist:
                return Response({"detail": "Invalid username or password."}, status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class AccountView(generics.ListCreateAPIView):
    queryset = User.objects.prefetch_related('account').all() 
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DeleteUserView(generics.DestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

class TransferMoneyView(APIView):
    serializer_class = TransferMoneySerializer

    def post(self, request):
        from_user_id = int(request.data["from_user"])
        from_account_number = request.data["from_account"]
        to_account_number = request.data["to_account"]
        from_account_pin = request.data["account_pin"]
        to_user_querySet = Account.objects.filter(account_number=to_account_number).first()

        to_user_id = 0
        if to_user_querySet:
            to_user_id = to_user_querySet.user_id
        if from_user_id == to_user_id:
            return Response({"message": "Cannot transfer funds to the same account"}, status=status.HTTP_400_BAD_REQUEST)

        from_account_querySet = Account.objects.filter(account_number=from_account_number).first()
        from_account_id = 0
        if from_account_querySet:
            from_account_id = from_account_querySet.account_id
            if from_account_querySet.account_pin != from_account_pin:
                return Response({"message": "Invalid account pin"}, status=status.HTTP_400_BAD_REQUEST)

        to_account_querySet = Account.objects.filter(account_number=to_account_number).first()
        to_account_id = 0
        if to_account_querySet:
            to_account_id = to_account_querySet.account_id
        amount = request.data["amount"]

        serializer = self.serializer_class(data={"from_user_id": from_user_id, "from_account_id": from_account_id, 
                                                 "to_account_id": to_account_id, "to_user_id": to_user_id, "from_account_number": from_account_number, 
                                                 "to_account_number": to_account_number, "amount": amount, "transaction_type": "transfer"})
        if serializer.is_valid():
            # If validation passes, retrieve the user.
            print("Validated", serializer.validated_data)

            if from_account_querySet.balance < int(amount):
                return Response({"message": "Insufficient balance"}, status=status.HTTP_400_BAD_REQUEST)
            serializer.save()
            # Update balance
            from_account_querySet.balance = from_account_querySet.balance - int(amount)
            from_account_querySet.save()
            to_account_querySet.balance = to_account_querySet.balance + int(amount)
            to_account_querySet.save()
            print("Transaction saved")
            return Response({"message": "Transaction successful"}, status=status.HTTP_200_OK)
        else:
            print("Invalid dataaa", serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        pass

class TransactionDetailsView(generics.ListCreateAPIView):
    queryset = TransactionDetails.objects.all()
    serializer_class = TransferMoneySerializer

    # Filter transaction related to from-user
    def list(self, request, *args, **kwargs):
        from_user_id = request.query_params.get('from_user_id', None)
        if from_user_id is not None:
            queryset = TransactionDetails.objects.filter(from_user_id=from_user_id)
            serializer = self.get_serializer(queryset, many=True)
            data = []
            for transaction in serializer.data:
                data.append(transaction)
            queryset = TransactionDetails.objects.filter(to_user_id=from_user_id)
            serializer = self.get_serializer(queryset, many=True)
            for transaction in serializer.data:
                data.append(transaction)
            return Response(data, status=status.HTTP_200_OK)
        else:
            queryset = self.get_queryset()
            serializer = self.get_serializer(queryset, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

class UpdateUserDetailsView(generics.UpdateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def update(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
class UpdateAccountPinView(generics.UpdateAPIView):
    serializer_class = UpdateAccountPinSerializer

    def get_object(self):
        account_number = self.kwargs.get("account_number")
        try:
            return Account.objects.get(account_number=account_number)
        except Account.DoesNotExist:
            # You can customize the response as needed
            raise Http404("No Account matches the given query.")

    def update(self, request, *args, **kwargs):
        try:
            return super(UpdateAccountPinView, self).update(request, *args, **kwargs)
        except Http404 as e:
            # Custom error handling for not found account
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)
        

class GetAccountPinIsSetView(APIView):
    def get(self, request, *args, **kwargs):
        account_number = self.kwargs.get("account_number")
        account = Account.objects.filter(account_number=account_number).first()
        if account:
            if account.account_pin == "0":
                return Response({"message": "Account pin is not set"}, status=status.HTTP_200_OK)
            else:
                return Response({"message": "Account pin is set"}, status=status.HTTP_200_OK)
        else:
            return Response({"message": "Account not found"}, status=status.HTTP_404_NOT_FOUND)
           
