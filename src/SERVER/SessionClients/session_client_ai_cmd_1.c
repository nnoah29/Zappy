/*
** EPITECH PROJECT, 2025
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** sessionClient.c
*/

#include "session_client.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

int forward_f(server_t *server, session_client_t *client,
    const command_t *cmd)
{
    int x = 0;
    int y = 0;

    calculate_direction(server, client, &x, &y);
    map_move_entity(server->map, client, x, y);
    ppo_f(server, client);
    printf("forward\n");
    (void)cmd;
    return 0;
}

int right_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    client->orientation = (client->orientation + 1) % 4;
    ppo_f(server, client);
    printf("right\n");
    (void)cmd;
    return 0;
}

int left_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    client->orientation = (client->orientation - 1 + 4) % 4;
    ppo_f(server, client);
    printf("left\n");
    (void)cmd;
    return 0;
}

int look_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    char *response = calloc(4096, sizeof(char));

    write_vision(server, client, response);
    send(client->fd, response, strlen(response), 0);
    free(response);
    (void)cmd;
    return 0;
}

int inventory_f(server_t *server, session_client_t *client,
    const command_t *cmd)
{
    dprintf(client->fd, "[food %d, linemate %d, deraumere %d, sibur %d, "
        "mendiane %d, phiras %d, thystame %d]\n",
        client->inventory[FOOD], client->inventory[LINEMATE],
        client->inventory[DERAUMERE], client->inventory[SIBUR],
        client->inventory[MENDIANE], client->inventory[PHIRAS],
        client->inventory[THYSTAME]);
    return 0;
}
