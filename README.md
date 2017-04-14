Application de gestion des recrutements
=======================================


Centralise la saisie des recrutements des différents service et signale les différents ajouts et changements aux administrateurs.


installation
------------

Exemple ubuntu 14.04


Certains modules nécessitent l'utilisation du paquet python3-dev

```
    sudo apt-get install python3-dev
```


```
    mkdir recrutement
    cd recrutement
```

Création du virtualenv et téléchargement des dépendances
--------------------------------------------------------


```
    virtualenv venv -p /usr/bin/python3
    source venv/bin/activate
    git clone https://github.com/PnCevennes/app_recrutement.git
    cd app_recrutement
    pip install -r requirements.txt 
```


Initialisation
--------------

Crée la configuration de base de l'application

```
    cp config.py.sample config.py
```


Crée la base de données avec des données de test

```
    python server.py shell
    >import all
```


Démarrage du serveur en mode debug
----------------------------------


```
    python server.py runserver -d -r
```



Démarrage du serveur en production
----------------------------------


```
    gunicorn --daemon -b '0.0.0.0:8000' server:app
```


Commandes make
--------------


Les commandes make ne nécessitent pas l'activation du virtualenv avant d'être lancées

```
    make shell
```
Lance une console python dans l'environnement virtuel de l'application (eq. (venv)$ python server.py shell)


```
    make develop
```
Lance le serveur en mode de développement (eq. (venv)$ python server.py runserver -d -r)


```
    make prod
```
Lance le serveur en production (cf. Demarrage du serveur en production)



```
    make prod-stop
```
Arrête tous les processus serveurs en production



Options des commandes make
--------------------------

```
HOST=0.0.0.0
```
Détermine l'IP sur laquelle le serveur écoute


```
PORT=8000
```
Détermine le port sur lequel le serveur écoute


```
VENV=venv
```
Détermine le nom du virtualenv utilisé par l'application


```
WORKERS=4
```
Détermine le nombre de processus serveur créés (normalement 2-4 x nb_coeurs). Utilisé uniquement par la commande `make prod`

