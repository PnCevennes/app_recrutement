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
    pip install -r requirements.txt 
    git clone https://github.com/PnCevennes/app_recrutement.git
```


Initialisation
--------------


Crée la base de données avec des données de test

```
    cd app_recrutement
    python alt_serv.py shell
    >import bootstrap
```


Démarrage du serveur en mode debug
----------------------------------


```
    python server.py
```
