from django.db import models

class Content(models.Model):
    title = models.CharField(max_length=255)
    type = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    image = models.URLField(blank=True, null=True)
    url = models.URLField()
    content_rating = models.CharField(max_length=50, blank=True, null=True)
    rating_value = models.FloatField(blank=True, null=True)

    def __str__(self):
        return f"{self.title} ({self.type}) - Rating: {self.rating_value}"
