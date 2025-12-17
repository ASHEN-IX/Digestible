import requests
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.conf import settings
from django.shortcuts import get_object_or_404

from .models import Article, Tag
from .serializers import ArticleSerializer, TagSerializer


class ArticleViewSet(viewsets.ModelViewSet):
    """
    API endpoint for articles - proxies to FastAPI backend
    """

    queryset = Article.objects.all()  # Required for DRF router basename
    serializer_class = ArticleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Article.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Create article via FastAPI backend"""
        url = self.request.data.get("url")
        if not url:
            return Response(
                {"error": "URL is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Submit to FastAPI backend
        fastapi_response = requests.post(
            f"{settings.FASTAPI_URL}/api/v1/articles",
            json={"url": url, "user_id": str(self.request.user.id)},
            timeout=30,
        )

        if fastapi_response.status_code == 202:
            backend_data = fastapi_response.json()

            # Create local Django record
            article = serializer.save(
                user=self.request.user,
                backend_id=backend_data["id"],
                url=url,
                status="PENDING",
            )

            # Update from backend response
            self._sync_with_backend(article.backend_id)

            return Response(
                ArticleSerializer(article).data, status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                {"error": "Failed to submit article"},
                status=fastapi_response.status_code,
            )

    @action(detail=True, methods=["get"])
    def sync(self, request, pk=None):
        """Sync article status with FastAPI backend"""
        article = self.get_object()
        self._sync_with_backend(article.backend_id)
        serializer = self.get_serializer(article)
        return Response(serializer.data)

    def _sync_with_backend(self, backend_id):
        """Sync article data from FastAPI backend"""
        try:
            response = requests.get(
                f"{settings.FASTAPI_URL}/api/v1/articles/{backend_id}"
            )
            if response.status_code == 200:
                backend_data = response.json()

                # Update local record
                article = Article.objects.filter(backend_id=backend_id).first()
                if article:
                    article.status = backend_data["status"]
                    article.title = backend_data.get("title")
                    article.summary = backend_data.get("summary")
                    article.updated_at = backend_data["created_at"]

                    if article.status == "COMPLETED":
                        article.completed_at = article.updated_at

                    article.save()

        except requests.RequestException:
            # Backend might be unavailable, continue with local data
            pass

    @action(detail=False, methods=["get"])
    def stats(self, request):
        """Get user article statistics"""
        user = request.user
        stats = {
            "total": Article.objects.filter(user=user).count(),
            "completed": Article.objects.filter(user=user, status="COMPLETED").count(),
            "processing": Article.objects.filter(
                user=user,
                status__in=[
                    "FETCHING",
                    "PARSING",
                    "CHUNKING",
                    "SUMMARIZING",
                    "RENDERING",
                ],
            ).count(),
            "failed": Article.objects.filter(user=user, status="FAILED").count(),
        }
        return Response(stats)


class TagViewSet(viewsets.ModelViewSet):
    """
    API endpoint for tags
    """

    queryset = Tag.objects.all()  # Required for DRF router basename
    serializer_class = TagSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Tag.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
