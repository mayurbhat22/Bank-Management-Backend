from django.db import models

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