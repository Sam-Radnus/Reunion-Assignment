from django.shortcuts import render
from django.http import JsonResponse
from .serializers import UserSerializer
from .models import User,UserFollowing,Post,Like
from rest_framework import generics
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from rest_framework_jwt.views import ObtainJSONWebToken
from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_jwt.serializers import jwt_encode_handler, jwt_payload_handler
from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
import jwt
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed
import json
from django.views.decorators.http import require_http_methods
# Create your views here.
def welcome(self):
    data={"data":"hello world"}
    return JsonResponse(data)

class CreateUserView(generics.CreateAPIView):
    queryset=User.objects.all()
    serializer_class=UserSerializer

class AuthenticateUserView(ObtainJSONWebToken):
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        print(request.data)
        print(serializer)
        if serializer.is_valid():
            user = serializer.object.get('user') or request.user
            token = serializer.object.get('token')
            response_data = {'token': token, 'username': user.username}
            return Response(response_data)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    print("hello")
    permission_classes = [IsAuthenticated]
    authentication_classes = [JSONWebTokenAuthentication]
    def get(self, request):
        try:
            user = request.user
            #followers = user.profile.followers.count()
            #following = user.profile.following.count()
            print(user.username)
            print(user.email)
            print(user.followers.all())
            print(user.following.all())
            data={
                'username':user.username,
                'email':user.email
            }
            return JsonResponse(data)
        except Exception as e:
            print("hello")
            return Response({'error': str(e)}, status=400)
        
@api_view(['GET'])
def user_profile_view(request):
    try:
        user = request.user
        followers = user.profile.followers.count()
        following = user.profile.following.count()
        print(user)
        return Response({'username': user.username, 'followers': followers, 'following': following})
    except Exception as e:
        print("hello")
        return Response({'error': str(e)}, status=400)
        
        

@require_POST
@csrf_exempt
def follow_user(request,id):
    # Get the authenticated user
    
    user = request.user

    print(request)
    auth_header = request.META.get('HTTP_AUTHORIZATION', None)
    print(auth_header)
    token = request.META.get('HTTP_AUTHORIZATION').split(' ')[1]

    try:
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Token expired')
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid token')
        
    print(decoded_token)
    print(decoded_token['email'])
    if not decoded_token:
        return JsonResponse({'error': 'You must be authenticated to follow a user.'}, status=401)

    
    print(id)
    # Check if the user with id exists
    user=get_object_or_404(User, email=decoded_token['email'])
    following_user = get_object_or_404(User, id=id)
    print(user.id)
    print(following_user)
    print(user.following.filter(id=id))
    following_user = get_object_or_404(User, id=id)

    # Check if the authenticated user is not following the same user already
    if user.following.filter(following_user_id=following_user).exists():
        return JsonResponse({'error': 'You are already following this user.'}, status=400)
    
    # Create the UserFollowing object
    user_following = UserFollowing(user_id=user, following_user_id=following_user)
    user_following.save()
    
    # Return success response
    return JsonResponse({'success': 'You are now following this user.'}, status=200)

@require_POST
@csrf_exempt
def unfollow_user(request, id):
    # Get the authenticated user
    user = request.user

    # Get the authorization token from the request header
    auth_header = request.META.get('HTTP_AUTHORIZATION', None)
    if not auth_header:
        return JsonResponse({'error': 'Authorization header missing.'}, status=401)

    try:
        token = auth_header.split(' ')[1]
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        print(decoded_token)
    except jwt.ExpiredSignatureError:
        raise AuthenticationFailed('Token expired')
    except jwt.InvalidTokenError:
        raise AuthenticationFailed('Invalid token')
    
    user=get_object_or_404(User, email=decoded_token['email'])
    # Check if the authenticated user is following the given user
    following_user = get_object_or_404(User, id=id)
    print(following_user)
    print(user.following.filter(following_user_id=id))
    if not user.following.filter(following_user_id=id).exists():
        return JsonResponse({'error': 'You are not following this user.'}, status=400)

    # Delete the UserFollowing object
    user_following = user.following.get(following_user_id=id)
    user_following.delete()

    # Return success response
    return JsonResponse({'success': 'You have unfollowed this user.'}, status=200)


@require_POST
@csrf_exempt
def create_post(request):
    # Get the user object
    
    auth_header = request.META.get('HTTP_AUTHORIZATION', None)
    
    if not auth_header:
        return JsonResponse({'error': 'Authorization header missing.'}, status=401)
    print(auth_header)
    try:
        token = auth_header.split(' ')[1]
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        scopes = decoded_token.get('scope', '').split()
        
        print(decoded_token)
        print(scopes)
    except jwt.ExpiredSignatureError:
        return JsonResponse({"Error":"Token Expired"})
    except jwt.InvalidTokenError:
        return JsonResponse({"Error":"Token Invalid"})
    
    user=get_object_or_404(User, email=decoded_token['email'])
    print(user)
    # Get the JSON data from the request body
    data = json.loads(request.body)

    # Create the new post object
    post = Post(name=data['name'], caption=data['caption'],user=user)
    post.save()

    # Return success response with the created post object
    response_data = {
        'Post-ID': post.id,
        'Title': post.name,
        'Description': post.caption,
        'user': post.user.username,
        'Created Time(UTC)': post.time_created.strftime('%Y-%m-%d %H:%M:%S'),
        'likes': post.total_likes(),
    }
    return JsonResponse(response_data, status=201)

