from django.urls import path

from .views import (CustomLoginView, CustomLogoutView,
                    ProfileView, RegisterView, PatientProfileUpdateView)

app_name = "users"

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("accounts/login/", CustomLoginView.as_view(), name="login"),
    path("logout/", CustomLogoutView.as_view(), name="logout"),
    path("accounts/profile/", ProfileView.as_view(), name="profile"),
    path("profile/", ProfileView.as_view(), name="profile"),
    path('profile/update/', PatientProfileUpdateView.as_view(), name='update_profile'),
]