# Generated by Django 5.0.4 on 2024-04-27 03:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0014_alter_posts_postid'),
    ]

    operations = [
        migrations.AlterField(
            model_name='suburbs',
            name='CBD',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='suburbs',
            name='Latitude',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='suburbs',
            name='Len',
            field=models.FloatField(),
        ),
        migrations.AlterField(
            model_name='suburbs',
            name='Longitude',
            field=models.FloatField(),
        ),
    ]
