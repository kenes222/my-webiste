# Generated by Django 5.0.6 on 2024-06-16 06:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('give', '0010_remove_post_city_remove_post_country_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='photos',
            field=models.ManyToManyField(related_name='posts', to='give.photo'),
        ),
    ]
