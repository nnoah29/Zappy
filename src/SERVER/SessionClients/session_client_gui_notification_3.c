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

/// Notifie qu’un joueur a pondu un œuf (enw)
void enw_f(server_t *server, session_client_t *egg)
{
    char buffer[128];

    if (!egg->is_egg)
        return;
    snprintf(buffer, sizeof(buffer), "enw #%d %d %d %d\n",
        egg->idx, egg->parent_idx, egg->x, egg->y);
    send_to_all_guis(server, buffer);
}

/// Notifie qu’un œuf a été éclos (ebo)
void ebo_f(server_t *server, int egg_id)
{
    char buffer[64];

    snprintf(buffer, sizeof(buffer), "ebo #%d\n", egg_id);
    send_to_all_guis(server, buffer);
}

/// Notifie qu’un œuf est mort (edi)
void edi_f(server_t *server, int egg_id)
{
    char buffer[64];

    snprintf(buffer, sizeof(buffer), "edi #%d\n", egg_id);
    send_to_all_guis(server, buffer);
}

/// Notifie la fin du jeu (seg)
void seg_f(server_t *server, const char *winning_team)
{
    char buffer[128];

    snprintf(buffer, sizeof(buffer), "seg %s\n", winning_team);
    send_to_all_guis(server, buffer);
}

/// Envoie un message du serveur au GUI (smg)
void smg_f(server_t *server, const char *message)
{
    char buffer[1024];

    snprintf(buffer, sizeof(buffer), "smg %s\n", message);
    send_to_all_guis(server, buffer);
}
