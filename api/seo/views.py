from django.http import JsonResponse
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
from .serializers import ArticleSerializer, SuggestionSerializer

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

    def get(self, request, article_slug=None):
        if article_slug:
            article = get_object_or_404(Article, slug=article_slug)
            pending_suggestions = Suggestion.objects.filter(
                article=article, status=Suggestion.PENDING
            )
            if pending_suggestions.exists():
                suggestion = random.choice(pending_suggestions)
                article_serializer = ArticleSerializer(article)
                suggestion_serializer = SuggestionSerializer(suggestion)
                return JsonResponse(
                    {
                        "article": article_serializer.data,
                        "suggestion": suggestion_serializer.data,
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

    def put(self, request, article_slug, suggestion_id):
        try:
            data = json.loads(request.body)
            new_status = data.get("new_status")
            article_content = data.get("article_content")

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
