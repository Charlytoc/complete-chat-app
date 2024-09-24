import logging
from celery import shared_task
from .actions import (
    get_all_urls_from_sitemap,
    fetch_asset_data,
    create_article_from_json,
    get_last_part_of_url
)
from .models import Sitemap

logger = logging.getLogger(__name__)


@shared_task
def async_fetch_article(sitemap_url: str, article_url: str):
    slug = get_last_part_of_url(article_url)
    sitemap = Sitemap.objects.get(url=sitemap_url)
    data = fetch_asset_data(slug)
    data["url"] = article_url
    create_article_from_json(sitemap, data)


@shared_task
def async_create_article_from_sitemap(sitemap_url: str):

    urls = get_all_urls_from_sitemap(sitemap_url)
    for u in urls:
        async_fetch_article.delay(sitemap_url=sitemap_url, article_url=u)
