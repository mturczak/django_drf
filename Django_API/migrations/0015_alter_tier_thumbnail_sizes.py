# Generated by Django 4.2.5 on 2023-10-18 21:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Django_API', '0014_alter_tier_thumbnail_sizes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='tier',
            name='thumbnail_sizes',
            field=models.JSONField(),
        ),
    ]
