# Site des interludes

[![website](https://img.shields.io/website?url=https%3A%2F%2Finterludes.ens.fr%2F)](https://interludes.ens.fr)
[![forks](https://img.shields.io/badge/forks-5-blue)](#forks)

Ce répo contient le code source du site des interludes. La version 2021 est en ligne à
[https://interludes.ens.fr](https://interludes.ens.fr). Il est disponible sur le
[git interne de l'ENS Ulm](https://git.eleves.ens.fr/dlesbre/site-interludes) et
sur [github](https://github.com/dlesbre/site-interludes). Il est diffusé sous
une [licence MIT](https://choosealicense.com/licenses/mit/).

**Ce site permet de :**
- Afficher de l'information sur l'événement (page d'accueil et FAQ, modifiable
  directement depuis l'admin du site)
- Recenser les activités proposées (page activités)
- Un formulaire pour permettre aux gens de proposer des activités
  qui envoie un mail aux administrateurs à chaque fois qu'une nouvelle activité
	est proposée.
- Un formulaire d'inscription où chaque inscrit peut renseigner des infos
  personnelles (repas/dormir) et les activités qu'il souhaite
- Afficher un planning dynamique des différentes activités
- Une fois la répartition faite, envoyer un mail à tous les inscrits pour leur
  communiquer les activités obtenues et un mail aux orgas pour leur communiquer
  la liste des participants
- Un formulaire pour envoyer un mail à tous (à utiliser avec modération)
- Exporter les tables intéressantes au format CSV


**Il n'est PAS capable de :**
- vendre des tickets - différentes solutions ont été utilisées pour ça par le passé :
  - utiliser une billetterie externe (ex [HelloAsso](https://www.helloasso.com/))
  - recruter les BdE/BdL des autres écoles pour qu'ils gèrent les paiements
  - paiement en espèces/CB sur place le jour J
- répartir les activités - nous faisons un premier jet avec le [ce
  code](https://github.com/Lamakaio/InterludesMatchings) (en prenant l'export
  CSV de la table de choix d'activités), puis l'adaptons à la main et le
  renseignons dans ce site.

**Contenu:**
- [Forks](#forks)
- [Lancement rapide](#lancement-rapide)
- [Installation pas à pas](#installation-pas-à-pas)
- [Lancer le serveur](#lancer-le-serveur)
- [Guide de l'administrateur](#guide-de-ladministrateur)
- [En production](#en-production)
- [Idées de développement](#idées-de-développement)
- [Liens divers](#liens-divers)

## Forks

Ce serveur a été repris pour plusieurs événements similaires :

| Site Web                                                      | Code source                                                                                                                  | Notes                                                              | État                                                                                                                                           |
| :------------------------------------------------------------ | :--------------------------------------------------------------------------------------------------------------------------- | :----------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------- |
| [Interludes 2025 Ulm](https://interludes.ens.fr/)             | [github](https://github.com/dlesbre/site-interludes/) ou [gitlab ENS Ulm](https://git.eleves.ens.fr/dlesbre/site-interludes) | tag v3.0.8                                       | ![website](https://img.shields.io/website?url=https%3A%2F%2Finterludes.ens.fr%2F&down_message=hors%20ligne&label&up_message=en%20ligne)        |
| [Interludes 2021 Ulm](https://interludes.ens.fr/static/archive/2021/index.html)             | [github](https://github.com/dlesbre/site-interludes/) ou [gitlab ENS Ulm](https://git.eleves.ens.fr/dlesbre/site-interludes) | Version initiale, tag v1.2.8                                       | ![website](https://img.shields.io/website?url=https%3A%2F%2Finterludes.ens.fr%2Fstatic%2Farchive%2F2021%2Findex.html&down_message=hors%20ligne&label&up_message=en%20ligne)        |
| [48h des jeux](https://48hdesjeux.cof.ens.fr/)                | [gitlab ENS Ulm](https://git.eleves.ens.fr/dlesbre/48h-des-jeux)                                                             | Rentrée ludique d'Ulm 2021 (48h-v2.3.1), 2022 et 2023 (48h-v3.0.1) | ![website](https://img.shields.io/website?url=https%3A%2F%2F48hdesjeux.cof.ens.fr%2F&down_message=hors%20ligne&label&up_message=en%20ligne)    |
| [Interludes 2022 Lyon](https://interludes.assos-ensl.fr/)     | [github](https://github.com/Pantoofle/site-interludes)                                                                       | Branche Lyon-2022, tag v2.1.0                                      | ![website](https://img.shields.io/website?url=https%3A%2F%2Finterludes.assos-ensl.fr%2F&down_message=hors%20ligne&label&up_message=en%20ligne) |
| [KWEI](https://kwei.crans.org/)                               | [gitlab Paris Saclay](https://gitlab.crans.org/aeltheos/site-kwei)                                                           | Rentrée ludique Paris-Saclay 2022 et 2023                          | ![website](https://img.shields.io/website?url=https%3A%2F%2Fkwei.crans.org%2F&down_message=hors%20ligne&label&up_message=en%20ligne)           |
| [Interludes 2023 Paris-Saclay](https://interludes.crans.org/) | [gitlab Paris Saclay](https://gitlab.crans.org/mediatek/site-interludes/)                                                    | Branche Saclay-2023                                                | ![website](https://img.shields.io/website?url=https%3A%2F%2Finterludes.crans.org%2F&down_message=hors%20ligne&label&up_message=en%20ligne)     |

Le code de l'algorithme de répartition est aussi disponible [sur github](https://github.com/Imakoala/InterludesMatchings).

## Lancement rapide

Pour installer toutes les dépendances et lancer le serveur :

```console
git clone https://github.com/dlesbre/site-interludes.git &&
sudo apt-get install libsasl2-dev python-dev-is-python3 libldap2-dev libssl-dev &&
cd site-interlude &&
python3 -m venv venv &&
source venv/bin/activate &&
make start
```

Le site devrait être accessible à [http://localhost:8000](http://localhost:8000).

Par la suite vous pouvez relancer le site simplement avec `make serve`.

## Installation pas à pas

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

4. Installer les dépendance externes (nécessaire pour `python-ldap`, qui est nécessaire
	pour la connexion clipper):

	```console
	sudo apt-get install libsasl2-dev python-dev-is-python3 libldap2-dev libssl-dev
	```

5. Installer les dépendances

	```console
	pip3 install -r requirements.txt
	```

6. Copier/linker le fichier `interludes/secret_example.py` dans `interludes/secret.py`

	```console
	ln -s interludes/secret_example.py interludes/secret.py
	```

7. Faire les migrations

	```console
	python3 manage.py makemigrations
	python3 manage.py migrate
	```

Pour l'aide au développement et maintenir un code propre, j'utilise :
- les formateurs/linter [ruff](https://github.com/astral-sh/ruff),
	à installer via `pip install ruff` puis lancer par `make format`
- le type-checker [mypy](https://pypi.org/project/mypy/)
	à installer via `pip install mypy django-stubs` puis lancer par `make mypy`. Normalement
	tous les fichiers sont bien typés, sauf `shared/forms.py` qui utilisent trop de hacks.

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

Le site inclus un guide de l'administrateur accessible aux super-utilisateurs
a [http://localhost:8000/admin_pages/info](http://localhost:8000/admin_pages/info)

Le site se gère depuis deux pages d'administration :

**Page d'administration Django :**
[http://localhost:8000/admin](http://localhost:8000/admin) (autogénérée) permet de modifier
directement la base de donnée. Descriptif rapide des tables intéressantes :

- Utilisateurs - contient tous les utilisateurs et leurs permissions. Pour
  donner les droits d'administrateur à quelqu'un il faut lui donner le statut
  superuser (accès à l'admin du site) ET le statut équipe (accès à l'admin
  django).

- Pages HTML - contient les pages d'informations (notamment home, activités et
  FAQ). Cela permet aux administrateurs de modifier leur contenu facilement
  depuis le site en ligne, sans avoir à accéder au serveur. Ces pages ont un nom
  (uniquement visible dans l'admin), un URL d'accès et un contenu (format HTML
  avec tags de templates django).

	Les pages `home` (url vide) `activites` et `faq` sont spéciales. Elles
  apparaissent sur la barre de navigation et sont régénérées à partir de
  fichiers de base dans [pages/default/](./pages/default/) si quelqu'un tente
  d'y accéder après leur suppression.

	Vous pouvez créer d'autres pages sur des URL libres si ça vous semble pertinent.

	Les autres pages du site (formulaires, pages de connexion...) sont des
	templates django plus classiques et ne peuvent être modifié que depuis le code
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
	- Ajouter une version PDF/PNG du planning (pour mobiles)
	- Ajouter l'affiche (visible sur la page d'accueil)


	De nombreux champs dans les paramètres sont purement informationnels et ne servent
	qu'à mettre à jour l'affichage dans certaines pages, mais certains servent
	à activer/désactiver des fonctionnalités du site (inscription, soumission d'activités, ...).

- Activités - liste des activités prévues. C'est ici que vous pouvez
	rajouter/modifier les activités qui s'affichent sur la page activité. Un
	formulaire permet aux utilisateurs de proposer des activités directement. Il
	vous faudra les relire et les valider ensuite manuellement pour qu'elles
	soient affichées sur le site.

- Créneaux - place une activité sur le planning. Une activité peut avoir
  plusieurs créneaux si elle a lieu plusieurs fois. Noter que les inscriptions
  se font à des créneaux et non a des activités.

	Note : le planning généré par le site (en JS) est difficilement lisible sur
	mobile. Le site permet d'uploader une version PDF ou PNG propre pour mobiles.
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

2. Initialiser les variables d'environnement secrètes (tous les variables initialisées
    par un `credentials` dans [settings.py](./interludes/settings.py)). Par exemple,
    (les variables d'environnement doivent avoir un préfixe `INTERLUDE_`).

3. Faire les migrations `make migrate`

4. Faire un `make preprod` pour générer les fichiers statiques et vérifier les réglages

## Idées de développement

A.K.A. la liste des trucs utiles que je n'ai pas eu le temps d'ajouter :

- Intégrer l'[algorithme de répartition](https://github.com/Imakoala/InterludesMatchings) dans le site au lieu de le faire tourner en externe à partir des exports CSV et de remplir les résultats à la main
- Envoyer une concaténation de tous les emails aux admins (pour vérification, et pas juste en copie pour éviter le spam...)
- Générer la version PDF du planning automatiquement au lieu de la faire à base de captures d'écran
- ~~Remplacer les templates HTML statiques par du rendu de fichier markdown
  éditable depuis la page d'admin (afin d'éviter de devoir refaire un pull à
  chaque petit changement)~~ fait
- Réutiliser les comptes élèves pour éviter aux gens de devoir créer des
  comptes. À Ulm, nous avons un système de compte clipper fourni par l'admin
  qu'on réutilise dans quasi tous les sites étudiants. Je ~~peux facilement le
  rajouter à ce site~~ fait, mais je ne sais pas comment faire pour les autres écoles.
- Rajouter des tests unitaires...

## Liens divers

- [Le site des interludes 2021 et 2025](https://interludes.ens.fr) (contient aussi en archive les vielles version du site)
- [Le site des interludes 2022](https://interludes.assos-ensl.fr/)
- [le site des interludes 2023](https://interludes.crans.org/)
- [Le github de l'algorithme de répartition](https://github.com/Imakoala/InterludesMatchings)
- [Le wiki de Paris-Saclay](https://wiki.crans.org/VieBdl/InterLudes) qui recense les visuels, sites webs et photos des interludes passées.
- [Le site des 48h des jeux](https://48hdesjeux.cof.ens.fr/) et son [gitlab](https://git.eleves.ens.fr/dlesbre/48h-des-jeux), un événement très similaire intra-ENS Ulm, c'est fork de ce répo.
- [Le site du KWEI](https://kwei.crans.org/) et son [gitlab](https://gitlab.crans.org/mediatek/site-kwei), un événement similaire intra-ENS Paris-Saclay
- [Le site du club jeu d'Ulm](https://jeux.cof.ens.fr/)
