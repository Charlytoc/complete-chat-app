from django.urls import path
from .views import hello_world, ReceiveData, SuggestionsView, PublicSitemapIndexView, PublicArticleFetcher

app_name = "seo"

urlpatterns = [
    path("hello_world", hello_world, name="hello_world"),
    path("article", ReceiveData.as_view(), name="article"),
    path("suggestions", SuggestionsView.as_view(), name="suggestions"),
    path(
        "suggestions/<str:article_id>/",
        SuggestionsView.as_view(),
        name="suggestion_detail",
    ),
    path(
        "public/sitemap-index",
        PublicSitemapIndexView.as_view(),
        name="public_sitemap",
    ),
    path(
        "public/sitemap-index/<str:token>",
        PublicSitemapIndexView.as_view(),
        name="public_sitemap_token",
    ),
    path(
        "public/fetch-article",
        PublicArticleFetcher.as_view(),
        name="public_fetch_article",
    ),

]
