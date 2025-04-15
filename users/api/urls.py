from django.urls import path
from . import views

urlpatterns = [
    path("get/", views.get_users),
    path("get/<str:user_id>/", views.get_user),
    path("add/", views.add_user),
    path("update/<str:user_id>/", views.update_user),
    path("invitations/create/<str:user_id>/", views.get_or_create_invitation),
    path("invitations/invite/<str:invitation_token>/<str:user_id>/", views.invite_user),
]
