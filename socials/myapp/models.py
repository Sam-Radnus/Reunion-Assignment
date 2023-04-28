from enum import unique
from django.db import models
from django.contrib.auth.models import AbstractUser

from django.contrib.auth.models import Group, Permission
class User(AbstractUser):
    username = models.CharField(db_index=True, max_length=255, null=True)
    email = models.EmailField(unique=True, null=True)
    password = models.CharField(max_length=255,null=True)
    groups = models.ManyToManyField(Group, related_name="myapp_users") 
    user_permissions = models.ManyToManyField(Permission, related_name="myapp_users_permissions")
   
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']
    
    def total_followers(self):
        return self.followers.count()

    def total_following(self):
        return self.following.count()    
    
    def __str__(self):
        return self.username
    

class Post(models.Model):
    name = models.CharField(db_index=True, max_length=255, null=True)  
    caption = models.CharField(blank=True, max_length=255, null=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)
    time_created = models.DateTimeField(auto_now_add=True, null=True)
    
    def __str__(self):
        return self.name
    
    def liked_by_users(self):
        return self.likes.all()
    
    def total_likes(self):
        return self.likes.count()
    
    
class UserFollowing(models.Model):
    user_id=models.ForeignKey("User",related_name="following",on_delete=models.CASCADE)
    following_user_id=models.ForeignKey("User",related_name="followers",on_delete=models.CASCADE)
    created=models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together=('user_id','following_user_id')

    def __str__(self):
        return f"{self.user_id} follows {self.following_user_id}"    
    
    def getFollowers(self):
        return f"{self.user_id}"

class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes_user')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes_post')
    created = models.DateTimeField(auto_now_add=True)     

    def __str__(self):
        return self.user.username
    
    def liked_by_users(self):
        return self.likes.all()
    
    def total_likes(self):
        return self.likes.count()


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    time_created = models.DateTimeField(auto_now_add=True)
    text = models.TextField(max_length=225)    

    def __str__(self):
        return self.text[0:50]
    
    