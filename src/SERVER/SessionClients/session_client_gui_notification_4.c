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

/// Notifie une commande non autorisée (suc)
void suc_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    (void)server;
    (void)client;
    (void)cmd;
    printf("suc\n");
}

/// Notifie une commande invalide (sbp)
void sbp_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    (void)server;
    (void)client;
    (void)cmd;
    printf("sbp\n");
}

/// Notifie qu’un joueur a rejoint le jeu (pnw)
void pnw_f(server_t *server, session_client_t *client)
{
    char buffer[128];

    snprintf(buffer, sizeof(buffer), "pnw #%d %d %d %d %d %s\n",
        client->idx, client->x, client->y, client->orientation, client->level, server->teams[client->team_idx].name);
    send_to_all_guis(server, buffer);
    printf("pnw\n");
}