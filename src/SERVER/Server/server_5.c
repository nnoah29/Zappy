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

void handle_events(server_t *server, int i)
{
    if (server->fds[i].revents & POLLIN) {
        if (server->fds[i].fd == server->server_fd)
            accept_client_connection(server);
        else
            receive_client_data(server, i);
    }
}

void handle_server(server_t *server)
{
    for (int i = 0; i < server->nfds; ++i) {
        if (server->fds[i].fd < 0 || server->clients[i].is_egg)
            continue;
        handle_events(server, i);
        exec_cmd(server, i);
        check_life(server, i);
    }
}

void handle_command_ai(server_t *server, session_client_t *client, const command_t *cmd)
{

}
