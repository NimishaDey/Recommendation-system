# Generated by Django 3.0.14 on 2022-05-29 17:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('polls', '0011_profile'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Profile',
        ),
    ]
