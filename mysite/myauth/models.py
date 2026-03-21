from django.contrib.auth.models import User
from django.db import models


def profile_avatar_directory_path(instance: 'Profile', filename: str):
    return f'users/{instance.user.pk}/{filename}'


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE) # Profile не нужен после удаления User
    bio = models.TextField(max_length=500, blank=True)
    agreement_accepted = models.BooleanField(default=False)
    avatar = models.ImageField(null=True, blank=True, upload_to=profile_avatar_directory_path)
