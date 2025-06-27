/*
** EPITECH PROJECT, 2025
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** sessionClient.c
*/

#include "../SessionClients/session_client.h"
#include <stdio.h>
#include <stdlib.h>

int find_free_slot(server_t *server, session_client_t *client)
{
    if (server->teams[client->team_idx].nbPlayers >=
        server->config->nbClients) {
        LOG(LOG_WARN, "Player %d failed to fork: team '%s' is full.",
            client->idx, server->teams[client->team_idx].name);
        return -1;
    }
    for (int i = 0; i < MAX_CLIENTS; i++) {
        if (server->players[i].fd == -1 && !server->players[i].is_egg) {
            return i;
        }
    }
    LOG(LOG_WARN, "Server critical: no free entity slots "
        "available to create an egg.");
    return -1;
}

void laying_process(server_t *server, session_client_t *client, int egg_idx)
{
    session_client_t *egg = &server->players[egg_idx];

    egg->is_egg = true;
    egg->active = false;
    egg->fd = -1;
    egg->idx = egg_idx;
    egg->x = client->x;
    egg->y = client->y;
    egg->team_idx = client->team_idx;
    egg->parent_idx = client->idx;
    egg->level = 1;
    egg->orientation = (int)random() % 4;
    server->teams[client->team_idx].nbEggs++;
    map_add_entity(&server->map[egg->y][egg->x], egg);
    dprintf(client->fd, "ok\n");
    pfk_f(server, client);
    enw_f(server, egg);
}