@require_http_methods(['DELETE'])
@csrf_exempt
def delete_post(request, id):
    # Get the authenticated user
    
    print(1)
    auth_header = request.META.get('HTTP_AUTHORIZATION', None)
    if not auth_header:
        return JsonResponse({'error': 'Authorization header missing.'}, status=401)
    
    try:
        token = auth_header.split(' ')[1]
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        print(decoded_token)
    except jwt.ExpiredSignatureError:
        return JsonResponse({"Error":"Token Expired"})
    except jwt.InvalidTokenError:
        return JsonResponse({"Error":"Token Invalid"})
    
    user=get_object_or_404(User, email=decoded_token['email'])
    
    # # Get the post to delete, checking that it belongs to the authenticated user
    try:
        print(id)
        print(user)

        post = get_object_or_404(Post, id=id, user=user)
    except:
        return JsonResponse({'Error':'Some Error Occurred'})
    # Delete the post
    post.delete()
    
    # # Return success response
    return JsonResponse({'message': 'Post deleted successfully.'})




@csrf_exempt
@require_http_methods(['DELETE', 'GET'])
def post_detail(request, id):
    
    if request.method == 'DELETE':
        # Get the post to delete, checking that it belongs to the authenticated user
        auth_header = request.META.get('HTTP_AUTHORIZATION', None)
        if not auth_header:
            return JsonResponse({'error': 'Authorization header missing.'}, status=401)
    
        try:
            token = auth_header.split(' ')[1]
            decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
            print(decoded_token)
        except jwt.ExpiredSignatureError:
            return JsonResponse({"Error":"Token Expired"})
        except jwt.InvalidTokenError:
            return JsonResponse({"Error":"Token Invalid"})
    
        user=get_object_or_404(User, email=decoded_token['email'])
        try:
            post = get_object_or_404(Post, id=id, user=user)
            # Delete the post
            post.delete()
            # Return success response
            return JsonResponse({'message': 'Post deleted successfully.'})
        except:
            return JsonResponse({'message': 'Some Error Occurred.'})
    
    elif request.method == 'GET':
        # Get the post, checking that it exists
        try:
            post = get_object_or_404(Post, id=id)
            # Get the number of likes and comments for the post
            num_likes = 0 #post.likes.count()
            num_comments = 0 #post.comments.count()
            print(post.name)
            print(post.caption)
            print(post.user)
            # Return the post data along with the number of likes and comments
            return JsonResponse({'post':post.name , 'num_likes': num_likes, 'num_comments': num_comments})
        except:
            return JsonResponse({'error':'some error occurred'})
    else :
        return JsonResponse({'message':'method not allowed'})


@require_POST
@csrf_exempt
def like_post(request, id):
    # Get the authenticated user
    auth_header = request.META.get('HTTP_AUTHORIZATION', None)
    if not auth_header:
        return JsonResponse({'error': 'Authorization header missing.'}, status=401)
    
    try:
        token = auth_header.split(' ')[1]
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        print(decoded_token)
    except jwt.ExpiredSignatureError:
        return JsonResponse({"Error":"Token Expired"})
    except jwt.InvalidTokenError:
        return JsonResponse({"Error":"Token Invalid"})
    
    user=get_object_or_404(User, email=decoded_token['email'])

    # Get the post to like
    post = get_object_or_404(Post, id=id)

    # Create a new Like object for the post and user
    like, created = Like.objects.get_or_create(user=user, post=post)

    # If the Like object was just created, increment the post's like count
    if created:
       post.likes.add(user)
    else:
       return JsonResponse({'error': 'Post Already liked. or Some other Error'})

    # Return success response
    return JsonResponse({'message': 'Post liked successfully.'})

@require_POST
@csrf_exempt
def unlike_post(request, id):
    # Get the authenticated user
    user = request.user
    auth_header = request.META.get('HTTP_AUTHORIZATION', None)
    if not auth_header:
        return JsonResponse({'error': 'Authorization header missing.'}, status=401)
    
    try:
        token = auth_header.split(' ')[1]
        decoded_token = jwt.decode(token, settings.SECRET_KEY, algorithms=['HS256'])
        print(decoded_token)
    except jwt.ExpiredSignatureError:
        return JsonResponse({"Error":"Token Expired"})
    except jwt.InvalidTokenError:
        return JsonResponse({"Error":"Token Invalid"})
    
    user=get_object_or_404(User, email=decoded_token['email'])
    # Get the Like object for the user and post
    try:
        like = get_object_or_404(Like, user=user, post__id=id)
        post = get_object_or_404(Post, id=id)
        # Decrement the post's like count and delete the Like object
        like.delete()
        post.likes.remove(user)
    except:
        return JsonResponse({'error': 'Some Error Occurred.'})

    # Return success response
    return JsonResponse({'message': 'Post unliked successfully.'})
# @api_view(['POST'])
# def authenticate_user(request):
#     email = request.data.get('email')
#     password = request.data.get('password')
#     print(user)
#     print(password)
#     # Authenticate the user using email and password
#     user = authenticate(request, email=email, password=password)
    
#     # If authentication is successful, generate JWT token and return it
#     if user is not None:
#         payload = jwt_payload_handler(user)
#         token = jwt_encode_handler(payload)
#         return Response({'token': token})
#     else:
#         return Response({'error': 'Invalid credentials'}, status=400)


        
