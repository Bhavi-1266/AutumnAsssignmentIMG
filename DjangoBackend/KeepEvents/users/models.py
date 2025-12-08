from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.
class users(AbstractUser):
    userid = models.AutoField(primary_key=True)
    username = models.CharField(max_length=150, unique=True)
    enrollmentNo = models.IntegerField(unique=True, blank=True, default=0 )
    email = models.EmailField(unique=True, blank=True, default='')
    userProfile = models.ImageField(upload_to='user_profiles/', blank=True, default='' )
    userbio = models.TextField(blank=True, max_length=500 ,null=True)
    batch = models.IntegerField(blank=True, null=True)
    dept = models.CharField(max_length=100, blank=True)
    password = models.CharField(max_length=128)  # Store hashed passwords
    # roles = models.JSONField(default=list, blank=True)  # List of roles/permissions
    date_joined = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        ordering = ['username']
    
    def __str__(self):
        return self.username
