/*
** EPITECH PROJECT, 2025
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** session_client_gui.c
*/

#include "session_client.h"
#include "../Server/server.h"
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../my.h"

/// Envoie la taille de la map (msz)
int msz_h(server_t *server, session_client_t *client, const command_t *cmd)
{
    (void)cmd;
    dprintf(client->fd, "msz %d %d\n", server->config->map_w,
        server->config->map_h);
    return 0;
}

/// Envoie le contenu d’une case spécifique (bct X Y)
int bct_h(server_t *server, session_client_t *client, const command_t *cmd)
{
    int x = 0;
    int y = 0;
    const tile_t *tile = NULL;

    if (cmd->args[0] == NULL || cmd->args[1] == NULL) {
        dprintf(client->fd, "sbp\n");
        return 84;
    }
    x = atoi(cmd->args[0]);
    y = atoi(cmd->args[1]);
    if (x < 0 || x >= server->config->map_w || y < 0 ||
        y >= server->config->map_h) {
        dprintf(client->fd, "sbp\n");
        return 84;
    }
    tile = &server->map[y][x];
    dprintf(client->fd, "bct %d %d %d %d %d %d %d %d %d\n",
        x, y, tile->resources[0], tile->resources[1], tile->resources[2],
        tile->resources[3], tile->resources[4], tile->resources[5],
        tile->resources[6]);
}

/// Envoie le contenu de toute la map (mct)
int mct_h(server_t *server, session_client_t *client, const command_t *cmd)
{
    const tile_t *tile = NULL;

    for (int y = 0; y < server->config->map_h; y++) {
        for (int x = 0; x < server->config->map_w; x++) {
            tile = &server->map[y][x];
            dprintf(client->fd, "bct %d %d %d %d %d %d %d %d %d\n",
                x, y, tile->resources[0], tile->resources[1],
                tile->resources[2], tile->resources[3], tile->resources[4],
                tile->resources[5], tile->resources[6]);
        }
    }
    (void)cmd;
    return 0;
}

/// Envoie la liste des équipes (tna)
int tna_h(server_t *server, session_client_t *client, const command_t *cmd)
{
    for (int i = 0; i < server->config->nb_teams; i++) {
        dprintf(client->fd, "tna %s\n", server->teams[i].name);
    }
    (void)cmd;
    return 0;
}

/// Envoie la position d’un joueur (#n) (ppo)
int ppo_h(server_t *server, session_client_t *client, const command_t *cmd)
{
    int player_idx = 0;
    const session_client_t *player = NULL;

    if (cmd->args[0] == NULL || cmd->args[0][0] != '#') {
        dprintf(client->fd, "sbp\n");
        return 84;
    }
    player_idx = atoi(&cmd->args[0][1]);
    player = &server->players[player_idx];
    if (player_idx != -1) {
        dprintf(client->fd, "ppo %d %d %d %d\n", player->idx,
            player->x, player->y, player->orientation);
    }
    (void)server;
    return 0;
}
