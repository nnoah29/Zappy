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

void put_online(server_t *server)
{
    LOG(LOG_INFO, "Mis en ligne du serveur...");
    server->server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server->server_fd == -1)
        exit_error("Socket", 84);
    memset(&server->server_addr, 0, sizeof(server->server_addr));
    server->server_addr.sin_family = AF_INET;
    server->server_addr.sin_addr.s_addr = INADDR_ANY;
    server->server_addr.sin_port = htons(server->port);
    if (bind(server->server_fd, (struct sockaddr *)&server->server_addr,
        sizeof(server->server_addr)) < 0)
        exit_error("Bind", 84);
    if (listen(server->server_fd, 5) < 0)
        exit_error("Listen", 84);
}

void init_clients(server_t *server)
{
    LOG(LOG_DEBUG, "Initialisation des clients...");
    for (int i = 0; i < MAX_CLIENTS; ++i) {
        server->fds[i].fd = -1;
        server->players[i].fd = -1;
        server->players[i].active = false;
        server->players[i].idx = -1;
        server->players[i].is_egg = false;
    }
    for (int i = 0; i < MAX_INCANTATIONS; i++) {
        server->incantations[i].active = false;
    }
}

void initialize_teams(server_t *server)
{
    char **names = server->config->names;

    LOG(LOG_DEBUG, "Initialisation des équipes...");
    for (int i = 0; i < server->config->nb_teams; i++) {
        server->teams[i].name = strdup(names[i]);
        server->teams[i].nbPlayers = 0;
        server->teams[i].nbMaxPlayers = server->config->nbClients;
        server->teams[i].nbEggs = server->config->nbClients * 2 / 3;
        init_eggs(i, server);
    }
}

server_t *setup_server(config_server_t *config)
{
    server_t *server = malloc(sizeof(server_t));

    LOG(LOG_INFO, "Configuration du serveur...");
    srandom((unsigned int)time(NULL));
    memset(server, 0, sizeof(server_t));
    server->config = config;
    server->port = config->port;
    server->nfds = 1;
    server->map = map_create(config->map_w, config->map_h);
    init_clients(server);
    initialize_teams(server);
    put_online(server);
    server->fds[0].fd = server->server_fd;
    server->fds[0].events = POLLIN;
    map_spawn_resources(server);
    re_spawn_ressources_duration(server);
    signal(SIGINT, handle_signal);
    LOG(LOG_INFO, "Serveur en attente de connexions sur le port %d",
        server->port);
    return server;
}
