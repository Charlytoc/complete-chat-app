# Generated by Django 5.1.1 on 2024-09-23 08:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('messaging', '0002_conversation_public_token_alter_conversation_user'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='attachments',
            field=models.JSONField(blank=True, default=list),
        ),
    ]
