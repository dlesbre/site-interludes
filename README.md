# Site des interludes

Ce répo contient le sites des interludes. La version 2021 est en ligne à
[https://interludes.ens.fr](https://interludes.ens.fr). Il est disponible sur le
[git interne de l'ENS Ulm](https://git.eleves.ens.fr/dlesbre/site-interludes) et
sur [github](https://github.com/dlesbre/site-interludes). Il est diffusé sous
une [license MIT](https://choosealicense.com/licenses/mit/).

**Ce site permet de :**
- Afficher de l'information sur l'événement (page d'accueil et FAQ, modifiable
  directement depuis l'admin du site)
- Recenser es activités proposées (page activités)
- Un formulaire pour permettre aux gens de proposer des activités
- Un formulaire d'inscription ou chaque inscrit peut renseigner des infos
  personnelles (repas/dormir) et les activités qu'il souhaite
- Afficher un planning dynamique des différentes activités
- Une fois la répartition faite, envoyer un mail à tous les inscrits pour leur
  communiquer les activités obtenu et un mail aux orgas pour leur communiquer la
  liste des participants
- Un formulaire pour envoyer un mail à tous (à utiliser avec modération)
- Exporter les tables intéressantes au format CSV


**Il n'est PAS capable de :**
- vendre des tickets - pour le faire il faut soit utiliser une billetterie
  externe (ex [HelloAsso](https://www.helloasso.com/)) ou de recruter les
  BdE/BdL des autres écoles pour qu'ils inscrivent les participants
- répartir les activités - nous faisons un premier jet avec le [ce
  code](https://github.com/Lamakaio/InterludesMatchings) (en prenant l'export
  CSV de la table de choix d'activités), puis l'adaptons à la main et le
  renseignons dans ce site.

**Contenu:**
- [Lancement rapide](#lancement-rapide)
- [Installation manuelle](#installation-manuelle)
- [Lancer le serveur](#lancer-le-serveur)
- [Guide de l'administrateur](#guide-de-ladministrateur)
- [En production](#en-production)
- [Idées de développement](#idées-de-développement)
- [Liens divers](#liens-divers)

## Lancement rapide

Pour installer toutes les dépendances et lancer le serveur :

	```console
	git clone https://github.com/dlesbre/site-interludes.git &&
	cd site-interlude &&
	python3 -m venv venv &&
	source venv/bin/activate &&
	make start
	```

Le site devrait être accessible à [http://localhost:8000](http://localhost:8000).

Par la suite vous z relancer le site simplement avec `make serve`.

## Installation manuelle

Pour tester et modifier le répo, après l'avoir cloné :

1. Créer un [environement
   virtuel](https://docs.python.org/3/tutorial/venv.html) (`python3-venv`)

	```console
	python3 -m venv venv
	```

	(si vous le nommez autre chose que venv, ajouter le dossier correspondant
    au `.gitignore`)

2. Lancer l'environnement virtuel

	```console
	source venv/bin/activate
	```

3. Installer la dernière version de pip

	```console
	python3 -m pip install --upgrade pip
	```

4. Installer les dépendances

	```console
	pip3 install -r requirements.txt
	```

5. Copier/linker le fichier `interludes/secret_example.py` dans `interludes/secret.py`

	```console
	ln -s interludes/secret_example.py interludes/secret.py
	```

6. Faire les migrations

	```console
	python3 manage.py makemigrations
	python3 manage.py migrate
	```

## Lancer le serveur

Pour pouvoir afficher et tester le site (après avoir tout installé)

1. Lancer l'environnement virtuel si ce n'est pas déjà fait (si le prompt du
   terminal ne commence pas par `(venv)`)

	```console
	source venv/bin/activate
	```

2. Lancer le serveur avec `make serve` ou

	```console
	python3 manage.py runserver
	```

	Cette commande bloque le terminal, le serveur tourne tant qu'elle n'est pas
	interrompue (par `Ctrl+C` ou autre).

3. Dans un navigateur, le site se trouve à l'adresse
   [http://localhost:8000/](http://localhost:8000/)

4. Créer un compte super-utilisateur avec `make adduser`. Les réglages se modifient depuis les pages d'admin de Django [http://localhost:8000/admin](http://localhost:8000/admin).

## Guide de l'administrateur

Le site se gère depuis deux pages d'administration :

**Page d'administration Django :**
[http://localhost:8000/admin](http://localhost:8000/admin) permet de modifier
directement la base de donnée. Descriptif rapide des tables intéressantes :

- Utilisateurs - contient tous les utilisateurs et leurs permissions. Pour
  donner les droits d'administrateur à quelqu'un il faut lui donner le statut
  superuser (accès à l'admin du site) ET le statut équipe (accès à l'admin
  django).

- Pages HTML - contient les pages d'informations (notamment home, activités et
  FAQ). Cela permet de modifier leur contenu facilement (sans faire de pull).
  Ces pages ont un nom (uniquement visible dans l'admin), un URL d'accès et un
  contenu (format HTML avec tags de templates django).

	Les pages `home` (url vide) `activites` et `faq` sont spéciales. Elles
  apparaissent sur la barre de navigation et sont régénérées à partir de
  fichiers de base dans [pages/default/](./pages/default/) si quelqu'un tente
  d'y accéder après leur suppression.

	Les autres pages du site (formulaires, pages de connexion...) sont des
	templates django plus classique et ne peuvent être modifié que depuis le code
	source.

- Paramètres - les réglages du site, ils permettent :
	- ouvrir/fermer la création de compte, les inscriptions
	- renseigner l'ENS d'accueil
	- renseigner un lien de la billetterie et de serveur discord
	- ouvrir/fermer le formulaire de proposition d'activités
	- afficher/cacher le planning
	- renseigner l'email de contact, les dates de l'événement, les dates d'inscription
	- ajouter un message global au-dessus de toutes les pages
	- bloquer/autoriser l'envoi d'email globaux
	- Ajouter une version PDF du planning (pour mobiles)
	- Ajouter l'affiche (visible sur la page d'accueil)

- Activités - liste des activités prévues. C'est ici que vous pouvez
	rajouter/modifier les activités qui s'affichent sur la page activité. Un
	formulaire permet aux utilisateurs de proposer des activités directement. Il
	vous faudra les relire et les valider ensuite manuellement pour qu'elles
	soient affichées sur le site.

- Créneaux - place une activité sur le planning. Une activité peut avoir
  plusieurs créneaux si elle a lieu plusieurs fois. Noter que les inscriptions
  se font à des créneaux et non a des activités.

	Note : le planning généré par le site (en JS) est difficilement lisible sur
	mobile. Le site permet d'uploader une version PDF propre pour mobiles.
	Personnellement je faisais une capture d'écran du planning (vu sur un grand
	écran) que j'exportais en PDF.

- Participant - liste des gens inscrits et des informations sur leur inscription
  (ENS, repas choisi...)

- Choix d'activité - Liste de (participant, priorité, activité) indiquant les
  vœux des participants. Une fois que vous avez fait l'attribution, cocher les
  case "Obtenues" pour indiquer qui a eu quelle activité.


**Page d'administration du site :** [http://localhost:8000/admin_pages/](http://localhost:8000/admin_pages/)
- permet d'exporter les différentes tables au format CSV
- affiche l'état du site (version, réglages actuels, différentes métriques)
- une prévisualisation du planning
- permet l'écriture d'un mail à tous
- permet d'envoyer deux séries d'emails :
	- une aux inscrits pour leur communiquer les activités qu'ils ont obtenus
	- une aux orgas qui ont besoin de connaître la liste des participants à
		l'avance pour préparer leurs activités.

## En production

Le serveur a besoin d'être configuré pour HTTPS et d'être configuré pour livrer directement les fichiers situés dans `/static/` et `/media/`.

1. Installer les dépendances `make install`

2. S'assurer que `DEBUG = False` et que `ALLOWED_HOSTS` contient les adresses des hôtes dans [settings.py](./interludes/settings.py)

3. Créer ou remplacer le fichier `interludes/secret.py` pour qu'il ait les mots de passe et un nouveau secret. Vous pouvez générer un secret django avec

		python manage.py shell -c 'from django.core.management import utils; print(utils.get_random_secret_key())'

4. Faire les migration `make migrate`

5. Faire un `make preprod` pour générer les fichiers statiques et vérifier les réglages

## Idées de développement

A.K.A. la liste des trucs utiles que je n'ai pas eu le temps d'ajouter :

- Intégrer l'[algorithme de répartition](https://github.com/Imakoala/InterludesMatchings) dans le site au lieu de le faire tourner en externe à partir des exports CSV et de remplir les résultats à la main
- Envoyer une concaténation de tous les emails aux admins (pour vérification, et pas juste en copie pour éviter le spam...)
- Générer la version PDF du planning automatiquement au lieu de la faire à base de captures d'écran
- ~~Remplacer les templates HTML statiques par du rendu de fichier markdown éditable depuis la page d'admin (afin d'éviter de devoir refaire un pull à chaque petit changement)~~ fait
- Réutiliser les comptes élèves pour éviter aux gens de devoir créer des
  comptes. À Ulm, nous avons un système de compte clipper fourni par l'admin
  qu'on réutilise dans quasi tous les sites étudiants. Je peux facilement le
  rajouter à ce site, mais je ne sais pas comment faire pour les autres écoles.

## Liens divers

- [Le site des interludes 2021](https://interludes.ens.fr)
- [Le site des interludes 2022](https://interludes.assos-ensl.fr/)
- [Le github de l'algorithme de répartition](https://github.com/Imakoala/InterludesMatchings)
- [Le wiki de Paris-Saclay](https://wiki.crans.org/VieBdl/InterLudes) qui recense les visuels, sites webs et photos des interludes passées.
- [Le gitlab du site des 48h des jeux](https://git.eleves.ens.fr/dlesbre/48h-des-jeux) un événement très similaire intra-ENS Ulm, c'est fork de ce répo.
- [Le site des 48h des jeux](https://48hdesjeux.cof.ens.fr/)
