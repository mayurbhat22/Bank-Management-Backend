from django.shortcuts import render
from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.decorators import api_view
from .models import User
from .serializers import UserSerializer, CreateUserSerializer, LoginUserSerializer
# Create your views here.

class UserView(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer 


class CreateUserView(APIView):
    print("CreateUserView")
    serializer_class = CreateUserSerializer

    def post(self, request):
        print(request.data)
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            print("Validated", serializer.validated_data)
            user = User(
                name=serializer.validated_data["name"],
                user_name=serializer.validated_data["user_name"],
                email=serializer.validated_data["email"],
                password=serializer.validated_data["password"],
                user_type=serializer.validated_data["user_type"],
                user_role=serializer.validated_data["user_role"]
            )
            user.save()
            print("User saved")
            print("User_Data", UserSerializer(user).data)
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
        print("Invalid data", serializer.errors)
        return Response(status=status.HTTP_400_BAD_REQUEST, data={"data": serializer.errors})

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
        
# This will return a list of books
@api_view(["GET"])
def book(request):
    books = ["Pro Python", "Fluent Python", "Speaking javascript", "The Go programming language"]
    return Response(status=status.HTTP_200_OK, data={"data": books})