# Generated by Django 3.2.9 on 2021-11-07 19:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('site_settings', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettings',
            name='hosting_school',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name="École hébergeant l'événement"),
        ),
    ]