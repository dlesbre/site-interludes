# Generated by Django 4.1.1 on 2022-09-10 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pages', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='htmlpagemodel',
            name='visible',
            field=models.BooleanField(default=True, help_text='Décochez pour cacher la page sans pour autant la supprimer'),
        ),
        migrations.AlterField(
            model_name='htmlpagemodel',
            name='slug',
            field=models.SlugField(blank=True, help_text="Url de la page (laisser vide pour la page d'acceuil)", unique=True, verbose_name='url'),
        ),
    ]