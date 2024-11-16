# Generated by Django 4.2.16 on 2024-11-16 11:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('site_settings', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='SponsorModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text="L'affichage des sponsors se fait par order alphabétique", max_length=100, verbose_name='nom')),
                ('display', models.BooleanField(default=False, verbose_name='Affiché')),
                ('image', models.FileField(upload_to='', verbose_name='logo')),
                ('url', models.URLField(verbose_name='lien')),
                ('alt_text', models.CharField(help_text="S'affiche si l'image ne peut pas être chargée", max_length=100, verbose_name='alt-text')),
            ],
            options={
                'verbose_name': 'sponsor',
                'verbose_name_plural': 'sponsors',
                'ordering': ('name',),
            },
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='option1_description',
            field=models.CharField(blank=True, help_text="ex: 'Adhérent du COF', 'Commande un Mug'...", max_length=200, null=True, verbose_name='Description Option 1'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='option1_enable',
            field=models.BooleanField(default=False, verbose_name='Option 1'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='option2_description',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Description Option 2'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='option2_enable',
            field=models.BooleanField(default=False, verbose_name='Option 2'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='option3_description',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Description Option 3'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='option3_enable',
            field=models.BooleanField(default=False, verbose_name='Option 3'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='option4_description',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Description Option 4'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='option4_enable',
            field=models.BooleanField(default=False, verbose_name='Option 4'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='option5_description',
            field=models.CharField(blank=True, max_length=200, null=True, verbose_name='Description Option 5'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='option5_enable',
            field=models.BooleanField(default=False, verbose_name='Option 5'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='price_option1_paid',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='prix option 1 (salarié)'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='price_option1_unpaid',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='prix option 1 (non-salarié)'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='price_option2_paid',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='prix option 2 (salarié)'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='price_option2_unpaid',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='prix option 2 (non-salarié)'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='price_option3_paid',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='prix option 3 (salarié)'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='price_option3_unpaid',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='prix option 3 (non-salarié)'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='price_option4_paid',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='prix option 4 (salarié)'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='price_option4_unpaid',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='prix option 4 (non-salarié)'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='price_option5_paid',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='prix option 5 (salarié)'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='price_option5_unpaid',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=5, verbose_name='prix option 5 (non-salarié)'),
        ),
    ]
