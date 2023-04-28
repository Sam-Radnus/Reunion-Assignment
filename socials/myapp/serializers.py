from rest_framework import serializers
from myapp.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.authentication import TokenAuthentication, SessionAuthentication, BasicAuthentication
from rest_framework_jwt.authentication import JSONWebTokenAuthentication

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model=User
        fields=['username','email','password']
    
    def validate(self, data):
        # Check if the password is provided
        if not data.get('password'):
            raise serializers.ValidationError("Please provide a password")
        
        # Check if the username is provided
        if not data.get('username'):
            raise serializers.ValidationError("Please provide a username")
        
        # Check if the email is provided
        if not data.get('email'):
            raise serializers.ValidationError("Please provide an email address")
        
        return data
    
    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user