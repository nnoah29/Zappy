/*
** EPITECH PROJECT, 2025
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** ai.c
*/

#include <stdio.h>
#include <stdlib.h>

#include "../SessionClients/session_client.h"
#include <string.h>

void send_initial_gui_state(server_t *server, session_client_t *gui_client)
{
    session_client_t *p = NULL;

    msz_h(server, gui_client, NULL);
    sgt_h(server, gui_client, NULL);
    tna_h(server, gui_client, NULL);
    mct_h(server, gui_client, NULL);
    for (int i = 0; i < MAX_CLIENTS; i++) {
        p = &server->players[i];
        if (p->fd != -1 || p->is_egg) {
            enw_f(server, p);
            pnw_f(server, p);
        }
    }
}
