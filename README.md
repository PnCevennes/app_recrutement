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
    pip install flask
    pip install flask-sqlalchemy
    pip install flask-mail
    git clone https://github.com/PnCevennes/app_recrutement.git
```


Démarrage du serveur en mode debug
----------------------------------


```
    cd app_recrutement
    python server.py
```
