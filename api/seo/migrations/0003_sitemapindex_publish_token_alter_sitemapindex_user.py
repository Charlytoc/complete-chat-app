# Generated by Django 5.1.1 on 2024-11-06 18:24

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authenticate', '0017_alter_publishabletoken_token'),
        ('seo', '0002_article_article_content_md'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='sitemapindex',
            name='publish_token',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='authenticate.publishabletoken'),
        ),
        migrations.AlterField(
            model_name='sitemapindex',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
