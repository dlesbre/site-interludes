# Generated by Django 3.2.16 on 2022-11-15 09:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_auto_20221108_1943'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activitymodel',
            name='status',
            field=models.CharField(blank=True, choices=[('P', 'En présentiel uniquement'), ('D', 'En distanciel uniquement'), ('2', 'Les deux')], default='P', max_length=1, verbose_name='Présentiel/distanciel'),
        ),
    ]
