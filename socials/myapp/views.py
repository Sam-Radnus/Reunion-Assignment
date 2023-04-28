from django.shortcuts import render
from django.http import JsonResponse
from .serializers import UserSerializer
from .models import User,UserFollowing
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


        
