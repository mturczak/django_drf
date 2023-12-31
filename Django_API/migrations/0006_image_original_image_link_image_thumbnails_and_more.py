# Generated by Django 4.2.5 on 2023-10-16 11:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('Django_API', '0005_alter_image_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='original_image_link',
            field=models.URLField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='image',
            name='thumbnails',
            field=models.JSONField(blank=True, null=True),
        ),
        migrations.AlterField(
            model_name='thumbnail',
            name='parent_image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='image_thumbnails', to='Django_API.image'),
        ),
    ]
