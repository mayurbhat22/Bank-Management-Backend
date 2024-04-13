from rest_framework import serializers
from .models import Account, TransactionDetails, UserProfile, AccountModel, TransactionDetailsModel
from django.contrib.auth.hashers import make_password, check_password
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

# class UserSerializer(serializers.ModelSerializer):
#     account = serializers.SerializerMethodField()

#     class Meta:
#         model = User
#         fields = ('user_id', 'name', 'user_name', 'email', 'user_type', 'user_role', 'created_at', 'account', 'password')
#         extra_kwargs = {
#             'password': {'write_only': True}  
#         }
#     def get_account(self, obj):
#         account = obj.account.first()  
#         if account:
#             print("get_account", obj.account)
#             return {
#                 'account_number': account.account_number,
#                 'account_type': account.account_type,
#                 'balance': account.balance
#             }
#         return None
    
#     def update(self, instance, validated_data):
#         # Check if 'password' is being updated and hash it before setting
#         password = validated_data.pop('password', None)
#         if password:
#             instance.password = make_password(password)

#         instance.save()
#         return instance

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def update(self, instance, validated_data):
        print("instance", instance)
        password = validated_data.pop('password', None)
        print("password", password)
        if password:
            instance.set_password(password)
            instance.save() 
        return super(UserSerializer, self).update(instance, validated_data)
    
class UserProfileSerializer(serializers.ModelSerializer):
    account = serializers.SerializerMethodField()

    class Meta:
        model = UserProfile
        fields = ('id', 'user', 'name', 'user_name', 'email', 'user_type', 'user_role', 'created_at', 'account')
    def get_account(self, obj):
        account = obj.account.first()  
        if account:
            print("get_account", obj.account)
            return {
                'account_number': account.account_number,
                'account_type': account.account_type,
                'balance': account.balance
            }
        return None
    
    # def update(self, instance, validated_data):
    #     # Check if 'password' is being updated and hash it before setting
    #     password = validated_data.pop('password', None)
    #     if password:
    #         instance.password = make_password(password)

    #     instance.save()
    #     return instance

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        instance = super().update(instance, validated_data)

        if password:
            instance.set_password(password)
            instance.save()

        return instance
    

class UserDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ('name', 'user_name', 'email', 'user_type', 'user_role')


class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        print("CreateUserSerializer")
        model = UserProfile
        fields = ('name', 'user_name', 'email', 'user_type', 'user_role')

    def validate(slf, data):
        # Check if the email is unique
        if UserProfile.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email already exists")
        # Check if the user_name is unique
        if UserProfile.objects.filter(user_name=data['user_name']).exists():
            raise serializers.ValidationError("Username already exists")
        return data

class CreateAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountModel
        fields = ('user', 'account_number', 'account_type', 'balance', 'account_pin')
        extra_kwargs = {
            'account_number': {'write_only': True},
            'account_pin': {'write_only': True}
        }
    def upate(self, instance, validated_data):
        account_pin = validated_data.pop('account_pin', None)
        if account_pin:
            instance.account_pin = account_pin
       
        instance.save()
        return instance

class UpdateAccountPinSerializer(serializers.ModelSerializer):
    class Meta:
        model = AccountModel
        fields = ('account_pin',)
        extra_kwargs = {
            'account_pin': {'write_only': True}
        }
    
class LoginUserSerializer(serializers.Serializer):
        # Check if the user exists
        user_name = serializers.CharField()
        user_type = serializers.CharField()
        user_role = serializers.CharField()
        def validate(self, data):
            user = UserProfile.objects.filter(
                user_name=data["user_name"]
            )
            if not user.exists():
                raise serializers.ValidationError("User not found")
               
            if not data["user_type"] == user.first().user_type:
                raise serializers.ValidationError("User type is incorrect")
            
            if not data["user_role"] == user.first().user_role:
                raise serializers.ValidationError("User role is incorrect")
            
            return data

class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(username=data['username'], password=data['password'])
        if user and user.is_active:
            refresh = RefreshToken.for_user(user)
            return {
                'user_id': user.user_id,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        raise serializers.ValidationError("Incorrect Credentials")
    
class TransferMoneySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionDetailsModel
        fields = ('transaction_id', 'from_account_id', 'to_account_id', 'from_user_id', 'to_user_id', 'from_account_number', 
                  'to_account_number', 'amount', 'created_at', 'updated_at', 'transaction_type', 'isAuthoriseRequired')
    
    def update(self, instance, validated_data):
        instance.isAuthoriseRequired = False
        instance.save()
        return instance