/*
** EPITECH PROJECT, 2025
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** client_utils.c
*/

#include <string.h>

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

void add_space(char *buffer, bool need_space)
{
    if (need_space)
        strcat(buffer, " ");
}

void add_semicolon(char *response, int side, int forward)
{
    if (forward != 0 || side != 0)
        strcat(response, ",");
}

const char *resource_to_string(resource_t res)
{
    static const char *resource_names[] = {
        "food", "linemate", "deraumere", "sibur",
        "mendiane", "phiras", "thystame"
    };

    if (res < NB_RESOURCES) {
        return resource_names[res];
    }
    return "";
}
