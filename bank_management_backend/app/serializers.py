from rest_framework import serializers
from .models import User, Account, TransactionDetails
from django.contrib.auth.hashers import make_password, check_password

class UserSerializer(serializers.ModelSerializer):
    account = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('user_id', 'name', 'user_name', 'email', 'user_type', 'user_role', 'created_at', 'account', 'password')
        extra_kwargs = {
            'password': {'write_only': True}  
        }
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
    
    def update(self, instance, validated_data):
        # Check if 'password' is being updated and hash it before setting
        password = validated_data.pop('password', None)
        if password:
            instance.password = make_password(password)

        instance.save()
        return instance

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        print("CreateUserSerializer")
        model = User
        fields = ('name', 'user_name', 'email', 'password', 'user_type', 'user_role')
        extra_kwargs = {'password': {'write_only': True}}

    def validate(slf, data):
        # Check if the email is unique
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email already exists")
        # Check if the user_name is unique
        if User.objects.filter(user_name=data['user_name']).exists():
            raise serializers.ValidationError("Username already exists")
        return data

class CreateAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
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
        model = Account
        fields = ('account_pin',)
        extra_kwargs = {
            'account_pin': {'write_only': True}
        }
    
class LoginUserSerializer(serializers.Serializer):
        # Check if the user exists
        user_name = serializers.CharField()
        password = serializers.CharField()
        def validate(self, data):
            user = User.objects.filter(
                user_name=data["user_name"]
            )
            if not user.exists():
                raise serializers.ValidationError("User not founddd")
            #Check if ppassword is correct
            # if data["password"] != user.first().password:
            #     raise serializers.ValidationError("Password is incorrect")
            if not check_password(data["password"], user.first().password):
                raise serializers.ValidationError("Password is incorrect")
            return data

class TransferMoneySerializer(serializers.ModelSerializer):
    class Meta:
        model = TransactionDetails
        fields = ('transaction_id', 'from_account_id', 'to_account_id', 'from_user_id', 'to_user_id', 'from_account_number', 'to_account_number', 'amount', 'created_at', 'updated_at', 'transaction_type')
