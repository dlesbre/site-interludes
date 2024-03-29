# Generated by Django 4.1.9 on 2023-10-03 14:26

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("site_settings", "0004_sitesettings_affiche_sitesettings_ticket_url_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="meal_sunday_evening",
            field=models.BooleanField(
                default=True, verbose_name="Repas dimanche soir (à emporter)"
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="menu_friday_evening",
            field=models.CharField(
                blank=True,
                default="",
                max_length=400,
                verbose_name="Menu du repas de vendredi soir",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="menu_saturday_evening",
            field=models.CharField(
                blank=True,
                default="",
                max_length=400,
                verbose_name="Menu du repas de samedi soir",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="menu_saturday_midday",
            field=models.CharField(
                blank=True,
                default="",
                max_length=400,
                verbose_name="Menu du repas de samedi midi",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="menu_saturday_morning",
            field=models.CharField(
                blank=True,
                default="",
                max_length=400,
                verbose_name="Menu du repas de samedi matin",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="menu_sunday_evening",
            field=models.CharField(
                blank=True,
                default="",
                max_length=400,
                verbose_name="Menu du repas de dimanche soir",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="menu_sunday_midday",
            field=models.CharField(
                blank=True,
                default="",
                max_length=400,
                verbose_name="Menu du repas de dimanche midi",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="menu_sunday_morning",
            field=models.CharField(
                blank=True,
                default="",
                max_length=400,
                verbose_name="Menu du repas de dimanche matin",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="price_entry_paid",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=5,
                verbose_name="prix d'inscription (salarié)",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="price_entry_unpaid",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=5,
                verbose_name="prix d'inscription (non-salarié)",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="price_meal_paid",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=5,
                verbose_name="prix d'un repas (salarié)",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="price_meal_unpaid",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=5,
                verbose_name="prix d'un repas (non-salarié)",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="price_sleep_paid",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=5,
                verbose_name="prix d'hébergement (salarié)",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="price_sleep_unpaid",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=5,
                verbose_name="prix d'hébergement (non-salarié)",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="price_sunday_meal_paid",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=5,
                verbose_name="prix du repas du dimanche soir (salarié)",
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="price_sunday_meal_unpaid",
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=5,
                verbose_name="prix du repas du dimanche soir (non-salarié)",
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="activities_allocated",
            field=models.BooleanField(
                default=False,
                help_text="Une fois que l'allocation des activités a été effectuée.",
                verbose_name="Afficher les activités obtenues",
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="activity_submission_open",
            field=models.BooleanField(
                default=False,
                help_text="Permet de proposer une activité via le formulaire dédié. Nécessite d'ouvrir la création de comptes.",
                verbose_name="Ouvrir l'ajout d'activité",
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="global_message",
            field=models.TextField(
                blank=True,
                help_text='Message affiché en haut de chaque page (si non vide). Vous pouvez également modifier le contenu de certaines pages depuis "Pages HTML"',
                null=True,
                verbose_name="Message global",
            ),
        ),
        migrations.AlterField(
            model_name="sitesettings",
            name="show_host_emails",
            field=models.BooleanField(
                default=False,
                help_text="Ces mail sont affichés sur la page activités pour qu'ils puissent être contactés",
                verbose_name="Afficher les mails des orgas d'activités",
            ),
        ),
    ]
