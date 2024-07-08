from django.conf import settings
from django.db import models

class GoogleOAuth2Credentials(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    access_token = models.TextField(blank=True, null=True)
    refresh_token = models.TextField()
    scopes = models.TextField()

    def __str__(self):
        return f'{self.user.username} Google OAuth2 Credentials'
