# Generated by Django 5.1.1 on 2024-10-12 13:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seo', '0009_systempromptmodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='academy_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
