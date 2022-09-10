# Site des 48h des jeux

Ce répo contient le site des 48h des jeux. Ce site est en ligne à l'adresse [https://48hdesjeux.cof.ens.fr/](https://48hdesjeux.cof.ens.fr/).

Ce répo est diffusé sous une [license MIT](https://choosealicense.com/licenses/mit/).

**Contenu :**
- [Description](#description)
- [Lancement rapide](#lancement-rapide)
- [Installation](#installation)
- [Lancer le serveur](#lancer-le-serveur)
- [Guide de l'administrateur](#guide-de-ladministrateur)
- [En production](#en-production)
- [Idées de développement](#idées-de-développement)
- [Liens divers](#liens-divers)

## Description

Ce site sert à organiser les 48h des jeux (ou les interludes). Il dispose des fonctionnalités suivantes :

- Formulaire de soumission d'activité pour l'appel à projet
- Système pour afficher le planning
- ~~Système d'inscription des participants avec souhaits (triés) des différentes
  activités~~ (Retirer, on demande aux participants d'envoyer des mails aux orgas)


## Lancement rapide

Pour installer toutes les dépendances et lancer le serveur :

	```console
	git clone https://git.eleves.ens.fr/dlesbre/48h-des-jeux.git &&
	cd site-interlude &&
	python3 -m venv venv &&
	source venv/bin/activate &&
	make start
	```

Le site devrait être accessible à [http://localhost:8000](http://localhost:8000).

Par la suite vous pouvez relancer le site simplement avec `make serve`.

## Installation

Pour tester et modifier le repo, après l'avoir cloné :

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

4. Installer les requirements

	```console
	pip3 install -r requirements.txt
	```

5. Copier/linker le fichier `site48h/secret_example.py` dans `site48h/secret.py`

	```console
	ln -s site48h/secret_example.py site48h/secret.py
	```

6. Faire les migrations

	```console
	make migrate
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
	make serve
	```

	Cette commande bloque le terminal, le serveur tourne tant qu'elle n'est pas
	interrompue (par `Ctrl+C` ou autre).

3. Dans un navigateur, le site se trouve à l'adresse
   [http://localhost:8000/](http://localhost:8000/)

4. Créer un compte super-utilisateur avec `make adduser`. Les réglages se modifient depuis les pages d'admin de Django [http://localhost:8000/admin](http://localhost:8000/admin).

## Guide de l'administrateur

Le site se gère depuis deux pages d'administration :

**Page d'administration Django :** [http://localhost:8000/admin](http://localhost:8000/admin) permet de modifier directement la base de donnée. Descriptif rapide des tables intéressantes :

- Utilisateurs - contient tous les utilisateurs et leurs permissions. Pour
  donner les droits d'administrateur à quelqu'un il faut lui donner le statut
  superuser (accès à l'admin du site) ET le statut équipe (accès à l'admin
  django).

	Pour ajouter un compte non-clipper vous pouvez le créer ici (avec un
  mot de passe bidon), y rajouter un email, et ensuite demander à la personne
  concernée d'utilisé le formulaire de changement de mot de passe pour en créer un.

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
	- ~~ouvrir/fermer la création de compte, les inscriptions~~ (uniquement sur la version Interludes)
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

- ~~Participant - liste des gens inscrits et des informations sur leur inscription
  (ENS, repas choisi...)~~

- ~~Choix d'activité - Liste de (participant, priorité, activité) indiquant les
  vœux des participants. Une fois que vous avez fait l'attribution, cocher les
  case "Obtenues" pour indiquer qui a eu quelle activité.~~


**Page d'administration du site :** [http://localhost:8000/admin_pages/](http://localhost:8000/admin_pages/)
- permet d'exporter les différentes tables au format CSV
- affiche l'état du site (version, réglages actuels, différentes métriques)
- une prévisualisation du planning
- permet l'écriture d'un mail à tous.

## En production

Le serveur a besoin d'être configuré pour HTTPS et d'être configuré pour livrer directement les fichiers situés dans `/static/` et `/media/`.

1. Installer les dépendances `make install`

2. S'assurer que `DEBUG = False` et que `ALLOWED_HOSTS` contient les adresses des hôtes dans [settings.py](./site48h/settings.py)

3. Créer ou remplacer le fichier `site48h/secret.py` pour qu'il ait les mots de passe et un nouveau secret. Vous pouvez générer un secret django avec

	```console
	python manage.py shell -c 'from django.core.management import utils; print(utils.get_random_secret_key())'
	```

4. Faire les migrations `make migrate`

5. Faire un `make preprod` pour générer les fichiers statiques et vérifier les réglages

## Idées de développement

A.K.A. la liste des trucs utiles que je n'ai pas eu le temps d'ajouter

- Envoyer une concaténation de tous les emails aux admins (pour vérification, et pas juste en copie pour éviter le spam...)
- Générer la version PDF du planning automatiquement au lieu de la faire à base de captures d'écran

## Liens divers

- [Le site des 48h des jeux](https://48hdesjeux.cof.ens.fr/)
- [Le github de l'algorithme de répartition](https://github.com/Imakoala/InterludesMatchings)
- [Le site du club jeu](https://jeux.cof.ens.fr/)
- [le site des interludes](https://interludes.ens.fr/) dont ce site est une variant allégée
- [Le gitlab du site des interludes](https://git.eleves.ens.fr/dlesbre/site-interludes), origine de ce fork
- [Le github du site des interludes](https://github.com/dlesbre/site-interludes) la même chose, mais sur github
