### **Documentation Complète du Projet Zappy - Serveur**


# Zappy - Serveur

Zappy est un projet Epitech qui consiste à développer un jeu en réseau multijoueur. Le jeu se déroule sur un monde 2D nommé Trantor, qui est une grille torique (les bords se rejoignent). Plusieurs équipes de joueurs, contrôlés par des Intelligences Artificielles (IA), s'affrontent pour collecter des ressources et élever leur niveau.

L'objectif final pour une équipe est d'être la première à avoir au moins 6 joueurs atteignant le niveau 8.

Le projet se décompose en trois exécutables principaux :

*   **`zappy_server`**: Le serveur de jeu, écrit en C. Il est l'arbitre et le moteur du jeu, gérant toute la logique, l'état du monde, les actions des joueurs et la communication.
*   **`zappy_ai`**: Le client IA, dans un langage au choix(le notre en python). Il se connecte au serveur et contrôle un unique joueur en lui envoyant des commandes.
*   **`zappy_gui`**: Le client d'interface graphique, écrit en C++. Il se connecte au serveur pour obtenir une visualisation en temps réel de l'état du jeu.


## Table des matières
1.  [Compilation et Lancement](#compilation-et-lancement)
2.  [Protocoles de Communication](#protocoles-de-communication)
    *   [Protocole de l'IA](#protocole-de-lia)
    *   [Protocole du GUI](#protocole-du-gui)
3.  [Mécaniques de Jeu Principales](#mécaniques-de-jeu-principales)
    *   [Le Rituel d'Incantation](#le-rituel-dincantation)
    *   [Cycle de Vie d'un Joueur (Ponte et Éclosion)](#cycle-de-vie-dun-joueur-ponte-et-éclosion)
    *   [Gestion des Ressources et de la Nourriture](#gestion-des-ressources-et-de-la-nourriture)
4.  [Bonus : Commandes d'Administration](#bonus--commandes-dadministration)
5.  [Architecture Interne (Pour les Développeurs)](#architecture-interne-pour-les-développeurs)

## Compilation et Lancement

### Compilation
Pour compiler le projet, exécutez la commande suivante à la racine du projet :
```sh
make
```

### Lancement
```sh
USAGE: ./zappy_server -p port -x width -y height -n name1 name2 ... -c clientsNb -f freq
```
| Option | Description |
|:---|:---|
| **-p** port | Le numéro de port pour écouter les connexions. |
| **-x** width | La largeur du monde. |
| **-y** height | La hauteur du monde. |
| **-n** nameX | Les noms des différentes équipes. |
| **-c** clientsNb | Le nombre de clients autorisés à se connecter par équipe au début du jeu. |
| **-f** freq | La fréquence, qui détermine la vitesse du jeu. La durée d'une action est `T/f` secondes. |

Le serveur est un processus unique avec un seul thread. Il utilise `poll()` pour le multiplexage des I/O, ce qui lui permet de gérer de multiples clients de manière non-bloquante.

> Le nom d'équipe **`GRAPHIC`** est réservé et doit être utilisé par le client GUI pour s'authentifier.

---

## Protocoles de Communication

### Protocole de l'IA

La communication entre le client IA et le serveur se fait via des chaînes de caractères terminées par un `\n`.

#### Connexion d'un client IA

1.  Le client ouvre un socket sur le port du serveur.
2.  La séquence de connexion est la suivante :
    *   Serveur : `WELCOME\n`
    *   Client : `TEAM_NAME\n`
    *   Serveur : `CLIENT_NUM\n` (nombre de slots restants dans l'équipe)
    *   Serveur : `X Y\n` (dimensions du monde)

Si `CLIENT_NUM` est supérieur ou égal à 1, la connexion est acceptée.

> Un client peut envoyer jusqu'à **10 commandes** à la suite sans attendre de réponse. Les commandes supplémentaires seront ignorées. Le serveur les exécute dans l'ordre de réception, en respectant leur durée respective.

#### Commandes de l'IA

| Action | Commande | Durée | Réponse |
|:--- |:--- |:---:|:--- |
| Avancer d'une case | `Forward` | 7/f | `ok` |
| Tourner à droite de 90° | `Right` | 7/f | `ok` |
| Tourner à gauche de 90° | `Left` | 7/f | `ok` |
| Regarder autour | `Look` | 7/f | `[ tile1, tile2, ...]` |
| Consulter l'inventaire | `Inventory` | 1/f | `[ linemate n, sibur n, ...]` |
| Envoyer un message | `Broadcast text` | 7/f | `ok` |
| Slots d'équipe non utilisés | `Connect_nbr` | - | `value` |
| Créer un œuf | `Fork` | 42/f | `ok` |
| Expulser les joueurs | `Eject` | 7/f | `ok` / `ko` |
| Mort du joueur | - | - | `dead` |
| Prendre un objet | `Take object` | 7/f | `ok` / `ko` |
| Poser un objet | `Set object` | 7/f | `ok` / `ko` |
| Démarrer l'incantation | `Incantation` | 300/f | `Elevation underway` <br> `Current level: k` / `ko`|

> En cas de commande inconnue ou d'arguments invalides, le serveur répond `ko\n`.

### Protocole du GUI

Le client graphique utilise un protocole plus riche pour obtenir un état complet et en temps réel du jeu.

#### Symboles du protocole

| Symbole | Signification |
|:---|:---|
| `X`, `Y` | Largeur/hauteur ou position |
| `q0`..`q6` | Quantité des ressources (0: food, 1: linemate, etc.) |
| `n` | Numéro du joueur |
| `O` | Orientation: 1(N), 2(E), 3(S), 4(W) |
| `L` | Niveau du joueur ou de l'incantation |
| `e` | Numéro de l'œuf |
| `T` | Unité de temps (fréquence `f`) |
| `N` | Nom de l'équipe |
| `R` | Résultat de l'incantation (0 pour échec, 1 pour succès) |
| `M` | Message |
| `i` | Numéro de la ressource |

#### Commandes et Notifications du GUI

| Événement / Commande du GUI | Commande Serveur -> GUI | Détails |
|:---|:---|:---|
| **Informations initiales** | | (Envoyées après la connexion du GUI) |
| `msz` | `msz X Y\n` | Taille de la carte |
| `sgt` | `sgt T\n` | Fréquence actuelle |
| `mct` | `bct X Y q0 ... q6\n` (pour chaque case) | Contenu de toute la carte |
| `tna` | `tna N\n` (pour chaque équipe) | Noms de toutes les équipes |
| - | `pnw #n X Y O L N\n` (pour chaque joueur) | Connexion d'un nouveau joueur |
| - | `enw #e #n X Y\n` (pour chaque œuf) | Un œuf a été pondu |
| **Événements en temps réel** | | (Envoyés à tous les GUIs) |
| Connexion d'un joueur | `pnw #n X Y O L N\n` | Un joueur éclot ou se connecte |
| Mouvement du joueur | `ppo #n X Y O\n` | Position et orientation du joueur |
| Niveau du joueur | `plv #n L\n` | Le joueur a gagné un niveau |
| Inventaire du joueur | `pin #n X Y q0 ... q6\n` | Contenu de l'inventaire du joueur |
| Expulsion | `pex #n\n` | Le joueur a été expulsé d'une case |
| Broadcast | `pbc #n M\n` | Le joueur envoie un message |
| Début d'incantation | `pic X Y L #n #n ...\n` | Des joueurs commencent une incantation |
| Fin d'incantation | `pie X Y R\n` | Résultat de l'incantation |
| Ponte d'un œuf | `pfk #n\n` | Un joueur pond un œuf |
| Ressource lâchée | `pdr #n i\n` | Un joueur a posé une ressource |
| Ressource prise | `pgt #n i\n` | Un joueur a ramassé une ressource |
| Mort d'un joueur | `pdi #n\n` | Le joueur est mort |
| Ponte d'un œuf (effectif) | `enw #e #n X Y\n` | Un œuf apparaît sur la carte |
| Éclosion d'un œuf | `ebo #e\n` | Un joueur se connecte à cet œuf |
| Mort d'un œuf | `edi #e\n` | Un œuf a été détruit (par `Eject`) |
| **Commandes du GUI** | | (Le GUI peut demander ces informations) |
| `sst T` | `sst T\n` | Modification de la fréquence |
| **Fin de partie** | | |
| Victoire d'une équipe | `seg N\n` | Fin du jeu, l'équipe N a gagné |
| **Erreurs** | | |
| Commande inconnue | `suc\n` | |
| Mauvais paramètres | `sbp\n` | |

---

## Mécaniques de Jeu Principales

### Le Rituel d'Incantation
Pour monter de niveau, les joueurs doivent réaliser un rituel sur une même case.

*   **Conditions** : Un nombre précis de joueurs du même niveau et une quantité requise de chaque pierre doivent être présents sur la case.
*   **Déclenchement** : Un joueur lance la commande `Incantation`. Le serveur vérifie immédiatement les prérequis. Si ils ne sont pas remplis, le rituel échoue instantanément (`ko`).
*   **Déroulement** : Si les conditions sont bonnes, le rituel commence et dure `300/f` secondes. Tous les joueurs participants sont bloqués.
*   **Validation** : À la fin du rituel, le serveur **revérifie** que les conditions sont toujours remplies. Si c'est le cas, tous les joueurs participants montent de niveau et les pierres sont consommées. Sinon, le rituel échoue.

### Cycle de Vie d'un Joueur (Ponte et Éclosion)
1.  **Ponte (`Fork`)** : Un joueur crée un œuf sur sa case. Une nouvelle entité de type "œuf" est ajoutée au jeu, liée à l'équipe du joueur.
2.  **Connexion** : Un nouveau client IA se connecte avec le nom de l'équipe.
3.  **Éclosion** : Le serveur attribue au client un œuf disponible de cette équipe. L'œuf "éclot" et se transforme en un joueur actif de niveau 1. La connexion est établie.

### Gestion des Ressources et de la Nourriture
*   **Nourriture** : La survie d'un joueur dépend de sa nourriture. Une unité de nourriture permet de survivre 126 unités de temps. Si l'inventaire de nourriture d'un joueur tombe à zéro, il meurt.
*   **Apparition des ressources** : Le serveur fait apparaître des ressources sur la carte à intervalle régulier (toutes les 20 unités de temps) pour maintenir les densités définies dans le sujet.

---

## Bonus : Commandes d'Administration
Le serveur accepte des commandes sur son entrée standard pour faciliter le débogage et l'administration.

| Commande | Effet |
|:---|:---|
| `/clients` | Liste tous les clients connectés. |
| `/quit` | Arrête proprement le serveur. |
| `/send_ais msg` | Envoie un message à tous les clients IA. |
| `/send_guis msg` | Envoie un message à tous les clients GUI. |
| `/map` | Affiche des informations sur l'état de la carte. |
| `/pause` | Met en pause l'exécution des actions des joueurs. |
| `/start` | Reprend l'exécution après une pause. |
| `/setTile res x y`| Modifie les ressources d'une case. |
| `/kill id` | Tue un joueur par son ID. |
| `/setLevel id L` | Change le niveau d'un joueur. |
| ... | *(listez ici toutes vos autres commandes bonus)* |

---

## Architecture Interne (Pour les Développeurs)

<details>
<summary>Cliquez pour dérouler l'analyse détaillée de l'architecture du serveur.</summary>


Cette documentation se concentre exclusivement sur l'analyse et l'explication du code source du `zappy_server`.


#### **Table des Matières**

1.  [**Architecture Générale du Serveur**](#1-architecture-générale-du-serveur)
2.  [**Analyse des Modules**](#2-analyse-des-modules)
    *   [2.1. Module Logger](#21-module-logger)
    *   [2.2. Module Clock](#22-module-clock)
    *   [2.3. Module Commandes](#33-module-commandes)
    *   [2.4. Module Map](#24-module-map)
    *   [2.5. Module `Utilitaires`](#25-module-utilitaires)
    *   [2.6. Module `SessionClients`](#26-module-sessionclients)
    *   [2.7. Module `Server`](#27-module-server)
    *   [2.8. Point d'entrée `main.c`](#28-point-dentree-mainc)
3.  [**Structures de Données Centrales**](#3-structures-de-données-centrales)
4.  [**Cycle de vie et Mécaniques de Jeu**](#4-cycle-de-vie-et-mécaniques-de-jeu)
    *   [5.1. Cycle de vie d'un Joueur](#41-cycle-de-vie-dun-joueur)
    *   [5.2. Le Rituel d'Incantation](#42-le-rituel-dincantation)
5.  [**Compilation et Lancement**](#5-compilation-et-lancement)

---

### **1. Architecture Générale du Serveur**

Le serveur Zappy est conçu autour d'un modèle événementiel et non-bloquant, utilisant un unique processus et un unique thread, comme l'exige le cahier des charges.

Les concepts architecturaux clés sont :

*   **Boucle d'Événements (Event Loop)** : Le cœur du serveur est une boucle `while` qui utilise la fonction `poll()`. `poll()` surveille un ensemble de descripteurs de fichiers (le socket d'écoute du serveur et tous les sockets des clients connectés) pour toute activité (par exemple, une nouvelle connexion ou une commande reçue).
*   **Multiplexage des E/S** : `poll()` permet au serveur de gérer de multiples connexions clientes simultanément sans avoir besoin de créer un thread ou un processus par client.
*   **Gestion Asynchrone des Commandes** : Les commandes des joueurs ne sont pas exécutées instantanément. Elles ont un coût en temps, défini par la fréquence `f` du serveur. Chaque joueur possède une file de commandes (`command_queue_t`) qui stocke jusqu'à 10 commandes. Chaque commande est horodatée avec le moment où elle sera prête à être exécutée. La boucle principale du serveur vérifie en permanence quelles commandes sont prêtes à être traitées.
*   **Planificateur d'Événements (Scheduler)** : Le serveur ne se contente pas d'attendre l'activité réseau. Il doit aussi gérer des événements temporels comme la réapparition des ressources, la consommation de nourriture par les joueurs, et l'exécution des commandes. Pour cela, un planificateur (`calculate_next_event_timeout`) calcule le `timeout` minimal à passer à `poll()`, correspondant au temps d'attente jusqu'au prochain événement programmé.
*   **État Centralisé** : La structure principale `server_t` contient l'intégralité de l'état du jeu : la carte, la liste des joueurs, les équipes, les incantations en cours, etc. Toutes les fonctions opèrent sur cette structure, garantissant une source unique de vérité.

### **2. Analyse des Modules**

Le projet est structuré en plusieurs répertoires, chacun représentant un module avec des responsabilités distinctes.

#### **2.1. Module Logger**

Ce module fournit un système de journalisation simple mais efficace pour le débogage et le suivi de l'exécution du serveur.

*   **Fichiers**: `Logger/logger.h`, `Logger/logger.c`
*   **`log_level_t` (enum)** : Définit les niveaux de criticité des logs.
    *   `LOG_DEBUG`: Pour les messages de débogage très verbeux.
    *   `LOG_INFO`: Pour les informations générales sur le déroulement du jeu (connexions, etc.).
    *   `LOG_WARN`: Pour les avertissements, situations anormales mais non bloquantes.
    *   `LOG_ERROR`: Pour les erreurs critiques.
*   **`logger_config_t` (struct)** : Contient la configuration du logger.
    *   `level`: Le niveau de log minimum à afficher.
*   **`m_t` (struct)** : Contient les méta-informations sur l'origine d'un log.
    *   `file`: Le nom du fichier (`__FILE__`).
    *   `line`: Le numéro de la ligne (`__LINE__`).
*   **`LOG(l, f, ...)` (macro)** : Le point d'entrée principal pour logger un message. Il encapsule l'appel à `doc()` en passant automatiquement le niveau, le fichier et la ligne.
*   **`doc(...)` (fonction)** : La fonction principale qui formate et affiche le message de log.
*   **`log_set_level(...)` (fonction)** : Permet de changer le niveau de log à l'exécution.
*   **Logique interne (`logger.c`)**:
    *   Utilise des tableaux `G_LEVEL_STRINGS` et `G_LEVEL_COLORS` pour l'affichage.
    *   Un "singleton" `get_logger_config()` fournit un accès global à la configuration.
    *   Le temps est formaté avec `get_formatted_time()` qui utilise `clock_gettime(CLOCK_REALTIME)` pour une précision à la milliseconde.
    *   L'affichage est coloré uniquement si la sortie est un terminal (`isatty`).
    *   Les chaînes de log sont "sanitized" pour éviter les sauts de ligne intempestifs.

#### **2.2. Module Clock**

Ce module abstrait la gestion du temps, ce qui est fondamental pour le planificateur d'événements et la gestion des commandes.

*   **Fichiers**: `Clock/clock.h`, `Clock/clock.c`
*   **`struct timespec`**: Le type de données standard de `<time.h>` utilisé pour représenter le temps avec une précision à la nanoseconde.
*   **`get_current_time(...)`**: Récupère le temps actuel. Utilise `clock_gettime(CLOCK_MONOTONIC, ...)` pour obtenir un temps qui avance de manière continue et n'est pas affecté par les changements de l'horloge système. C'est crucial pour la stabilité du planificateur de jeu.
*   **`timespec_cmp(...)`**: Compare deux structures `timespec`. Compare d'abord les secondes (`tv_sec`), puis, si elles sont égales, les nanosecondes (`tv_nsec`). Retourne -1, 0, ou 1, suivant la convention de `strcmp`.
*   **`add_seconds_to_timespec(...)`**: Ajoute une durée (en secondes, potentiellement avec une partie fractionnaire) à un `timespec`. Sépare la durée en secondes entières et en nanosecondes et gère correctement le report.

#### **2.3. Module Commandes**

Ce module implémente la file d'attente de commandes pour chaque joueur, permettant une gestion asynchrone des actions.

*   **Fichiers**: `Commandes/command.h`, `Commandes/command_queue.c`, `Commandes/command_utils.c`
*   **`command_t` (struct)**: Représente une seule commande.
    *   `raw_cmd`: Le nom de la commande (ex: "Forward").
    *   `args`: Un tableau de chaînes pour les arguments de la commande.
    *   `duration`: La durée d'exécution de la commande en secondes.
    *   `ready_at`: L'instant précis (`struct timespec`) où la commande doit être exécutée.
    *   `argc`: Le nombre d'arguments.
*   **`command_queue_t` (struct)**: Représente la file d'attente.
    *   Implémentée comme un buffer circulaire de taille `MAX_COMMANDS` (10) avec des index `head`, `tail` et un compteur `size`.
*   **`enqueue_command(...)`**: Ajoute une commande à la fin de la file.
    1.  Vérifie si la file est pleine.
    2.  Appelle `setup_command()` pour parser la chaîne de commande brute.
    3.  Calcule l'heure d'exécution (`ready_at`) en ajoutant la durée de la commande à l'heure actuelle.
    4.  Met à jour les pointeurs de la file circulaire.
*   **`get_next_ready_command(...)`**: Parcourt la file pour trouver la prochaine commande prête à être exécutée. Parmi toutes les commandes prêtes, elle retourne l'index de celle qui devait être exécutée le plus tôt, assurant un traitement dans l'ordre de leur achèvement prévu.
*   **`remove_command_at(...)`**: Supprime une commande de la file. C'est une opération coûteuse car elle décale tous les éléments suivants pour compacter la file. Elle libère aussi toute la mémoire allouée pour la commande.
*   **`setup_command(...)`**: Parse une chaîne de commande brute (ex: `"Broadcast Hello World"`) en utilisant `strtok_r` pour découper la chaîne en mots (commande et arguments) et alloue la mémoire nécessaire avec `strdup`.

#### **2.4. Module Map**

Ce module gère la structure de données du monde du jeu.

*   **Fichiers**: `Map/map.h`, `Map/map_management.c`, `Map/map_entities.c`
*   **`resource_t` (enum)**: Énumère les 7 types de ressources possibles, de `FOOD` à `THYSTAME`.
*   **`tile_t` (struct)**: Représente une case de la carte.
    *   `resources`: Un tableau d'entiers contenant la quantité de chaque ressource sur la case.
    *   `entities`: Un pointeur vers une liste chaînée (`entity_on_tile_t`) des entités (joueurs ou œufs) présentes sur la case.
*   **`map_create(...)`**: Alloue dynamiquement une matrice 2D de `tile_t` et initialise chaque case.
*   **`map_destroy(...)`**: Libère toute la mémoire de la carte, y compris les listes d'entités sur chaque tuile.
*   **`map_spawn_resources(...)`**:
    1.  Calcule la quantité cible de chaque ressource sur la carte en utilisant les densités spécifiées (`map_size * density`).
    2.  Compte les ressources déjà présentes.
    3.  Ajoute les ressources manquantes sur des tuiles choisies au hasard.
    4.  Notifie les clients GUI des changements via `bct_f`.
*   **`map_add_entity(...)`, `map_detach_entity(...)`, `map_move_entity(...)`**: Fonctions pour gérer la présence des entités sur la carte en manipulant les listes chaînées des tuiles.

#### **2.5. Module `Utilitaires`**

Regroupe diverses fonctions de support essentielles au fonctionnement du serveur.

*   **Fichiers**: `argument_parser_*.c`, `event_scheduler.c`, `dynamic_buffer.c`, `error.c`, `look_utils.c`, `ai_utils.c`, `gui_utils.c`, `incantation_utils.c`, `fork_utils.c`, `client_utils.c`.
*   **Analyse d'arguments**: Les fonctions `parse_*` découpent la ligne de commande et remplissent la structure `config_server_t`.
*   **Planificateur d'événements (`event_scheduler.c`)**:
    *   **`calculate_next_event_timeout(server_t *server)`**: Fonction cruciale qui détermine le `timeout` pour `poll()`. Elle calcule la différence de temps en millisecondes entre "maintenant" et le prochain événement programmé (nourriture, fin de commande, respawn de ressources) et retourne la plus petite de ces différences.
*   **Buffer Dynamique (`dynamic_buffer.c`)**: Fournit une structure `dynamic_buffer_t` avec des fonctions pour initialiser, ajouter du texte, et libérer un buffer de `char` qui peut grandir automatiquement via `realloc`. C'est indispensable pour construire des réponses de taille variable comme celle de la commande `Look`.
*   **Gestion des commandes complexes**:
    *   **`look_utils.c`**: Contient la logique pour la commande `Look`. `write_vision` itère sur les niveaux de vision du joueur, calcule les coordonnées absolues de chaque tuile visible, et `append_tile_content_to_buffer` ajoute le contenu de la tuile au buffer dynamique.
    *   **`incantation_utils.c`**: Contient la table `G_REQ_TABLE` avec les prérequis pour chaque niveau. `check_incantation_prerequisites` vérifie si les conditions sont remplies sur une tuile. Les autres fonctions gèrent le cycle de vie d'une incantation.

#### **2.6. Module `SessionClients`**

Ce module contient toute la logique métier liée à l'exécution des commandes des clients AI et GUI, ainsi que les fonctions de notification.

*   **Fichiers**: `session_client_*.c`
*   **Commandes de l'IA (ex: `forward_f`, `take_object_f`)**: Chaque fonction implémente la logique d'une commande spécifique.
    *   Elles modifient l'état du serveur (position du joueur, inventaires, etc.).
    *   Elles appellent les fonctions de notification GUI correspondantes (ex: `ppo_f`, `pgt_f`).
    *   Elles envoient une réponse au client AI (`"ok\n"` ou `"ko\n"`).
*   **Gestionnaires de commandes du GUI (ex: `msz_h`, `bct_h`)**: Ces fonctions répondent aux requêtes du client graphique en lui envoyant des informations sur l'état du jeu, sans modifier cet état.
*   **Fonctions de notification au GUI (ex: `pnw_f`, `pdi_f`, `pie_f`)**: Ces fonctions ne sont pas appelées directement par un client, mais par la logique du serveur lorsqu'un événement se produit. Elles formatent un message de notification et l'envoient à tous les clients GUI connectés via `send_to_all_guis`.

#### **2.7. Module `Server`**

Le module central qui orchestre tous les autres. Il gère le cycle de vie du serveur, le réseau, et la distribution des commandes.

*   **Fichiers**: `server_*.c`
*   **`setup_server(...)` et `cleanup_server(...)`**: Gèrent l'allocation et la libération de toutes les ressources du serveur (sockets, mémoire, etc.), assurant un démarrage et un arrêt propres.
*   **`run_server(...)`**: Contient la boucle d'événements principale qui appelle `poll()`, `handle_network_events()` et `handle_game_logic()`.
*   **`handle_network_events(...)`**: Gère les événements `POLLIN`. Si c'est sur le socket d'écoute, appelle `accept_client_connection`. Sinon, appelle `receive_client_data` pour lire les commandes d'un client.
*   **`handle_game_logic(...)`**: Le "tick" du jeu. Appelle `exec_cmd` pour chaque joueur, vérifie la nourriture (`check_life`), la fin des incantations, le respawn des ressources et les conditions de victoire.
*   **`handle_command(...)`**: Le dispatcher principal de commandes. Il détermine si un client est en cours d'authentification ou déjà en jeu, et s'il est de type AI ou GUI, puis appelle le gestionnaire de commande approprié.
*   **`server_egg_utils.c`**: Contient la logique spécifique à la connexion d'un joueur via un œuf, notamment `hatch_egg_for_client`.

#### **2.8. Point d'entrée `main.c`**

Le point de départ de l'application.

*   **`main(int ac, char *av[])`**:
    1.  Définit le niveau de log.
    2.  Appelle `parse_args` pour créer une structure `config_server_t` à partir des arguments de la ligne de commande.
    3.  Appelle `setup_server` pour initialiser le serveur avec cette configuration.
    4.  Assigne le pointeur du serveur à la variable globale `server_ptr` (utilisée pour le nettoyage en cas de signal `SIGINT`).
    5.  Lance la boucle principale avec `run_server(server)`.
    6.  Après la fin de la boucle, appelle `cleanup_server(server)` pour libérer toutes les ressources.

### **3. Structures de Données Centrales**

Une compréhension profonde des structures de données est essentielle.

| Structure | Fichier | Rôle |
| :--- | :--- | :--- |
| **`server_t`** | `Server/server.h` | **L'État Global du Jeu.** Contient tout : la carte, les joueurs, les équipes, la configuration, les sockets, etc. |
| **`session_client_t`**| `Server/server.h` | **Une Entité.** Peut représenter un joueur actif, un œuf, ou un client GUI. Contient sa position, son niveau, son inventaire, sa file de commandes, son état, etc. |
| **`config_server_t`**| `Server/server.h` | **La Configuration Initiale.** Stocke tous les paramètres de la ligne de commande (`-p`, `-x`, `-y`, etc.). |
| **`teams_t`** | `Server/server.h` | **Une Équipe.** Contient son nom, le nombre de joueurs, et des pointeurs vers ses joueurs. |
| **`tile_t`** | `Map/map.h` | **Une Case de la Carte.** Contient les ressources et une liste chaînée des entités présentes. |
| **`command_queue_t`**| `Commandes/command.h` | **La File d'Actions d'un Joueur.** Gère les commandes en attente pour un joueur. |
| **`incantation_t`** | `Server/server.h` | **Un Rituel d'Élévation.** Représente une incantation en cours, avec sa position, son niveau et son heure de fin. |

### **4. Cycle de vie et Mécaniques de Jeu**

#### **4.1. Cycle de vie d'un Joueur**

1.  **Ponte (`fork_f`)**: Un joueur crée un œuf sur sa case. Une nouvelle entité `session_client_t` est créée avec `is_egg = true`.
2.  **Connexion**: Un client AI se connecte et donne son nom d'équipe.
3.  **Éclosion (`hatch_egg_for_client`)**: Le serveur trouve un œuf de l'équipe. La connexion est transférée à l'entité œuf, qui devient un joueur (`is_egg = false`, `active = true`).
4.  **Survie (`check_life`)**: Le joueur consomme de la nourriture à intervalle régulier. S'il n'en a plus, il meurt.
5.  **Mort**: La connexion du client est fermée, l'entité est retirée du jeu, et la mort est notifiée (`pdi_f`).

#### **4.2. Le Rituel d'Incantation**

1.  **Initiation (`incantation_f`)**: Un joueur lance la commande. Le serveur vérifie les prérequis (joueurs et pierres) via `check_incantation_prerequisites`.
2.  **Déroulement**: Si les prérequis sont valides, une `incantation_t` est activée pour 300/f secondes. Les joueurs participants sont bloqués (`is_elevating`).
3.  **Validation**: À la fin du temps, `check_and_finish_incantations` revérifie les prérequis.
    *   **Succès**: Si les conditions sont toujours valides, les joueurs montent de niveau, les pierres sont consommées.
    *   **Échec**: Sinon, le rituel échoue, et personne ne monte de niveau.

### **5. Compilation et Lancement**

Le projet se compile avec un `Makefile` qui doit générer le binaire `zappy_server`.

**Lancement :**
```bash
./zappy_server -p <port> -x <width> -y <height> -n <team_name_1> <team_name_2> ... -c <clientsNb> -f <freq>
```
Tous les paramètres sont obligatoires pour un fonctionnement correct du serveur.
