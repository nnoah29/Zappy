/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** server_init.c
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <time.h>
#include "server.h"
#include "../my.h"

static void cleanup_command_queue(command_queue_t *queue)
{
    if (!queue) {
        return;
    }
    while (queue->size > 0) {
        remove_command_at(queue, queue->head);
    }
    free(queue);
}

static void close_socket(server_t *server)
{
    LOG(LOG_DEBUG, "Fermeture des sockets clients...");
    for (int i = 0; i < MAX_CLIENTS; i++) {
        if (server->players[i].fd != -1) {
            close(server->players[i].fd);
            server->players[i].fd = -1;
        }
        if (server->players[i].queue) {
            cleanup_command_queue(server->players[i].queue);
            server->players[i].queue = NULL;
        }
    }
    if (server->server_fd != -1) {
        LOG(LOG_DEBUG, "Fermeture du socket serveur principal...");
        close(server->server_fd);
        server->server_fd = -1;
    }
}

static void free_teams(server_t *server)
{
    LOG(LOG_DEBUG, "Libération des noms d'équipes...");
    for (int i = 0; i < server->config->nb_teams; i++) {
        if (server->teams[i].name) {
            free(server->config->names[i]);
            server->config->names[i] = NULL;
            free(server->teams[i].name);
            server->teams[i].name = NULL;
        }
    }
}

static void clean_map_and_config(server_t *server)
{
    if (server->map && server->config) {
        LOG(LOG_DEBUG, "Libération de la carte...");
        map_destroy(server->map, server->config->map_w,
            server->config->map_h);
        server->map = NULL;
    }
    if (server->config) {
        free_teams(server);
        LOG(LOG_DEBUG, "Libération de la structure de configuration...");
        free(server->config);
        server->config = NULL;
    }
}

/**
 * @brief Nettoie et libère toutes les ressources allouées par le serveur.
 *        Cette fonction est conçue pour être sûre et éviter les double-frees.
 * @param server Le pointeur vers la structure du serveur.
 */
void cleanup_server(server_t *server)
{
    if (!server) {
        return;
    }
    LOG(LOG_INFO, "Début du nettoyage du serveur...");
    close_socket(server);
    clean_map_and_config(server);
    LOG(LOG_DEBUG, "Libération de la structure serveur...");
    free(server);
    LOG(LOG_INFO, "Serveur nettoyé et arrêté.");
}
