/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** sessionClient.c
*/

#include "session_client.h"
#include "../Server/server.h"
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../my.h"

/// Envoie le niveau d’un joueur (#n) (plv)
void plv_h(server_t *server, session_client_t *client, const command_t *cmd)
{
    int player_idx = 0;
    const session_client_t *player = NULL;

    if (cmd->args[0] == NULL || cmd->args[0][0] != '#') {
        dprintf(client->fd, "sbp\n");
        return;
    }
    player_idx = atoi(&cmd->args[0][1]);
    player = &server->clients[player_idx];
    if (player_idx != -1) {
        dprintf(client->fd, "plv %d %d\n", player->idx,
            player->level);
    }
}

/// Envoie l’inventaire d’un joueur (#n) (pin)
void pin_h(server_t *server, session_client_t *client, const command_t *cmd)
{
    int player_idx = 0;
    const session_client_t *player = NULL;

    if (cmd->args[0] == NULL || cmd->args[0][0] != '#') {
        dprintf(client->fd, "sbp\n");
        return;
    }
    player_idx = atoi(&cmd->args[0][1]);
    if (player_idx != -1) {
        player = &server->clients[player_idx];
        dprintf(client->fd, "pin %d %d %d %d %d %d %d %d %d %d\n",
            player->idx, player->x, player->y, player->inventory[0],
            player->inventory[1], player->inventory[2], player->inventory[3],
            player->inventory[4], player->inventory[5], player->inventory[6]);
    }
}

/// Envoie le temps d’exécution d’une action (sgt)
void sgt_h(server_t *server, session_client_t *client, const command_t *cmd)
{
    dprintf(client->fd, "sgt %d\n", server->config->freq);
    (void)cmd;
}

/// Définit le temps d’exécution d’une action (sst T)
void sst_h(server_t *server, session_client_t *client, const command_t *cmd)
{
    char buffer[64];
    int new_freq = 0;

    if (cmd->args[0] == NULL) {
        dprintf(client->fd, "sbp\n");
        return;
    }
    new_freq = atoi(cmd->args[0]);
    if (new_freq > 0) {
        server->config->freq = new_freq;
        snprintf(buffer, sizeof(buffer), "sgt %d\n", server->config->freq);
        send_to_all_guis(server, buffer);
    } else {
        dprintf(client->fd, "sbp\n");
    }
}
