# Zappy

## Description
Zappy est de développer un jeu en réseau où plusieurs équipes s’affrontent sur une grille torique (les bords se connectent) pour collecter des ressources et élever leurs joueurs. La victoire revient à la première équipe dont au moins six joueurs atteignent le niveau maximal d’« élévation »

## Fonctionnalités
- Communication avec le serveur Zappy
- Vision et analyse de l'environnement
- Prise de décision autonome
- Navigation intelligente
- Gestion des ressources
- Communication entre joueurs
- Montée de niveau automatique

## Prérequis
- Python 3.8 ou supérieur
- Serveur Zappy

## Installation

### Cloner le repository
```bash
git clone https://github.com/EpitechPromo2028/B-YEP-400-COT-4-1-zappy-noah.toffa.git
cd B-YEP-400-COT-4-1-zappy-noah.toffa/
```

### Installer les dépendances
```bash
pip install -r src/ai/requirements.txt
```

## Utilisation

### Configuration
Vous pouvez configurer l'IA de trois façons :

1. Arguments en ligne de commande :
```bash
python src/ai/main.py -p 4242 -n team1 -h localhost
```

2. Variables d'environnement :
```bash
export ZAPPY_HOST=localhost
export ZAPPY_PORT=4242
export ZAPPY_TEAM=team1
python src/ai/main.py
```

3. Fichier de configuration :
```bash
python src/ai/main.py --config config.json
```

### Lancer l'IA
```bash
python src/ai/main.py
```

## Structure du Projet
```
zappy/
├── docs/                    # Documentation technique
│   ├── ai.md               # Documentation du module AI
│   ├── protocol.md         # Documentation du module Protocol
│   ├── vision.md           # Documentation du module Vision
│   └── main.md             # Documentation du module principal
├── src/
│   └── ai/                 # Code source
│       ├── ai.py           # Module d'intelligence artificielle
│       ├── protocol.py     # Module de communication
│       ├── vision.py       # Module de vision
│       └── main.py         # Point d'entrée
│       ├── requirements.txt # Dépendances Python
│       ├── tests/           # Tests unitaires
└── README.md              # Ce fichier
```

## Documentation
La documentation technique détaillée est disponible dans le dossier `docs/` :
- [Documentation Client](docs/client.md)
- [Documentation Protocol](docs/protocol.md)
- [Documentation Vision](docs/vision.md)

## Tests
Pour exécuter les tests pythons:
```bash
make test_ai
```

## Auteurs
- Chrisnaud AGOSSOU: Développeur IA
- Chance TOSSOU : Développeur IA assistant
- Christian ABIALA
- Noah Toffa
- Hermes AGANI
- Aurel DOSSOU
