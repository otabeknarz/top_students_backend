from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from users.api.serializers import UserSerializer
from users.models import User, Invitation


@api_view(["GET"])
@permission_classes([AllowAny])
def get_users(request):
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_user(request, user_id):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return Response(status=status.HTTP_404_NOT_FOUND)
    serializer = UserSerializer(user)
    return Response(serializer.data)


@api_view(["POST"])
@permission_classes([AllowAny])
def add_user(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["PATCH"])
@permission_classes([AllowAny])
def update_user(request, user_id):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.data.get("id"):
        request.data.pop("id")

    serializer = UserSerializer(user, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
@permission_classes([AllowAny])
def get_or_create_invitation(request, user_id):
    user = User.objects.filter(id=user_id).first()
    if not user:
        return Response(status=status.HTTP_404_NOT_FOUND)
    user.has_successfully_registered = True
    user.save()
    invitation_count = None
    user_who_invite = None
    if user.invited_by.count() != 0:
        user_who_invite = [u for u in user.invited_by.all()][0]
        invitation_count = user_who_invite.invitation.count()
    invitation = Invitation.objects.filter(user=user).first()
    if not invitation:
        new_invitation = Invitation.objects.create(user=user)
        return Response({"token": new_invitation.token, "count": invitation_count, "user_id": user_who_invite.id if user_who_invite else None}, status=status.HTTP_201_CREATED)
    return Response({"token": invitation.token, "count": invitation_count, "user_id": user_who_invite.id if user_who_invite else None}, status=status.HTTP_200_OK)


@api_view(["GET"])
@permission_classes([AllowAny])
def add_invitation(request, user_id, being_invited_user_id):
    user = User.objects.filter(id=user_id).first()
    invited_user = User.objects.filter(id=being_invited_user_id).first()
    if not user or not invited_user:
        return Response(status=status.HTTP_404_NOT_FOUND)
    invitation = Invitation.objects.filter(user=user).first()
    if not invitation:
        new_invitation = Invitation(user=user)
        new_invitation.invited_users.add(user)
        new_invitation.save()
    else:
        invitation.invited_users.add(user)


@api_view(["GET"])
@permission_classes([AllowAny])
def invite_user(request, invitation_token, user_id):
    invitation = Invitation.objects.filter(token=invitation_token).first()
    if not invitation:
        return Response(status=status.HTTP_404_NOT_FOUND)
    user = User.objects.filter(id=user_id).first()
    if not user:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if user.invited_by.count() != 0:
        return Response(status=status.HTTP_403_FORBIDDEN)

    invitation.invited_users.add(user)
    invitation.save()
    return Response({"user_id": invitation.user.id, "count": invitation.invited_users.filter(has_successfully_registered=True).count()}, status=status.HTTP_200_OK)
