from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Article, SitemapIndex, Sitemap

# TODO: Investigate how signals works in Django and add a post_save signal to the article model and print its new content

# TODO: For another moment
# https://documenter.getpostman.com/view/2432393/T1LPC6ef#41478cbd-3073-4d63-8d27-df51c268fdd0

"""
We will sent a PUT request to that endpoint to update the article in the breathecode API
"""


@receiver(post_save, sender=SitemapIndex)
def sync_sitemap_index(sender, instance, created, **kwargs):
    if created:
        print(f"New sitemap index created: {instance.url}")
        result = instance.get_sitemaps()
        if not result:
            raise Exception("Error while syncing sitemap")


@receiver(post_save, sender=Sitemap)
def sync_sitemap(sender, instance, created, **kwargs):
    if created:
        print(f"Fetching articles for sitemap: {instance.url}")
        instance.get_urls()
