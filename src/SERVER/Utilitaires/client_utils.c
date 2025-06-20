/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** client_utils.c
*/

#include "../my.h"

int find_free_client_slot(server_t *server)
{
    for (int i = 0; i < MAX_CLIENTS; i++) {
        if (server->clients[i].fd == -1) {
            return i;
        }
    }
    return -1;
}

int find_client_by_fd(server_t *server, int fd)
{
    for (int i = 0; i < MAX_CLIENTS; i++) {
        if (server->clients[i].fd == fd) {
            return i;
        }
    }
    return -1;
}