# Generated by Django 3.0.14 on 2022-05-28 05:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0007_auto_20220527_1843'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rating',
            name='rate',
            field=models.FloatField(default=0.0),
        ),
    ]
