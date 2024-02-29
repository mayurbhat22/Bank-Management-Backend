from rest_framework import serializers
from .models import User, Account, Transaction


class UserSerializer(serializers.ModelSerializer):
    account = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('user_id', 'name', 'user_name', 'email', 'user_type', 'user_role', 'created_at', 'account')

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


    
class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        print("CreateUserSerializer")
        model = User
        fields = ('name', 'user_name', 'email', 'password', 'user_type', 'user_role')
        # extra_kwargs = {'password': {'write_only': True}}

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
        fields = ('user', 'account_number', 'account_type', 'balance')

class LoginUserSerializer(serializers.Serializer):
        #Check if the user exists
        user_name = serializers.CharField()
        password = serializers.CharField()
        def validate(self, data):
            user = User.objects.filter(
                user_name=data["user_name"]
            )
            if not user.exists():
                raise serializers.ValidationError("User not founddd")
            #Check if ppassword is correct
            if user.first().password != data["password"]:
                raise serializers.ValidationError("Password is incorrect")
            return data
