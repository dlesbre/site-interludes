# Generated by Django 3.2.7 on 2021-09-13 18:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import home.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ActivityModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('display', models.BooleanField(default=False, help_text="Si vrai, s'affiche sur la page activités", verbose_name='afficher dans la liste')),
                ('title', models.CharField(max_length=200, verbose_name='Titre')),
                ('act_type', models.CharField(choices=[('1 partie', 'Une partie'), ('2+ parties', 'Quelques parties'), ('Tournoi', 'Tournoi'), ('freeplay', 'Freeplay'), ('other', 'Autre')], max_length=12, verbose_name="Type d'activité")),
                ('game_type', models.CharField(choices=[('jeu cartes', 'Jeu de cartes'), ('jeu plateau', 'Jeu de société'), ('table RPG', 'Jeu de rôle sur table'), ('large RPG', 'Jeu de rôle grandeur nature'), ('videogame', 'Jeu vidéo'), ('partygame', 'Party game'), ('puzzle', 'Puzzle ou analogue'), ('secret roles', 'Jeu à rôles secrets'), ('coop', 'Jeu coopératif'), ('other', 'Autre')], max_length=12, verbose_name='Type de jeu')),
                ('description', models.TextField(help_text='Texte ou html selon la valeur de "Description HTML".\n', max_length=10000, verbose_name='description')),
                ('desc_as_html', models.BooleanField(default=False, help_text='Assurer vous que le texte est bien formaté, cette option peut casser la page activités.', verbose_name='Description au format HTML')),
                ('host_name', models.CharField(blank=True, help_text='Peut-être laissé vide pour des simples activités sans orga', max_length=50, null=True, verbose_name="nom de l'organisateur")),
                ('host_email', models.EmailField(help_text='Utilisé pour communiquer la liste des participants si demandé', max_length=254, verbose_name="email de l'organisateur")),
                ('host_info', models.TextField(blank=True, max_length=1000, null=True, verbose_name='Autre orgas/contacts')),
                ('must_subscribe', models.BooleanField(default=False, help_text="Informatif, il faut utiliser les créneaux pour ajouter dans la liste d'inscription", verbose_name='sur inscription')),
                ('communicate_participants', models.BooleanField(verbose_name="communiquer la liste des participants à l'orga avant l'événement")),
                ('max_participants', models.PositiveIntegerField(default=0, help_text='0 pour illimité', verbose_name='Nombre maximum de participants')),
                ('min_participants', models.PositiveIntegerField(default=0, verbose_name='Nombre minimum de participants')),
                ('duration', models.DurationField(help_text='format hh:mm:ss', verbose_name='Durée')),
                ('desired_slot_nb', models.PositiveIntegerField(default=1, validators=[home.models.validate_nonzero], verbose_name='Nombre de créneaux souhaités')),
                ('available_friday_evening', models.CharField(choices=[('0', 'Idéal'), ('1', 'Acceptable'), ('2', 'Indisponible')], default='1', max_length=1, verbose_name='Crénau vendredi soir')),
                ('available_friday_night', models.CharField(choices=[('0', 'Idéal'), ('1', 'Acceptable'), ('2', 'Indisponible')], default='1', max_length=1, verbose_name='Crénau vendredi nuit')),
                ('available_saturday_morning', models.CharField(choices=[('0', 'Idéal'), ('1', 'Acceptable'), ('2', 'Indisponible')], default='1', max_length=1, verbose_name='Crénau samedi matin')),
                ('available_saturday_afternoon', models.CharField(choices=[('0', 'Idéal'), ('1', 'Acceptable'), ('2', 'Indisponible')], default='1', max_length=1, verbose_name='Crénau samedi après-midi')),
                ('available_saturday_evening', models.CharField(choices=[('0', 'Idéal'), ('1', 'Acceptable'), ('2', 'Indisponible')], default='1', max_length=1, verbose_name='Crénau samedi soir')),
                ('available_saturday_night', models.CharField(choices=[('0', 'Idéal'), ('1', 'Acceptable'), ('2', 'Indisponible')], default='1', max_length=1, verbose_name='Crénau samedi nuit')),
                ('available_sunday_morning', models.CharField(choices=[('0', 'Idéal'), ('1', 'Acceptable'), ('2', 'Indisponible')], default='1', max_length=1, verbose_name='Crénau dimanche matin')),
                ('available_sunday_afternoon', models.CharField(choices=[('0', 'Idéal'), ('1', 'Acceptable'), ('2', 'Indisponible')], default='1', max_length=1, verbose_name='Crénau dimanche après-midi')),
                ('constraints', models.TextField(blank=True, max_length=2000, null=True, verbose_name='Contraintes particulières')),
                ('status', models.CharField(choices=[('P', 'En présentiel uniquement'), ('D', 'En distanciel uniquement'), ('2', 'Les deux')], max_length=1, verbose_name='Présentiel/distanciel')),
                ('needs', models.TextField(blank=True, max_length=2000, null=True, verbose_name='Besoin particuliers')),
                ('comments', models.TextField(blank=True, max_length=2000, null=True, verbose_name='Commentaires')),
                ('host', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL, verbose_name='Organisateur')),
            ],
            options={
                'verbose_name': 'activité',
            },
        ),
        migrations.CreateModel(
            name='SlotModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(default='{act_title}', help_text="Utilisez '{act_title}' pour insérer le titre de l'activité correspondante", max_length=200, verbose_name='Titre')),
                ('start', models.DateTimeField(verbose_name='début')),
                ('duration', models.DurationField(blank=True, help_text="Format 00:00:00. Laisser vide pour prendre la durée de l'activité correspondante", null=True, verbose_name='durée')),
                ('room', models.CharField(blank=True, max_length=100, null=True, verbose_name='salle')),
                ('on_planning', models.BooleanField(default=False, help_text='Nécessite de salle et heure de début non vide', verbose_name='afficher sur le planning')),
                ('subscribing_open', models.BooleanField(default=False, help_text="Si vrai, apparaît dans la liste du formulaire d'inscription", verbose_name='ouvert aux inscriptions')),
                ('color', models.CharField(choices=[('a', 'Rouge'), ('b', 'Orange'), ('c', 'Jaune'), ('d', 'Vert'), ('e', 'Bleu'), ('f', 'Bleu foncé'), ('g', 'Noir')], default='f', help_text='La légende des couleurs est modifiable dans les paramètres', max_length=1, verbose_name='Couleur')),
                ('activity', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.activitymodel', verbose_name='Activité')),
            ],
            options={
                'verbose_name': 'créneau',
                'verbose_name_plural': 'créneaux',
            },
        ),
        migrations.CreateModel(
            name='ParticipantModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_registered', models.BooleanField(default=False, verbose_name='est inscrit')),
                ('meal_friday_evening', models.BooleanField(default=False, verbose_name='repas de vendredi soir')),
                ('meal_saturday_morning', models.BooleanField(default=False, verbose_name='repas de samedi matin')),
                ('meal_saturday_midday', models.BooleanField(default=False, verbose_name='repas de samedi midi')),
                ('meal_saturday_evening', models.BooleanField(default=False, verbose_name='repas de samedi soir')),
                ('meal_sunday_morning', models.BooleanField(default=False, verbose_name='repas de dimanche matin')),
                ('meal_sunday_midday', models.BooleanField(default=False, verbose_name='repas de dimanche soir')),
                ('sleeps', models.BooleanField(default=False, verbose_name='dormir sur place')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='Utilisateur', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'participant',
            },
        ),
        migrations.CreateModel(
            name='ActivityChoicesModel',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('priority', models.PositiveIntegerField(verbose_name='priorité')),
                ('accepted', models.BooleanField(default=False, verbose_name='Obtenue')),
                ('participant', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.participantmodel', verbose_name='participant')),
                ('slot', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.slotmodel', verbose_name='créneau')),
            ],
            options={
                'verbose_name': "choix d'activités",
                'verbose_name_plural': "choix d'activités",
                'ordering': ('participant', 'priority'),
                'unique_together': {('priority', 'participant'), ('participant', 'slot')},
            },
        ),
    ]
