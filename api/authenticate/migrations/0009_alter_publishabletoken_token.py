# Generated by Django 5.1.1 on 2024-09-24 21:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authenticate', '0008_alter_publishabletoken_token'),
    ]

    operations = [
        migrations.AlterField(
            model_name='publishabletoken',
            name='token',
            field=models.CharField(default='19e909a1a9054d4d878c18bdb61f90be', max_length=255, unique=True),
        ),
    ]
