# Generated by Django 3.0.14 on 2022-05-27 13:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0006_auto_20220527_1121'),
    ]

    operations = [
        migrations.AlterField(
            model_name='rating',
            name='rate',
            field=models.FloatField(),
        ),
    ]