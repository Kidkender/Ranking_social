# Generated by Django 5.0.4 on 2024-04-22 03:30

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0010_suburbs_alter_posts_countcomment_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='suburbs',
            old_name='len',
            new_name='Len',
        ),
        migrations.RenameField(
            model_name='suburbs',
            old_name='PostCode',
            new_name='Postcode',
        ),
        migrations.RemoveField(
            model_name='suburbs',
            name='is_old',
        ),
        migrations.AddField(
            model_name='suburbs',
            name='id_old',
            field=models.IntegerField(default=0, validators=[django.core.validators.MinValueValidator(0, 'Value must be non-negative')]),
        ),
    ]
