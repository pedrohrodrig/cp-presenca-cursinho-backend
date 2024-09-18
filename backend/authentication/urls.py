from django.urls import include, path
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from .views import UserView, RegisterMultipleView

urlpatterns = format_suffix_patterns(
    [
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("user/", UserView.as_view({"get": "list", "post": "register"})), 
    path("user/self/", UserView.as_view(actions={"get": "retrieve_self"})),
    path("user/<int:pk>/", UserView.as_view(actions={"get": "retrieve_basic_info_by_id"})),
    path("register_multiple/", RegisterMultipleView.as_view({"post": "register_multiple"})),
    ]
)