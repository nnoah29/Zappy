/*
** EPITECH PROJECT, 2024
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
void msz_h(server_t *server, session_client_t *client, const command_t *cmd)
{
    (void)cmd;
    dprintf(client->fd, "msz %d %d\n", server->config->map_w, server->config->map_h);
}

/// Envoie le contenu d’une case spécifique (bct X Y)
void bct_h(server_t *server, session_client_t *client, const command_t *cmd)
{
    int x = 0;
    int y = 0;
    const tile_t *tile = NULL;

    if (cmd->args[0] == NULL || cmd->args[1] == NULL) {
        dprintf(client->fd, "sbp\n"); return;
    }
    x = atoi(cmd->args[0]);
    y = atoi(cmd->args[1]);
    if (x < 0 || x >= server->config->map_w || y < 0 || y >= server->config->map_h) {
        dprintf(client->fd, "sbp\n");
        return;
    }
    tile = &server->map[y][x];
    dprintf(client->fd, "bct %d %d %d %d %d %d %d %d %d\n",
        x, y, tile->resources[0], tile->resources[1], tile->resources[2],
        tile->resources[3], tile->resources[4], tile->resources[5], tile->resources[6]);
}

/// Envoie le contenu de toute la map (mct)
void mct_h(server_t *server, session_client_t *client, const command_t *cmd)
{
    const tile_t *tile = NULL;

    for (int y = 0; y < server->config->map_h; y++) {
        for (int x = 0; x < server->config->map_w; x++) {
            tile = &server->map[y][x];
            dprintf(client->fd, "bct %d %d %d %d %d %d %d %d %d\n",
                x, y, tile->resources[0], tile->resources[1], tile->resources[2],
                tile->resources[3], tile->resources[4], tile->resources[5], tile->resources[6]);
        }
    }
    (void)cmd;
}

/// Envoie la liste des équipes (tna)
void tna_h(server_t *server, session_client_t *client, const command_t *cmd)
{
    for (int i = 0; i < server->config->nb_teams; i++) {
        dprintf(client->fd, "tna %s\n", server->teams[i].name);
    }
    (void)cmd;
}

/// Envoie la position d’un joueur (#n) (ppo)
void ppo_h(server_t *server, session_client_t *client, const command_t *cmd)
{
    int player_idx = 0;

    if (cmd->args[0] == NULL || cmd->args[0][0] != '#') {
        dprintf(client->fd, "sbp\n");
        return;
    }
    player_idx = atoi(&cmd->args[0][1]);
    if (player_idx != -1) {
        dprintf(client->fd, "ppo %d %d %d %d\n", client->idx, client->x, client->y, client->orientation);
    }
    (void)server;
}
