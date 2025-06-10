/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** server_5.c
*/

#include "server.h"
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../my.h"

void handle_server(server_t *server)
{
    for (int i = 0; i < server->nfds; ++i) {
        if (server->fds[i].fd < 0 || server->clients[i].is_egg)
            continue;
        handleEntry(server, i);
        execCmd(server, i);
        checkLife(server, i);
    }
}
