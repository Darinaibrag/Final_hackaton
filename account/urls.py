from django.urls import path
from .views import RegistrationView, ActivationView, LoginView, UserListView, LogoutView, RegistrationPhoneView
from rest_framework_simplejwt.views import TokenRefreshView




urlpatterns = [
    path('register/', RegistrationView.as_view()),
    path('activate/', ActivationView.as_view()),
    path('login/', LoginView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
    path('list_user/', UserListView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('register_phone/', RegistrationPhoneView.as_view()),

]