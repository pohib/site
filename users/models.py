from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)

    def get_avatar_url(self):
        if self.avatar and hasattr(self.avatar, 'url'):
            return self.avatar.url
        return '/static/img/default-avatar.png'

class TelegramData(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    telegram_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=32, blank=True, null=True)
    photo_url = models.URLField(blank=True, null=True)
    auth_date = models.DateTimeField()

    def __str__(self):
        return f"Telegram данные для {self.user.username}"
    
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()