from django.db import models
from django.conf import settings
# Create your models here.
class Events(models.Model):
    eventid = models.AutoField(primary_key=True)
    eventname = models.CharField(max_length=100)
    eventdesc = models.TextField(max_length=1000)
    eventdate = models.DateField()
    eventtime = models.TimeField()
    eventCoverPhoto = models.ImageField(upload_to='event_covers/', blank=True, default='' )
    eventCreator = models.ForeignKey(settings.AUTH_USER_MODEL , on_delete=models.SET_NULL, null=True)
    eventlocation = models.CharField(max_length=100)
    visibility = models.CharField(
        max_length=10,
        choices=(
            ("admin", "Admin"),
            ("img", "IMG Member"),
            ("public", "Public"),
        ),
        default="public",
    )

    class Meta:
        db_table = 'events'
        verbose_name = 'Event'
        verbose_name_plural = 'Events'
        ordering = ['eventdate', 'eventtime']
        permissions = (
            ("view_event_obj", "Can view this event object"),
            ("change_event_obj", "Can change this event object"),
            ("delete_event_obj", "Can delete this event object"),
        )

    def __str__(self):
        return self.eventname
