from rest_framework import serializers
from .models import Article, Suggestion, SitemapIndex, Sitemap


class ArticleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Article
        fields = "__all__"


class SuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suggestion
        fields = "__all__"


class SitemapSerializer(serializers.ModelSerializer):
    articles = serializers.SerializerMethodField()

    class Meta:
        model = Sitemap
        fields = "__all__"

    def get_articles(self, obj):
        articles = Article.objects.filter(sitemap=obj)
        return ArticleSerializer(articles, many=True).data


class SitemapIndexSerializer(serializers.ModelSerializer):
    sitemaps = serializers.SerializerMethodField()

    class Meta:
        model = SitemapIndex
        fields = "__all__"

    def get_sitemaps(self, obj):
        # Fetch related sitemaps using the reverse relationship
        sitemaps = Sitemap.objects.filter(index=obj)
        return SitemapSerializer(sitemaps, many=True).data
