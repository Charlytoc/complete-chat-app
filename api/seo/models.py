import uuid
from django.db import models

from django.contrib.auth.models import User
from django.utils import timezone

import html
import requests
import markdown2
from bs4 import BeautifulSoup
from markdownify import markdownify as md
from api.authenticate.models import PublishableToken

# https://breathecode.herokuapp.com/v1/registry/asset


class SitemapIndex(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    publish_token = models.ForeignKey(
        PublishableToken, on_delete=models.SET_NULL, null=True, blank=True
    )
    url = models.URLField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_sync = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.url

    def get_sitemaps(self):
        from .actions import get_all_sitemaps

        result = get_all_sitemaps(self.id)
        return result


class Sitemap(models.Model):
    index = models.ForeignKey(SitemapIndex, on_delete=models.CASCADE)
    url = models.URLField()

    last_sync = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.url

    def get_urls(self):
        from .actions import get_all_urls_for_a_sitemap

        result = get_all_urls_for_a_sitemap(self.id)
        return result


class Article(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    sitemap = models.ForeignKey(Sitemap, on_delete=models.CASCADE)
    content = models.TextField()
    html_content = models.TextField(null=True, blank=True)
    url = models.URLField(null=True, blank=True)
    title = models.CharField(max_length=255)
    fetched = models.BooleanField(default=False)
    language = models.CharField(max_length=10, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    last_sync = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    article_content_md = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

    def fetch_content(self):
        res = requests.get(self.url)

        soup = BeautifulSoup(res.text, "html.parser")

        for unwanted in soup.find_all(["script", "style"]):
            unwanted.decompose()

        title = soup.title.string if soup.title else "No Title"
        self.title = title

        article = soup.find("article")
        if article:
            sanitized_content = str(article)
            self.html_content = sanitized_content
        else:

            body = soup.find("body")
            if body:
                sanitized_content = str(body)
                self.html_content = sanitized_content
            else:
                print("Neither <article> nor <body> tags found.")
                return


        decoded_content = self.html_content 
        self.article_content_md = md(decoded_content)

        self.content = decoded_content


        self.fetched = True
        self.last_sync = timezone.now()
        self.save()

    def suggest_linking(self):
        from .actions import suggest_internal_linking

        suggest_internal_linking(self.id)


class ArticleVersion(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    content = models.TextField()
    keywords = models.JSONField()
    version_number = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.pk:  # If the object is not yet saved to the database
            last_version = (
                ArticleVersion.objects.filter(article=self.article)
                .order_by("-version_number")
                .first()
            )
            if last_version:
                self.version_number = last_version.version_number + 1
            else:
                self.version_number = 1
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Version {self.version_number} of {self.article.title} at {self.created_at}"


class Suggestion(models.Model):
    REJECTED = "REJECTED"
    ACCEPTED = "ACCEPTED"
    PENDING = "PENDING"
    STATUS_CHOICES = [
        (REJECTED, "Rejected"),
        (ACCEPTED, "Accepted"),
        (PENDING, "Pending"),
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
        return f"Suggestion(for={self.article.title})"


class SystemPromptModel(models.Model):
    keywords = models.TextField()
    internal_linking = models.TextField()

    def generate_prompt(self):
        return f"""
You are a SEO specialist. 
Refactor the following article to optimize the internal linking of it.
The keywords of the article is: {self.keywords}
Note: If there are a empty list of keywords, please suggest at least 3.

Please write the SuggestionsList like a SEO expert with more than 40 years of experience. The goal is to IMPROVE parts of the article. You must identify areas where an internal linking may be beneficial using the provided links down below. The internal linking should be made properly following SEO tips.

For example: 
original_text: "To create an AI application we must think about the features we want to add"
replacement_text: "To [create an AI application](link for some related article that talks about this topic) we must think about the features we want to add"

Also, if you identify that the content of the article may be extended in some part, feel free to add it!

You have all free creative thinking.

---LINKS YOU MAY USE FOR INTERNAL LINKING
{self.internal_linking}
---

The task is to REWRITE parts of the article to improve **internal linking**.

- Suggest at least 20 changes that can be made to the article.
- Keep in mind this about each suggestion: 
The `original_text` must be an exact match of the part of the article where an internal link can be added. Keep in mind that this text must have at least 5 words in order to avoid problems when replacing the content with the suggested one.

The `replacement_text` must replace the original_text adding internal links or improving misspellings, fixing things...

- You can also suggest new articles to create them if you think is necessary. To do so, when adding the link so it like: [NEW: text of the link](possible article link)

- Think about missing topics in the article based on the provided search results article that can be added to the content.
        """
