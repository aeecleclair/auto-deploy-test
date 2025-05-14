## allez edgar le singe


### Setup venv

`python -m venv .venv`

### Activate venv

`.venv\Scripts\activate`

### Install requirements

`pip install -r .\requirements.txt`

### Run app

`fastapi dev .\app\entrypoints\fastapi_app.py`

### Access website

`localhost:8000`

## Pourquoi tant de dossiers ?

### App

C'est ton serveur python à partir de là plus que des .py

#### Adaptaters

Pour tout ce qui fait appel à l'extérieur (récupérer le contenu d'une page web, stocker ou charger des données sur ton disque dur).

#### Entrypoints

Tout ce que l'utilisateur peut appeler, chaque entrypoint appelle une seule fonction de `logic` et traite les exceptions, c'est aussi l'endroit où tu définis quels adaptaters seront utilisé par ta logique (c'est ici qu'on définira si on utilise SQL ou des JSON pour stocker les données).

#### Logic

Fait tous les calculs, ne peut etre appelé que par un entrypoint, seule partie autorisée à utiliser les adaptaters, ceux-ci doivent etre donnés par les entrypoints.

#### Models

Défini la structure des données, tu peux faire de l'héritage et les models de base doivent hériter de `BaseModel` pour que Pydantic s'active, il permet de faire de la vérification de typage et marche très bien avec FastAPI pour vérifier les JSONs de communication.

### Assets

Lieux de stockage de tout ce qui est statique : html, images, css, données permanentes (par exemple liste de mots disponibles pour un pendu)
