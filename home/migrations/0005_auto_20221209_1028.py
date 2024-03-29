# Generated by Django 3.2.16 on 2022-12-09 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0004_participantmodel_paid'),
    ]

    operations = [
        migrations.AddField(
            model_name='participantmodel',
            name='meal_sunday_evening',
            field=models.BooleanField(default=False, verbose_name='repas de dimanche soir'),
        ),
        migrations.AlterField(
            model_name='participantmodel',
            name='meal_sunday_midday',
            field=models.BooleanField(default=False, verbose_name='repas de dimanche midi'),
        ),
    ]
