# Generated by Django 4.2.13 on 2024-06-24 13:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0005_review_created_at'),
    ]

    operations = [
        migrations.RenameField(
            model_name='review',
            old_name='rating',
            new_name='taste_rating',
        ),
        migrations.AddField(
            model_name='review',
            name='delivery_rating',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='review',
            name='service_rating',
            field=models.IntegerField(default=1),
            preserve_default=False,
        ),
    ]
