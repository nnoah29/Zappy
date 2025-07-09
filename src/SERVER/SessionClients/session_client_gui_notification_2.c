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

/// Notifie le résultat d’une incantation (pie)
void pie_f(server_t *server, int x, int y, int result)
{
    char buffer[64];

    snprintf(buffer, sizeof(buffer), "pie %d %d %d\n", x, y, result);
    send_to_all_guis(server, buffer);
}

/// Notifie qu’un œuf a été pondu (pfk)
void pfk_f(server_t *server, session_client_t *player)
{
    char buffer[64];

    snprintf(buffer, sizeof(buffer), "pfk #%d\n", player->idx);
    send_to_all_guis(server, buffer);
}

/// Notifie qu’un joueur a déposé une ressource (pdr)
void pdr_f(server_t *server, session_client_t *player, int resource_idx)
{
    char buffer[64];

    snprintf(buffer, sizeof(buffer), "pdr #%d %d\n", player->idx, resource_idx);
    send_to_all_guis(server, buffer);
}

/// Notifie qu’un joueur a ramassé une ressource (pgt)
void pgt_f(server_t *server, session_client_t *player, int resource_idx)
{
    char buffer[64];

    snprintf(buffer, sizeof(buffer), "pgt #%d %d\n", player->idx, resource_idx);
    send_to_all_guis(server, buffer);
}

/// Notifie la mort d’un joueur (pdi)
void pdi_f(server_t *server, session_client_t *player)
{
    char buffer[64];

    snprintf(buffer, sizeof(buffer), "pdi #%d\n", player->idx);
    send_to_all_guis(server, buffer);
}
