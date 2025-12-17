from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserPreference(models.Model):
    """
    User preferences for article processing
    """

    OUTPUT_FORMAT_CHOICES = [
        ("audio", "Audio (MP3)"),
        ("text", "Text Summary"),
        ("both", "Both Audio and Text"),
    ]

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="preferences"
    )
    output_format = models.CharField(
        max_length=10, choices=OUTPUT_FORMAT_CHOICES, default="both"
    )
    audio_quality = models.CharField(
        max_length=10,
        choices=[("low", "Low"), ("medium", "Medium"), ("high", "High")],
        default="medium",
    )
    auto_process = models.BooleanField(default=True)
    email_notifications = models.BooleanField(default=False)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Preferences for {self.user.username}"


@receiver(post_save, sender=User)
def create_user_preferences(sender, instance, created, **kwargs):
    """Create UserPreference when a new user is created"""
    if created:
        UserPreference.objects.create(user=instance)

    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username


class UserProfile(models.Model):
    """
    Extended user profile information
    """

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    timezone = models.CharField(max_length=50, default="UTC")

    # Statistics
    articles_submitted = models.PositiveIntegerField(default=0)
    articles_processed = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Profile for {self.user.username}"
