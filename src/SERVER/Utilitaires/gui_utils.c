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

void notify_gui_client(session_client_t *p, server_t *server,
    session_client_t *gui_client)
{
    char buffer[256];

    if (p->is_egg) {
        snprintf(buffer, sizeof(buffer), "enw %d %d %d %d\n",
            p->idx, p->parent_idx, p->x, p->y);
        send(gui_client->fd, buffer, strlen(buffer), 0);
    } else if (p->active && !p->is_gui) {
        snprintf(buffer, sizeof(buffer), "pnw #%d %d %d %d %d %s\n",
            p->idx, p->x, p->y, p->orientation + 1,
            p->level, server->teams[p->team_idx].name);
        send(gui_client->fd, buffer, strlen(buffer), 0);
    }
}

void send_initial_gui_state(server_t *server, session_client_t *gui_client)
{
    LOG(LOG_INFO, "Sending initial state to new GUI client #%d.",
        gui_client->idx);
    msz_h(server, gui_client, NULL);
    sgt_h(server, gui_client, NULL);
    tna_h(server, gui_client, NULL);
    mct_h(server, gui_client, NULL);
    for (int i = 0; i < MAX_CLIENTS; i++)
        notify_gui_client(&server->players[i], server, gui_client);
}
