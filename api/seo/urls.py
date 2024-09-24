from django.urls import path
from .views import hello_world, ReceiveData, SuggestionsView

app_name = "seo"

urlpatterns = [
    path("hello_world", hello_world, name="hello_world"),
    path("article", ReceiveData.as_view(), name="article"),
    path("suggestions", SuggestionsView.as_view(), name="suggestions"),
    path(
        "suggestions/<str:article_slug>/",
        SuggestionsView.as_view(),
        name="suggestion_detail",
    ),
]
