# Generated by Django 5.1.1 on 2024-09-24 22:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('seo', '0007_alter_suggestion_status'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suggestion',
            name='status',
            field=models.CharField(choices=[('REJECTED', 'Rejected'), ('ACCEPTED', 'Accepted'), ('PENDING', 'Pending')], default='PENDING', max_length=8),
        ),
    ]
