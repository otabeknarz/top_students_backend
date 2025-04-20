import uuid
import random
import string

from django.contrib.auth.models import AbstractUser
from django.db import models


def get_random_token():
    return "".join(random.choices(string.ascii_letters + string.digits, k=10))


class User(AbstractUser):
    id = models.CharField(
        primary_key=True, default=uuid.uuid4, max_length=50
    )
    name = models.CharField(blank=True, max_length=255, null=True)
    email = models.EmailField(blank=True, max_length=255, null=True)
    has_successfully_registered = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.username:
            self.username = self.id
        super(User, self).save(*args, **kwargs)

    @classmethod
    def get_invited_users(self):
        invitation = Invitation.objects.filter(user=self).first()
        if not invitation:
            return
        return invitation.invited_users.filter(has_successfully_registered=True)


class Invitation(models.Model):
    id = models.CharField(
        primary_key=True, default=uuid.uuid4, editable=False, unique=True, max_length=50
    )
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="invitation"
    )
    invited_users = models.ManyToManyField(User, blank=True, related_name="invited_by")
    token = models.CharField(default=get_random_token, unique=True, max_length=10)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.id} - {self.user.name} - @{self.user.username} - {self.invited_users.filter(has_successfully_registered=True).count()}"
