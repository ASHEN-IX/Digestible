from django.db import models
from django.conf import settings
from django.utils import timezone


class Article(models.Model):
    """
    Article model that mirrors FastAPI backend
    """

    ARTICLE_STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("FETCHING", "Fetching"),
        ("PARSING", "Parsing"),
        ("CHUNKING", "Chunking"),
        ("SUMMARIZING", "Summarizing"),
        ("RENDERING", "Rendering"),
        ("COMPLETED", "Completed"),
        ("FAILED", "Failed"),
    ]

    # FastAPI backend fields
    backend_id = models.CharField(
        max_length=36, unique=True, help_text="UUID from FastAPI backend"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="articles"
    )

    # Article data
    url = models.URLField(max_length=2000)
    title = models.CharField(max_length=500, blank=True, null=True)
    raw_html = models.TextField(blank=True, null=True)
    parsed_text = models.TextField(blank=True, null=True)
    summary = models.TextField(blank=True, null=True)

    # Processing metadata
    status = models.CharField(
        max_length=20, choices=ARTICLE_STATUS_CHOICES, default="PENDING"
    )
    error_message = models.TextField(blank=True, null=True)
    word_count = models.PositiveIntegerField(default=0)
    chunk_count = models.PositiveIntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    # Django-specific fields
    is_favorite = models.BooleanField(default=False)
    tags = models.ManyToManyField("Tag", blank=True, related_name="articles")
    notes = models.TextField(blank=True, help_text="User notes about this article")

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "status"]),
            models.Index(fields=["user", "created_at"]),
            models.Index(fields=["backend_id"]),
        ]

    def __str__(self):
        return self.title or self.url

    @property
    def is_processing(self):
        return self.status in [
            "FETCHING",
            "PARSING",
            "CHUNKING",
            "SUMMARIZING",
            "RENDERING",
        ]

    @property
    def is_completed(self):
        return self.status == "COMPLETED"

    @property
    def has_error(self):
        return self.status == "FAILED"


class Tag(models.Model):
    """
    Tags for organizing articles
    """

    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(
        max_length=7, default="#007bff", help_text="Hex color code"
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="tags"
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["name"]
        unique_together = ["name", "user"]

    def __str__(self):
        return self.name
