from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User,SupervisorProfile,AdvisorProfile
@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets=UserAdmin.fieldsets+(('نقش',{'fields':('role',)}),)
    list_display=('username','email','role','is_active','is_staff')
admin.site.register(SupervisorProfile); admin.site.register(AdvisorProfile)
