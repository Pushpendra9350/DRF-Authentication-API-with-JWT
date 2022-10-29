from django.contrib import admin
from django.urls import path
from AccountApp import views

urlpatterns = [
    path('register/', views.RegisterUserAPI.as_view(), name="register"),
    path('login/', views.UserLoginAPI.as_view(), name="login"),
    path('profile/', views.UserProfileAPI.as_view(), name="profile"),
    path('change-password/', views.UserChangePasswordAPI.as_view(), name="changePassword"),
    path('send-password-reset-link/', views.SendPasswordResetEamilAPI.as_view(), name="resetpasswordemail"),
    path('reset-password/<str:uid>/<str:token>/', views.ResetPasswordAPI.as_view(), name="resetpassword"),
]