from rest_framework import serializers
from AccountApp.models import User
import re
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from AccountApp.utils import Util

class UserRegisterationSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "name", "password", "tc"]
        extra_kwargs = {
            "password":{"write_only":True}
        }
        
        def create(self, validate_data):
            return User.objects.create_user(**validate_data)
            
class UserLoginSerializer(serializers.ModelSerializer):
    # Will validate email
    email = serializers.EmailField(max_length=255)
    class Meta:
        model = User
        fields = ["email", "password"]

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "email", "name"]

class UserChangePasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length = 255, style={"input_type":"password"}, write_only=True)
    class Meta:
        model = User
        fields = ["password"]
    def validate(self, attrs):
        password = attrs.get("password")
        user = self.context.get("user")
        user.set_password(password)
        user.save()
        return attrs

class SendPasswordResetEamilSerializer(serializers.Serializer):
    email = serializers.EmailField(max_length = 255)
    class Meta:
        model = User
        fields = ["email"]

    def validate(self, attrs):
        email = attrs.get("email")
        print(email)
        if User.objects.filter(email=email).exists():
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.id))
            token = PasswordResetTokenGenerator().make_token(user)
            final_link = "http://127.0.0.1:8000/api/user/reset-password/"+str(uid)+"/"+str(token)
            print(final_link)
            body = 'Click Following Link to Reset Your Password. Valid only for 5 minutes.'+final_link
            data = {
                'subject':'Reset Your Password',
                'body':body,
                'to_email':user.email
            }
            Util.send_email(data)
            return attrs
        else:
            raise serializers.ValidationError("You are not registered user")
        return attrs

class SendResetPasswordSerializer(serializers.Serializer):
    password = serializers.CharField(max_length = 255, style={"input_type":"password"}, write_only=True)
    class Meta:
        model = User
        fields = ["password"]

    def validate(self, attrs):
        try:
            password = attrs.get("password")
            encoded_uid = self.context.get("uid")
            token = self.context.get("token")
            ids = smart_str(urlsafe_base64_decode(encoded_uid))
            user = User.objects.get(id=ids)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise serializers.ValidationError("Token is not valid or expire")
            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError:
            PasswordResetTokenGenerator().check_token(user, token)
            raise serializers.ValidationError("Token is not valid or expire")