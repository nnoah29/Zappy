/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** server_3.c
*/

#include "server.h"
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../my.h"
static int running = 1;

void handle_signal(int signal)
{
    (void)signal;
    running = 0;
}

void register_player_in_team(server_t *server, int i, int j, char *team)
{
    const int nb = server->teams[j].nbPlayers;

    server->teams[j].players[nb] = &server->clients[i];
    server->teams[j].nbPlayers++;
    server->teams[j].nbEggs--;
    server->teams[j].nbMaxPlayers--;
    server->clients[i].team_idx = j;
    server->clients[i].is_egg = false;
    server->clients[i].is_gui = false;
}

void assign_team(server_t *server, int i, char *team)
{
    if (strcmp(team, "GRAPHIC") == 0) {
        server->clients[i].team_idx = -1;
        server->clients[i].is_egg = false;
        server->clients[i].is_gui = true;
        server->clients[i].active = true;
        return;
    }
    for (int j = 0; j < server->config->nb_teams; j++) {
        if (strcmp(team, server->teams[j].name) == 0 &&
            server->teams[j].nbEggs > 0 && server->teams[j].nbMaxPlayers > 0){
            register_player_in_team(server, i, j, team);
            return;
        }
    }
    send(server->clients[i].fd, "Team does not exit\n", 19, 0);
    close_client_connection(server, i);
}

void handle_command(server_t *server, session_client_t *client, char *cmd)
{
    if (!client->active) {
        connec_t(server, client, cmd);
        return;
    }
    if (client->is_gui) {
        handle_command_gui(server, client, cmd);
        return;
    }
    printf("cmd: %s\n", cmd);
}

void run_server(server_t *server)
{
    int ready = 0;

    while (running) {
        ready = poll(server->fds, server->nfds, -1);
        if (ready < 0)
            continue;
        handle_server(server);
        spawn_ressources(server);
    }
}
