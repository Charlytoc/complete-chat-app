from django.http import JsonResponse
from urllib.parse import urlparse

from django.views import View
import json
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.core.serializers import serialize
from django.shortcuts import get_object_or_404
from .models import Article, Suggestion
import random
from rest_framework.permissions import AllowAny
from .serializers import ArticleSerializer, SuggestionSerializer, SitemapIndexSerializer
from .models import SitemapIndex
from api.authenticate.models import PublishableToken


def hello_world(request):
    return JsonResponse({"message": "hello world"})


@method_decorator(csrf_exempt, name="dispatch")
class ReceiveData(View):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            data = json.loads(request.body)
            print(data)  # Imprime la información recibida
            return JsonResponse({"status": "success", "data": data})
        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON"}, status=400
            )


@method_decorator(csrf_exempt, name="dispatch")
class SuggestionsView(View):
    permission_classes = [AllowAny]

    def get(self, request, article_id=None):
        if article_id:
            article = get_object_or_404(Article, id=article_id)
            pending_suggestions = Suggestion.objects.filter(
                article=article, status=Suggestion.PENDING
            )
            if pending_suggestions.exists():
                # suggestion = random.choice(pending_suggestions)
                article_serializer = ArticleSerializer(article)
                # suggestion_serializer = SuggestionSerializer(suggestion)
                suggestions_data = []

                for suggestion in pending_suggestions:
                    suggestion_serializer = SuggestionSerializer(suggestion)
                    suggestions_data.append(suggestion_serializer.data)

                return JsonResponse(
                    {
                        "article": article_serializer.data,
                        "suggestion": suggestions_data,
                    }
                )
            else:
                return JsonResponse(
                    {"message": "No pending suggestions found for this article."},
                    status=404,
                )
        else:
            articles = Article.objects.all()
            response_data = []
            for article in articles:
                suggestions_count = Suggestion.objects.filter(article=article).count()
                if suggestions_count > 0:
                    article_serializer = ArticleSerializer(article)
                    response_data.append(
                        {
                            "article": article_serializer.data,
                            "suggestions": suggestions_count,
                        }
                    )
            return JsonResponse(response_data, safe=False)

    def put(self, request, article_slug):
        try:
            data = json.loads(request.body)
            new_status = data.get("new_status")
            suggestion_id = data.get("suggestion_id")
            article_content = data.get("article_content", "")

            if new_status not in [Suggestion.REJECTED, Suggestion.ACCEPTED]:
                return JsonResponse({"message": "Invalid status."}, status=400)

            suggestion = get_object_or_404(
                Suggestion, id=suggestion_id, article__slug=article_slug
            )

            suggestion.status = new_status
            suggestion.save()

            if new_status == Suggestion.ACCEPTED and article_content:
                article = suggestion.article
                article.content = article_content
                article.save()

            return JsonResponse({"message": "Suggestion updated successfully."})

        except json.JSONDecodeError:
            return JsonResponse({"message": "Invalid JSON."}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class SitemapIndexView(View):
    permission_classes = [AllowAny]

    def get(self, request):
        sitemaps = SitemapIndex.objects.all()
        data = serialize("json", sitemaps)
        return JsonResponse(data, safe=False)

    def post(self, request):
        data = json.loads(request.body)
        sitemap = SitemapIndex.objects.create(**data)
        return JsonResponse({"id": sitemap.id})


def is_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


@method_decorator(csrf_exempt, name="dispatch")
class PublicSitemapIndexView(View):
    permission_classes = [AllowAny]

    def get(self, request, token):

        sitemaps = SitemapIndex.objects.filter(publish_token__token=token)
        if not sitemaps.exists():
            return JsonResponse({"error": "Invalid token"}, status=404)

        data = SitemapIndexSerializer(sitemaps, many=True).data
        return JsonResponse(data, safe=False)

    def post(self, request):
        data = json.loads(request.body)
        url = data.get("url")
        print(data, "RECEIVED DATA")
        # CHeck if the url is indeed an url
        if not url or not is_url(url):
            return JsonResponse({"error": "A valid URL is required"}, status=400)

        p = PublishableToken.create_token()
        sitemap = SitemapIndex.objects.create(url=url, publish_token=p, last_sync=None)
        return JsonResponse({"id": sitemap.id, "publish_token": p.token})


@method_decorator(csrf_exempt, name="dispatch")
class PublicArticleFetcher(View):
    permission_classes = [AllowAny]

    def post(self, request):
        data = json.loads(request.body)
        article_id = data.get("article_id")
        a = Article.objects.get(id=article_id)
        a.fetch_content()
        a.suggest_linking()
        return JsonResponse({"message": "Ready to magic"})
