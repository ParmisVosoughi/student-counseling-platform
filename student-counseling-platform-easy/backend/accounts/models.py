from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN='ADMIN','Administrator'
        SUPERVISOR='SUPERVISOR','Supervisor'
        ADVISOR='ADVISOR','Advisor'
    role=models.CharField(max_length=20,choices=Role.choices,default=Role.ADVISOR,db_index=True)
    email=models.EmailField(unique=True)
    updated_at=models.DateTimeField(auto_now=True)
    REQUIRED_FIELDS=['email']
    def save(self,*args,**kwargs):
        if self.is_superuser: self.role=self.Role.ADMIN
        super().save(*args,**kwargs)
    def __str__(self): return f'{self.get_full_name() or self.username} ({self.role})'

class SupervisorProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='supervisor_profile',limit_choices_to={'role':User.Role.SUPERVISOR})
    phone=models.CharField(max_length=30,blank=True)
    notes=models.TextField(blank=True)
    def __str__(self): return self.user.get_full_name() or self.user.username

class AdvisorProfile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE,related_name='advisor_profile',limit_choices_to={'role':User.Role.ADVISOR})
    supervisor=models.ForeignKey(User,on_delete=models.PROTECT,related_name='supervised_advisors',limit_choices_to={'role':User.Role.SUPERVISOR})
    phone=models.CharField(max_length=30,blank=True)
    specialty=models.CharField(max_length=120,blank=True)
    notes=models.TextField(blank=True)
    def __str__(self): return self.user.get_full_name() or self.user.username
