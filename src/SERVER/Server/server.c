/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** Server.c
*/

#include "server.h"
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../my.h"
static const server_t *s;

void put_online(server_t *server)
{
    server->server_fd = socket(AF_INET, SOCK_STREAM, 0);
    if (server->server_fd == -1)
        exit_error("socket", 0);
    memset(&server->server_addr, 0, sizeof(server->server_addr));
    server->server_addr.sin_family = AF_INET;
    server->server_addr.sin_addr.s_addr = INADDR_ANY;
    server->server_addr.sin_port = htons(server->port);
    if (bind(server->server_fd, (struct sockaddr *)&server->server_addr,
        sizeof(server->server_addr)) < 0)
        exit_error("bind", 0);
    if (listen(server->server_fd, 5) < 0)
        exit_error("listen", 0);
}

void init_clients(server_t *server)
{
    for (int i = 0; i < MAX_CLIENTS; ++i) {
        server->fds[i].fd = -1;
        server->clients[i].fd = -1;
        server->clients[i].active = 0;
    }
}

void initialize_teams(server_t *server)
{
    char **names = server->config->names;

    for (int i = 0; names[i] != NULL; ++i) {
        server->teams[i].name = strdup(names[i]);
        server->teams[i].nbPlayers = 0;
        server->teams[i].nbMaxPlayers = server->config->nbClients;
        server->teams[i].nbEggs = server->config->nbClients * 2 / 3;
    }
}

server_t *setup_server(config_server_t *config)
{
    server_t *server = malloc(sizeof(server_t));

    memset(server, 0, sizeof(server_t));
    server->config = config;
    server->port = config->port;
    server->nfds = 0;
    init_clients(server);
    initialize_teams(server);
    put_online(server);
    server->clock = create_clock(config->freq);
    signal(SIGINT, handle_signal);
    printf("Serveur en attente de connexions sur le port %d\n", server->port);
    s = server;
    return server;
}

void cleanup_server(server_t *server)
{
    if (server->server_fd != -1)
        close(server->server_fd);
    for (int i = 0; i < server->nfds; i++) {
        if (server->fds[i].fd >= 0)
            close(server->fds[i].fd);
    }
    if (server->clock)
        free(server->clock);
    if (server->config) {
        for (int i = 0; i < server->config->nb_teams; i++)
            free(server->config->names[i]);
        free(server->config);
    }
    free(server);
}
