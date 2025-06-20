/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** sessionClient.c
*/

#include "session_client.h"
#include <stdio.h>

void forward_f(server_t *server, session_client_t *client,
    const command_t *cmd)
{
    int x = client->x;
    int y = client->y;

    switch (client->orientation) {
    case NORTH:
        y = (y - 1 + server->config->map_h) % server->config->map_h;
        break;
    case EAST:
        x = (x + 1) % server->config->map_w;
        break;
    case SOUTH:
        y = (y + 1) % server->config->map_h;
        break;
    case WEST:
        x = (x - 1 + server->config->map_w) % server->config->map_w;
        break;
    }
    map_move_entity(server->map, client, x, y);
    ppo_f(server, client);
    (void)cmd;
}

void right_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    client->orientation = (client->orientation + 1) % 4;
    ppo_f(server, client);
    printf("right\n");
    (void)cmd;
}

void left_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    client->orientation = (client->orientation - 1 + 4) % 4;
    ppo_f(server, client);
    printf("left\n");
    (void)cmd;
}

void look_f(server_t *server, session_client_t *client, const command_t *cmd)
{
    (void)server;
    (void)client;
    (void)cmd;
    printf("look\n");
}

void inventory_f(server_t *server, session_client_t *client,
    const command_t *cmd)
{
    (void)server;
    (void)client;
    (void)cmd;
    printf("inventory\n");
}
