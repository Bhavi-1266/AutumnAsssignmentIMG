from django.db import models
from django.conf import settings
from events.models import Events   # adjust import to your project structure

class Photo(models.Model):
    photoid = models.AutoField(primary_key=True)

    event = models.ForeignKey(
        Events,
        on_delete=models.CASCADE,
        related_name='photos'
    )

    uploadedBy = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_photos'
    )

    photoDesc = models.TextField(
        null=True,
        blank=True,
        max_length=500
    )

    photoFile = models.ImageField(
        upload_to='event_photos/'
    )

    uploadDate = models.DateTimeField(
        auto_now_add=True
    )

    # Tags extracted by AI/ML or user
    extractedTags = models.JSONField(
        null=True,
        blank=True
    )

    # Rich metadata (everything else)
    photoMeta = models.JSONField(
        null=True,
        blank=True,
        help_text="EXIF, width, height, ai_labels, colors, model, iso, shutter_speed, gps, etc."
    )

    def __str__(self):
        desc = self.photoDesc[:20] if self.photoDesc else ""
        return f"Photo {self.photoid}: {desc}"

    class Meta:
        ordering = ['-uploadDate']
        indexes = [
            models.Index(fields=['event']),
            models.Index(fields=['uploadDate']),
        ]
