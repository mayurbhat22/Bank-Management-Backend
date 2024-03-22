from django.db import models
import random

# Create your models here.

class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100, null=False, blank=False)
    user_name = models.CharField(max_length=100, null=False, blank=False, unique=True)
    email = models.EmailField(max_length=100, null=False, blank=False, unique=True)
    password = models.CharField(max_length=100, null=False, blank=False)
    user_type = models.CharField(max_length=100,blank=False)
    user_role = models.CharField(max_length=100,blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

def generate_account_number():
    while True:
        account_number =  str(random.randint(100000, 999999))
        if not Account.objects.filter(account_number=account_number).exists():
            return account_number
        
class Account(models.Model):
    account_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='account')
    account_number = models.CharField(max_length=6, null=False, blank=False, unique=True, default=generate_account_number)
    account_type = models.CharField(max_length=100, null=False, blank=False)
    balance = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    account_pin = models.CharField(max_length=6, null=False, blank=False, default=000000)

    def __str__(self):
        return self.account_number



class TransactionDetails(models.Model):
    transaction_id = models.AutoField(primary_key=True)
    from_account_id = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='from_account')
    to_account_id = models.ForeignKey(Account, on_delete=models.CASCADE, related_name='to_account')
    from_user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='from_user')
    to_user_id = models.ForeignKey(User, on_delete=models.CASCADE, related_name='to_user')
    from_account_number = models.CharField(max_length=6, null=False, blank=False)
    to_account_number = models.CharField(max_length=6, null=False, blank=False)
    transaction_type = models.CharField(max_length=100, null=False, blank=False, default='transfer')
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=False, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True) 


