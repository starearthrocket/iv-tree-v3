from django.conf import settings
from django.db import models


class Profile(models.Model):
    """Additional profile information for an I-V Tree user."""

    class Avatar(models.TextChoices):
        OAK_LEAF = 'avatar-oak-leaf.png', 'Oak Leaf'
        ACORN = 'avatar-acorn.png', 'Acorn'
        ROBIN = 'avatar-robin.png', 'Robin'
        FOX = 'avatar-fox.png', 'Fox'
        HEDGEHOG = 'avatar-hedgehog.png', 'Hedgehog'
        FERN = 'avatar-fern.png', 'Fern'
        BADGER = 'avatar-badger.png', 'Badger'
        SQUIRREL = 'avatar-squirrel.png', 'Squirrel'
        DEER = 'avatar-deer.png', 'Deer'
        PINECONE = 'avatar-pinecone.png', 'Pinecone'

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
    )
    avatar_choice = models.CharField(
        max_length=40,
        choices=Avatar.choices,
        default=Avatar.OAK_LEAF,
    )
    bio = models.TextField(
        max_length=500,
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'{self.user.username} profile'