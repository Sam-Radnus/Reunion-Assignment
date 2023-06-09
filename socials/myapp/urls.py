from django.urls import path,include
from .views import welcome,CreateUserView,AuthenticateUserView,UserProfileView,follow_user,unfollow_user,create_post,add_comment,post_detail,like_post,unlike_post,all_posts
urlpatterns = [
    path('welcome',welcome),
    path('createUser',CreateUserView.as_view(),name="create_user"),
    path('authenticate', AuthenticateUserView.as_view()),
    path('user',UserProfileView.as_view()),
    path('follow/<int:id>',follow_user),
    path('unfollow/<int:id>',unfollow_user),
    path('posts/',create_post),
    path('posts/<int:id>',post_detail),
    path('like/<int:id>',like_post),
    path('unlike/<int:id>',unlike_post),
    path('comment/<int:id>',add_comment),
    path('all_posts',all_posts,name="all_posts")
]