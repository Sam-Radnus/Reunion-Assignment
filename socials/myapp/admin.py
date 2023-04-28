from django.contrib import admin
from .models import User,UserFollowing
# Register your models here.
admin.site.register(User)
admin.site.register(UserFollowing)