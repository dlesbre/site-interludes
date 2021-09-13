# Site des interludes

Ce répo contient le sites des interludes. Ce site est en ligne à [https://interludes.ens.fr](https://interludes.ens.fr).

Ce répo est diffusé sous une [license MIT](https://choosealicense.com/licenses/mit/).

**Contenu:**
- [Lancement rapide](#lancement-rapide)
- [Installation](#installation)
- [Lancer le serveur](#lancer-le-serveur)
- [Guide de l'administrateur](#guide-de-ladministrateur)
- [En production](#en-production)
- [Idées de développement](#idées-de-développement)
- [Liens divers](#liens-divers)

## Lancement rapide

Pour installer toutes les dépendances et lancer le serveur :

		git clone https://git.eleves.ens.fr/dlesbre/site-interludes.git &&
		cd site-interlude &&
		python3 -m venv venv &&
		source venv/bin/activate &&
		make start

Le site devrait être accessible à [http://localhost:8000](http://localhost:8000).

Par la suite vous pouver relancer le site simplement avec `make serve`.

## Installation

Pour tester et modifier le repo, après l'avoir cloné :

1. Créer un [environement
   virtuel](https://docs.python.org/3/tutorial/venv.html) (`python3-venv`)

		python3 -m venv venv

	(si vous le nommez autre chose que venv, ajouter le dossier correspondant
    au `.gitignore`)

2. Lancer l'environnement virtuel

		source venv/bin/activate

3. Installer la dernière version de pip

		python3 -m pip install --upgrade pip

4. Installer les requirements

		pip3 install -r requirements.txt

5. Copier/linker le fichier `interludes/secret_example.py` dans `interludes/secret.py`

		ln -s interludes/secret_example.py interludes/secret.py

6. Faire les les migrations

		make migrate

## Lancer le serveur

Pour pouvoir afficher et tester le site (après avoir tout installé)

1. Lancer l'environnement virtuel si ce n'est pas déjà fait (si le prompt du
   terminal ne commence pas par `(venv)`)

		source venv/bin/activate

2. Lancer le serveur avec `make serve` ou

		make serve

	Cette commande bloque le terminal, le serveur tourne tant qu'elle n'est pas
	interrompue (par `Ctrl+C` ou autre).

3. Dans un navigateur, le site se trouve à l'adresse
   [http://localhost:8000/](http://localhost:8000/)

4. Créer un compte super-utilisateur avec `make adduser`. Les réglages se modifient depuis les pages d'admin de Django [http://localhost:8000/admin](http://localhost:8000/admin).

## Guide de l'administrateur

Le site se gère depuis deux pages d'administration:

- celle de django [http://localhost:8000/admin](http://localhost:8000/admin) permet de modifier directement la base de donnée. Celle ci contient six tables intéressantes :
	- Utilisateurs - contient tous les utilisateurs et leur permissions. Pour donner les droits d'administrateur à quelqu'un il faut lui donner le statut superutilisateur (accès à l'admin du site) ET le statut équipe (accès à l'admin django)
	- Paramêtres - les réglages du site, ils permettent:
		- ouvrir/fermer la création de compte, les inscriptions
		- ouvrir fermer le formulaire de proposition d'activités
		- afficher/cacher le planning
		- renseigner l'email de contact, les dates de l'événement, les dates d'inscription
		- ajouter un message global au dessus de toutes les pages
		- bloquer/autoriser l'envoi d'email globaux
	- Activités - liste des activités prévues. C'est ici que vous pouvez rajouter/modifier les activités qui s'affichent sur la page activité.
		Un formulaire permet aux utilisateurs de proposer des activités directement. Ils vous faudra les relire et les valider ensuite manuellement pour qu'elles soient affichées sur le site.
	- Crénaux - place une activité sur le planning. Une activité peut avoir plusieurs crénaux si elle a lieu plusieurs fois. Noter que les inscriptions se font à des crénaux et non a des activités.
	- Participant - liste des gens inscrits et des informations sur leur inscription (ENS, repas choisi...)
	- Choix d'activité - Liste de (participant, priorité, activité) indiquant les voeux des participant. Une fois que vous avez fait l'attribution, cocher les case "Obtenues" pour indiquer qui a eu quelle activité.

- celle du site [http://localhost:8000/admin_pages/](http://localhost:8000/admin_pages/)
	- permet d'exporter les différentes tables au format CSV
	- affiche l'état du site (version, réglages actuels, différentes métriques)
	- une prévisualisation du planning
	- permet d'envoyer deux séries d'emails :
		- une aux inscrits pour leur communiquer les activités qu'ils ont obtenus
		- une aux orgas qui ont besoin de connaître la liste des participants à l'avance pour préparer leurs activités.
	- permet l'écriture d'un mail à tous.

## En production

Le serveur a besoin d'être configuré pour HTTPS et d'être configuré pour livrer directement les fichiers situés des `/static/`.

1. Installer les dépendances `make install`

2. S'assurer que `DEBUG = False` et que `ALLOWED_HOSTS` contient les adresses des hôtes dans [settings.py](./interludes/settings.py)

3. Créer ou remplacer le fichier `interludes/secret.py` pour qu'il ait les mots de passe et un nouveau secret. Vous pouvez générer un secret django avec

		python manage.py shell -c 'from django.core.management import utils; print(utils.get_random_secret_key())'

4. Faire les migration `make migrate`

5. Faire un `make preprod` pour générer les fichiers statiques et vérifier les réglages

## Idées de développement

A.K.A. la liste des trucs utiles que j'ai pas eu le temps d'ajouter

- Intégrer l'[algorithme de répartition](https://github.com/Imakoala/InterludesMatchings) dans le site au lieu de le faire tourner en externe à partir des export CSV et de remplir les résultats à la main
- Envoyer une concaténation de tous les emails aux admin (pour vérification, et pas juste en copie pour éviter le spam...)
- Générer la version PDF du planning automatiquement au lieu de la faire à base de captures d'écran
- Remplacer les templates HTML statiques par du rendu de fichier markdown éditable depuis la page d'admin (afin d'éviter de devoir refaire un pull à chaque petit changement)

## Liens divers

- [Le site des interludes 2021](https://interludes.ens.fr)
- [Le github de l'algorithme de répartition](https://github.com/Imakoala/InterludesMatchings)
- [Le wiki de Paris-Saclay](https://wiki.crans.org/VieBdl/InterLudes) qui recensent les visuels, sites webs et photos des interludes passées.
