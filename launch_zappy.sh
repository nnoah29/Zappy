#!/bin/bash

# ==============================================================================
# Script de lancement pour le projet Zappy Epitech
#
# VERSION SILENCIEUSE & INTELLIGENTE
# - N'affiche QUE les logs du serveur.
# - Ne lance 'make re' QUE si un des binaires est manquant.
# - Les erreurs critiques de lancement sont toujours affichées.
# ==============================================================================

# --- Configuration par défaut ---
DEFAULT_PORT=8600
DEFAULT_FREQ=7
DEFAULT_WIDTH=25
DEFAULT_HEIGHT=25
HOST="127.0.0.1"
TEAMS=("team1" "team2" "team3")
AI_PER_TEAM=10
GUI_COUNT=2
BINARIES=("./zappy_server" "./zappy_ai" "./zappy_gui")

# --- Fonctions ---
function usage() {
    echo "Usage: $0 [-p port] [-f freq] [-x width] [-y height] [-h]"
    echo "Lance une instance complète du jeu Zappy."
    echo "La compilation est ignorée si les binaires existent déjà."
    echo
    echo "Options:"
    echo "  -p PORT      Spécifie le port du serveur (défaut: $DEFAULT_PORT)"
    echo "  -f FREQ      Spécifie la fréquence du jeu (défaut: $DEFAULT_FREQ)"
    echo "  -x WIDTH     Spécifie la largeur de la map (défaut: $DEFAULT_WIDTH)"
    echo "  -y HEIGHT    Spécifie la hauteur de la map (défaut: $DEFAULT_HEIGHT)"
    echo "  -h           Affiche cette aide"
    exit 0
}

# Fonction de nettoyage, appelée à la sortie du script (Ctrl+C)
function cleanup() {
    echo -e "\n\n--- Arrêt des processus Zappy ---" >&2
    if [ ${#PIDS[@]} -eq 0 ]; then
        exit 0
    fi
    kill ${PIDS[@]} 2>/dev/null
    echo "Nettoyage terminé." >&2
    exit 0
}

PORT=$DEFAULT_PORT
FREQ=$DEFAULT_FREQ
WIDTH=$DEFAULT_WIDTH
HEIGHT=$DEFAULT_HEIGHT

while getopts "p:f:x:y:h" opt; do
    case "$opt" in
        p) PORT="$OPTARG" ;;
        f) FREQ="$OPTARG" ;;
        x) WIDTH="$OPTARG" ;;
        y) HEIGHT="$OPTARG" ;;
        h) usage ;;
        \?) echo "Option invalide: -$OPTARG" >&2; usage ;;
    esac
done

# --- Exécution ---

declare -a PIDS

trap cleanup SIGINT SIGTERM

# 1. Compilation conditionnelle
if [ ! -x "${BINARIES[0]}" ] || [ ! -x "${BINARIES[1]}" ] || [ ! -x "${BINARIES[2]}" ]; then
    make re
    if [ $? -ne 0 ]; then
        echo "Erreur: La compilation a échoué. Arrêt du script." >&2
        exit 1
    fi
    echo "Info: Compilation terminée." >&2
else
    echo "Info: Binaires déjà présents. Compilation ignorée." >&2
fi

# 2. Vérification finale des binaires
for bin in "${BINARIES[@]}"; do
    if [ ! -x "$bin" ]; then
        echo "Erreur: Le binaire '$bin' est manquant ou non exécutable même après tentative de compilation." >&2
        exit 1
    fi
done

# 3. Lancement du serveur
SERVER_CMD="./zappy_server -p $PORT -x $WIDTH -y $HEIGHT -c $AI_PER_TEAM -f $FREQ -n ${TEAMS[@]}"
$SERVER_CMD &
SERVER_PID=$!
PIDS+=($SERVER_PID)

# Petite pause pour laisser le temps au serveur de démarrer
sleep 1

# 4. Lancement des clients IA (en mode silencieux)
for team in "${TEAMS[@]}"; do
    for ((i=1; i<=$AI_PER_TEAM; i++)); do
        ./zappy_ai -p $PORT -n "$team" -h $HOST > /dev/null 2>&1 &
        PIDS+=($!)
    done
done

# 5. Lancement des clients GUI (en mode silencieux)
for ((i=1; i<=$GUI_COUNT; i++)); do
    ./zappy_gui -p $PORT -h $HOST > /dev/null 2>&1 &
    PIDS+=($!)
done

# Le script attend ici. Seuls les logs du serveur s'affichent.
wait $SERVER_PID

cleanup