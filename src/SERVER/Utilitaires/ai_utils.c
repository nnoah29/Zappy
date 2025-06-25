/*
** EPITECH PROJECT, 2025
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** ai.c
*/

#include "../SessionClients/session_client.h"
#include <string.h>

void write_vision(server_t *server, session_client_t *client, char *response)
{
    int_pair_t rel = {0, 0};
    char tile_buffer[512] = {0};

    if (!response)
        return;
    response[0] = '[';
    for (int forward = 0; forward <= client->level; forward++)
        for (int side = -forward; side <= forward; side++) {
            rel.x = side;
            rel.y = forward;
            add_semicolon(response, side, forward);
            memset(tile_buffer, 0, 512);
            get_tile_content(server, client, rel, tile_buffer);
            strcat(response, tile_buffer);
        }
    strcat(response, "]\n\0");
}

void calculate_direction(server_t *server, session_client_t *client,
    int *x, int *y)
{
    *x = client->x;
    *y = client->y;
    switch (client->orientation) {
    case NORTH:
        *y = (*y - 1 + server->config->map_h) % server->config->map_h;
        break;
    case EAST:
        *x = (*x + 1) % server->config->map_w;
        break;
    case SOUTH:
        *y = (*y + 1) % server->config->map_h;
        break;
    case WEST:
        *x = (*x - 1 + server->config->map_w) % server->config->map_w;
        break;
    default:
        break;
    }
}

int process_ejection_on_entity(entity_on_tile_t **current, server_t *server,
    session_client_t *client)
{
    int_pair_t pos;
    session_client_t *other_player = (*current)->entity;

    *current = (*current)->next;
    if (other_player->idx == client->idx)
        return 0;
    if (other_player->is_egg) {
        edi_f(server, other_player->idx);
        map_detach_entity(&server->map[client->y][client->x], other_player);
        close_client_connection(server, other_player->idx);
        return 1;
    }
    calculate_direction(server, other_player, &pos.x, &pos.y);
    map_move_entity(server->map, other_player, pos.x, pos.y);
    ppo_f(server, other_player);
    pex_f(server, other_player);
    return 1;
}
