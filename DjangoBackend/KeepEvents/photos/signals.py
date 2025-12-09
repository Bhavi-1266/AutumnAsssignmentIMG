from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
from django.db.models import F
from .models import likedPhoto, comment, downloadedPhoto, viewedPhoto, Photo

# ---------- Likes ----------
@receiver(post_save, sender=likedPhoto)
def on_like_created(sender, instance, created, **kwargs):
    if not created:
        return
    # increment likecount atomically
    with transaction.atomic():
        Photo.objects.filter(pk=instance.photo_id).update(likecount=F('likecount') + 1)

@receiver(post_delete, sender=likedPhoto)
def on_like_deleted(sender, instance, **kwargs):
    # decrement but keep >= 0
    with transaction.atomic():
        Photo.objects.filter(pk=instance.photo_id, likecount__gte=1).update(likecount=F('likecount') - 1)

# ---------- comments ----------
@receiver(post_save, sender=comment)
def on_comment_created(sender, instance, created, **kwargs):
    if not created:
        return
    with transaction.atomic():
        Photo.objects.filter(pk=instance.photo_id).update(commentcount=F('commentcount') + 1)

@receiver(post_delete, sender=comment)
def on_comment_deleted(sender, instance, **kwargs):
    with transaction.atomic():
        Photo.objects.filter(pk=instance.photo_id, commentcount__gte=1).update(commentcount=F('commentcount') - 1)

# ---------- Downloads ----------
@receiver(post_save, sender=downloadedPhoto)
def on_download_created(sender, instance, created, **kwargs):
    if not created:
        return
    with transaction.atomic():
        Photo.objects.filter(pk=instance.photo_id).update(downloadcount=F('downloadcount') + 1)

@receiver(post_delete, sender=downloadedPhoto)
def on_download_deleted(sender, instance, **kwargs):
    with transaction.atomic():
        Photo.objects.filter(pk=instance.photo_id, downloadcount__gte=1).update(downloadcount=F('downloadcount') - 1)

# ---------- Views ----------
@receiver(post_save, sender=viewedPhoto)
def on_view_created(sender, instance, created, **kwargs):
    if not created:
        return
    with transaction.atomic():
        Photo.objects.filter(pk=instance.photo_id).update(viewcount=F('viewcount') + 1)

@receiver(post_delete, sender=viewedPhoto)
def on_view_deleted(sender, instance, **kwargs):
    with transaction.atomic():
        Photo.objects.filter(pk=instance.photo_id, viewcount__gte=1).update(viewcount=F('viewcount') - 1)
