/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** server_3.c
*/

#include <errno.h>

#include "server.h"
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <asm-generic/errno-base.h>

#include "../my.h"
#include "../SessionClients/session_client.h"
int running = 1;

void handle_signal(int signal)
{
    (void)signal;
    running = 0;
}

void register_player_in_team(server_t *server, int i, int j, const char *team)
{
    const int nb = server->teams[j].nbPlayers;

    server->teams[j].players[nb] = &server->clients[i];
    server->teams[j].nbPlayers++;
    server->teams[j].nbMaxPlayers--;
    if (server->teams[j].nbEggs > 0)
        server->teams[j].nbEggs--;
    server->clients[i].team_idx = j;
    server->clients[i].is_egg = false;
    server->clients[i].is_gui = false;
    server->clients[i].active = true;
    server->clients[i].level = 1;
    server->clients[i].x = (int)random() % server->config->map_w;
    server->clients[i].y = (int)random() % server->config->map_h;
    server->clients[i].orientation = ((int)random() % 4) + 1;
    for (int k = 0; k < 7; k++)
        server->clients[i].inventory[k] = 0;
    server->clients[i].inventory[FOOD] = 10;
    map_add_entity(&server->map[server->clients[i].y][server->clients[i].x],
        &server->clients[i]);
    get_current_time(&(server->clients[i].next_food_time));
    get_next_food_consumption(&server->clients[i], server);
}

void assign_team(server_t *server, int i, const char* team)
{
    char buffer[128];

    for (int j = 0; j < server->config->nb_teams; j++) {
        if (strcmp(team, server->teams[j].name) == 0 &&
            server->teams[j].nbEggs > 0 && server->teams[j].nbMaxPlayers > 0){
            register_player_in_team(server, i, j, team);
            snprintf(buffer, sizeof(buffer), "%d\n", server->teams[j].nbMaxPlayers);
            send(server->clients[i].fd, buffer, strlen(buffer), 0);
            snprintf(buffer, sizeof(buffer), "%d %d\n", server->config->map_w, server->config->map_h);
            send(server->clients[i].fd, buffer, strlen(buffer), 0);
            pnw_f(server, &server->clients[i], NULL);
            printf("Client %d a rejoint l'équipe '%s'.\n", server->clients[i].team_idx, team);
            return;
        }
    }
    printf("Client %d a échoué à rejoindre l'équipe '%s' (invalide ou pleine).\n", server->clients[i].team_idx, team);
    send(server->clients[i].fd, "Team does not exit\n", 19, 0);
    close_client_connection(server, i);
}

void handle_command(server_t *server, session_client_t *client, const command_t *cmd)
{
    printf("cmd: %s\n", cmd->raw_cmd);
    if (!client->active) {
        connec_t(server, client, cmd);
        return;
    }
    handle_command_ai(server, client, cmd);
}

void handle_game_logic(server_t *server)
{
    spawn_ressources(server);
    for (int i = 0; i < MAX_CLIENTS; i++) {
        if (server->clients[i].fd == -1 || server->clients[i].is_egg || !server->clients[i].active)
            continue;
        exec_cmd(server, i);
        check_life(server, i);
    }
}

void run_server(server_t *server)
{
    int ready = 0;
    int timeout = 0;

    while (running) {
        timeout = calculate_next_event_timeout(server);
        ready = poll(server->fds, server->nfds, timeout);

        if (ready < 0)
            continue;
        if (ready > 0)
            handle_network_events(server);
        handle_game_logic(server);
    }
}
