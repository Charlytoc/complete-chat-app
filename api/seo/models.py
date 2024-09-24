from django.db import models
from django.contrib.auth.models import User
# https://breathecode.herokuapp.com/v1/registry/asset


class Sitemap(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sync = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.url

class Article(models.Model):
    sitemap = models.ForeignKey(Sitemap, on_delete=models.CASCADE)
    slug = models.SlugField(unique=True)
    content = models.TextField()
    url = models.URLField(null=True, blank=True)
    title = models.CharField(max_length=255)
    keywords = models.JSONField()
    language = models.CharField(max_length=10)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class ArticleVersion(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    content = models.TextField()
    keywords = models.JSONField()
    version_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # If the object is not yet saved to the database
            last_version = ArticleVersion.objects.filter(article=self.article).order_by('-version_number').first()
            if last_version:
                self.version_number = last_version.version_number + 1
            else:
                self.version_number = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Version {self.version_number} of {self.article.title} at {self.created_at}"


class Suggestion(models.Model):
    REJECTED = 'REJECTED'
    ACCEPTED = 'ACCEPTED'
    PENDING = 'PENDING'
    STATUS_CHOICES = [
        (REJECTED, 'Rejected'),
        (ACCEPTED, 'Accepted'),
        (PENDING, 'Pending'),
    ]

    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    original_text = models.TextField()
    replacement_text = models.TextField()
    keywords = models.JSONField(null=True, blank=True)
    status = models.CharField(
        max_length=8,
        choices=STATUS_CHOICES,
        default=PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Suggestion(for={self.article.title})'


