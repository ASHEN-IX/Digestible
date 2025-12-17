from rest_framework import serializers
from .models import Article, Tag


class TagSerializer(serializers.ModelSerializer):
    article_count = serializers.SerializerMethodField()

    class Meta:
        model = Tag
        fields = ["id", "name", "color", "article_count", "created_at"]
        read_only_fields = ["id", "created_at"]

    def get_article_count(self, obj):
        return obj.articles.count()


class ArticleSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    is_processing = serializers.BooleanField(read_only=True)
    is_completed = serializers.BooleanField(read_only=True)
    has_error = serializers.BooleanField(read_only=True)

    class Meta:
        model = Article
        fields = [
            "id",
            "backend_id",
            "url",
            "title",
            "summary",
            "status",
            "error_message",
            "word_count",
            "chunk_count",
            "created_at",
            "updated_at",
            "completed_at",
            "is_favorite",
            "tags",
            "notes",
            "is_processing",
            "is_completed",
            "has_error",
        ]
        read_only_fields = [
            "id",
            "backend_id",
            "title",
            "summary",
            "status",
            "error_message",
            "word_count",
            "chunk_count",
            "created_at",
            "updated_at",
            "completed_at",
            "is_processing",
            "is_completed",
            "has_error",
        ]
