# Generated by Django 4.1.13 on 2024-08-29 10:23

from django.db import migrations, models
import site_settings.models


class Migration(migrations.Migration):

    dependencies = [
        ('site_settings', '0005_sitesettings_meal_sunday_evening_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='sitesettings',
            name='favicon',
            field=models.FileField(blank=True, help_text='Icône du site, image au format .ico', null=True, storage=site_settings.models.OverwriteStorage('favicon'), upload_to='', verbose_name='Favicon'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='logo',
            field=models.FileField(blank=True, help_text='Apparait dans le header', null=True, storage=site_settings.models.OverwriteStorage('LogoInterludes'), upload_to='', verbose_name='Logo'),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='notify_on_activity_submission',
            field=models.BooleanField(default=True, help_text="Envoie un email (à l'email de contact) lorsqu'une nouvelle activité est ajoutée via le formulaire.", verbose_name="Notification d'ajout d'activité"),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='orga_planning_notified',
            field=models.DateTimeField(blank=True, help_text="Email donnant aux organisateurs d'activité leurs créneaux. Ce champ existe pour éviter l'envoie de plusieurs mails successifs. Mettez le à vide pour ré-envoyer un email", null=True, verbose_name="Dernier envoie de l'email communiquant leurs créneaux aux orgas"),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='sleep_host_link',
            field=models.URLField(blank=True, null=True, verbose_name="Lien du formulaire de proposition d'hébergement"),
        ),
        migrations.AddField(
            model_name='sitesettings',
            name='sleeper_link',
            field=models.URLField(blank=True, null=True, verbose_name="Lien du formulaire de demande d'hébergement"),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='discord_link',
            field=models.URLField(blank=True, null=True, verbose_name='Lien du serveur discord'),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='hosting_school',
            field=models.CharField(choices=[('U', 'ENS Ulm'), ('L', 'ENS Lyon'), ('R', 'ENS Rennes'), ('C', 'ENS Paris Saclay')], default='U', max_length=1, verbose_name="École hébergeant l'événement"),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='orga_notified',
            field=models.DateTimeField(blank=True, help_text="Email donnant à chaque orga d'activité (qui le demande) la liste des participants inscrit à son activite. Ce champ existe pour éviter l'envoie de plusieurs mails successifs. Mettez le à vide pour ré-envoyer un email", null=True, verbose_name="Dernier envoie de l'email de liste des participants"),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='ticket_url',
            field=models.URLField(blank=True, max_length=300, null=True, verbose_name='Lien billeterie'),
        ),
        migrations.AlterField(
            model_name='sitesettings',
            name='user_notified',
            field=models.DateTimeField(blank=True, help_text="Email donnant à chaque participant la liste des activités qu'il a obtenu. Ce champ existe pour éviter l'envoie de plusieurs mails successifs. Mettez le à vide pour ré-envoyer un email", null=True, verbose_name="Dernier envoie de l'email de répartition des activités"),
        ),
    ]