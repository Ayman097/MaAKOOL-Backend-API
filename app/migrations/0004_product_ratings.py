# Generated by Django 4.2.7 on 2023-11-24 00:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_offer_is_deleted'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='ratings',
            field=models.DecimalField(decimal_places=1, default=0, max_digits=3),
        ),
    ]
