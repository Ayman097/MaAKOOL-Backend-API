# Generated by Django 4.2.7 on 2023-11-17 12:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='is_deleted',
            field=models.BooleanField(default=False),
        ),
    ]
