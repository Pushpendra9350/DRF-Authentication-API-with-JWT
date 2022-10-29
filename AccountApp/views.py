from django.shortcuts import render
from rest_framework.response import Response 
from rest_framework.views import APIView
from rest_framework import status
from AccountApp import serializers
import sys
from django.contrib.auth import authenticate
from AccountApp.renderers import UserRenderer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.permissions import IsAuthenticated

# Will generate tokens manually
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

# Create your views here.
class RegisterUserAPI(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format = None):
        serializer = serializers.UserRegisterationSerializer(data = request.data)
        if serializer.is_valid(raise_exception=True):
            print("Valid data and data is ", request.data)
            user = serializer.save()
            token = get_tokens_for_user(user)
            return Response({"Message":"User created successfully", "token":token}, status = status.HTTP_201_CREATED)
        return Response({"Message":serializer.errors}, status = status.HTTP_400_BAD_REQUEST)

class UserLoginAPI(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format = None):
        print("here>>",request.data)
        serializer = serializers.UserLoginSerializer(data = request.data)
        if serializer.is_valid():
            email = serializer.data.get("email")
            password = serializer.data.get("password")
            user = authenticate(email = email, password = password)
            if user is not None:
                token = get_tokens_for_user(user)
                return Response({"Message": "LoggedIn Successfully", "token":token}, status=status.HTTP_200_OK)
            else:
                return Response({"Message": "Invalid Credentials"}, status=status.HTTP_404_NOT_FOUND)
        return Response({"Message": serializer.errors}, status=status.HTTP_404_NOT_FOUND)

class UserProfileAPI(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    def get(self, request, format = None):
        serializer = serializers.UserProfileSerializer(request.user)
        return Response(serializer.data, status = status.HTTP_200_OK)

class UserChangePasswordAPI(APIView):
    renderer_classes = [UserRenderer]
    permission_classes = [IsAuthenticated]
    def post(self, request, format = None):
        serializer = serializers.UserChangePasswordSerializer(data = request.data, context = {"user": request.user})
        if serializer.is_valid(raise_exception=True):
            return Response({"Message":"User created successfully"}, status = status.HTTP_200_OK)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

class SendPasswordResetEamilAPI(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, format = None):
        serializer = serializers.SendPasswordResetEamilSerializer(
            data=request.data
        )
        if serializer.is_valid(raise_exception=True):
            return Response({"Message":"Email sent to your register email. Please check your email. Valid for next 5 minutes"}, status = status.HTTP_200_OK)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)

class ResetPasswordAPI(APIView):
    renderer_classes = [UserRenderer]
    def post(self, request, uid, token, format = None):
        serializer = serializers.SendResetPasswordSerializer(
            data=request.data,
            context = {"uid":uid, "token":token}
        )
        if serializer.is_valid(raise_exception=True):
            return Response({"Message":"Your new password reset successfully"}, status = status.HTTP_200_OK)
        return Response(serializer.errors, status = status.HTTP_400_BAD_REQUEST)
