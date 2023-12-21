from django.urls import path
from . import views
urlpatterns = [
    path('username-exist/<str:username>/', views.UsernameExists.as_view(), name='username-exist'),
    path('signup/', views.SignUp.as_view(), name = 'sign-up'),
    path('reset-password/', views.SendEmailToResetPassword.as_view(), name = 'reset-password')
]