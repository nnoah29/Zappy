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

void send_to_all_guis(server_t *server, const char *msg)
{
    for (int i = 0; i < MAX_CLIENTS; ++i) {
        if (server->players[i].fd < 0 || !server->players[i].is_gui
            || server->players[i].is_egg)
            continue;
        send(server->players[i].fd, msg, strlen(msg), 0);
    }
}

/// Envoie la position d’un joueur (#n) (ppo)
void ppo_f(server_t *server, session_client_t *client)
{
    char buffer[100];

    snprintf(buffer, sizeof(buffer), "ppo #%d %d %d %d\n",
        client->idx, client->x, client->y, client->orientation + 1);
    send_to_all_guis(server, buffer);
}

/// Notifie qu’un joueur a été éjecté (pex)
void pex_f(server_t *server, session_client_t *client)
{
    char buffer[64];

    snprintf(buffer, sizeof(buffer), "pex %d\n", client->idx);
    send_to_all_guis(server, buffer);
}

/// Notifie qu’un joueur a envoyé un message (pbc)
void pbc_f(server_t *server, session_client_t *client, const char *message)
{
    char buffer[1024];

    snprintf(buffer, sizeof(buffer), "pbc %d %s\n", client->idx, message);
    send_to_all_guis(server, buffer);
}

/// Notifie le début d’une incantation (pic)
void pic_f(server_t *server, session_client_t *client,
    const char *player_list_str)
{
    char buffer[2048];

    snprintf(buffer, sizeof(buffer), "pic %d %d %d %s\n", client->x,
        client->y, client->level, player_list_str);
    send_to_all_guis(server, buffer);
}
