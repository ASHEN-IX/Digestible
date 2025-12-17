# Using Django's default User model for Phase 0
# Custom User model will be added in Phase 1 when needed
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username


class UserProfile(models.Model):
    """
    Extended user profile information
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    timezone = models.CharField(max_length=50, default='UTC')

    # Statistics
    articles_submitted = models.PositiveIntegerField(default=0)
    articles_processed = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"Profile for {self.user.username}"