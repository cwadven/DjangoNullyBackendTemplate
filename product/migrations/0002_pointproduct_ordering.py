# Generated by Django 4.1.10 on 2023-12-31 11:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('product', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='pointproduct',
            name='ordering',
            field=models.PositiveIntegerField(db_index=True, default=0, verbose_name='순서'),
        ),
    ]
