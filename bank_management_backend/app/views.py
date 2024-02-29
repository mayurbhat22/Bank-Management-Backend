from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from .models import User
from .serializers import UserSerializer, CreateUserSerializer, LoginUserSerializer, CreateAccountSerializer
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
                password=serializer_create.validated_data["password"],
                user_type=serializer_create.validated_data["user_type"],
                user_role=serializer_create.validated_data["user_role"]
            )
            user.save()
            print("User saved")
            print("User_Data", UserSerializer(user).data)
            serializer_account = self.serializer_account_class(data={"user": user.user_id, "account_type": "Savings", "balance": 0})
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
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            # If validation passes, retrieve the user.
            user = User.objects.get(user_name=serializer.validated_data["user_name"])
            user_role = user.user_role
            # Implement session login logic.
            
            return Response({"message": "Login successful"}, status=status.HTTP_200_OK)
        else:
            print("Invalid data", serializer.errors)
            # If validation fails, return the error messages.
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)  

class AccountView(generics.ListCreateAPIView):
    queryset = User.objects.prefetch_related('account').all() 
    serializer_class = UserSerializer

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class DeleteUserView(generics.DestroyAPIView):
    print("DeleteUserView")
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        print("Destroying", instance)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)

# This will return a list of books
@api_view(["GET"])
def book(request):
    books = ["Pro Python", "Fluent Python", "Speaking javascript", "The Go programming language"]
    return Response(status=status.HTTP_200_OK, data={"data": books})