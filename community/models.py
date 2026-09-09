from django.conf import settings
from django.db import models


class CommunityPost(models.Model):
    """A community post created by an I-V Tree user."""

    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='community_posts',
        null=True,
        blank=True,
    )
    title = models.CharField(max_length=150)
    content = models.TextField()
    image = models.ImageField(
        upload_to='community-posts/',
        blank=True,
    )
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title