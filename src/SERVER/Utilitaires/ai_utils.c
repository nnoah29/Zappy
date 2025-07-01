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

void write_vision(server_t *server, session_client_t *client,
    dynamic_buffer_t *db)
{
    int_pair_t rel;
    bool is_first = true;

    buffer_append(db, "[");
    for (int forward = 0; forward <= client->level; forward++) {
        for (int side = -forward; side <= forward; side++) {
            buffer_append(db, !is_first ? "," : "");
            rel.x = side;
            rel.y = forward;
            get_and_append_tile_content(server, client, rel, db);
            is_first = false;
        }
    }
    buffer_append(db, "]\n");
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

int process_ejection_on_entity(entity_on_tile_t *current_node,
    server_t *server, session_client_t *ejector)
{
    session_client_t *other_player = NULL;
    int_pair_t pos;

    other_player = current_node->entity;
    if (!other_player || other_player->idx == ejector->idx)
        return 0;
    if (other_player->is_egg) {
        edi_f(server, other_player->idx);
        map_detach_entity(&server->map[ejector->y][ejector->x], other_player);
        close_client_connection(server, other_player->idx);
        return 1;
    }
    calculate_direction(server, ejector, &pos.x, &pos.y);
    map_move_entity(server->map, other_player, pos.x, pos.y);
    ppo_f(server, other_player);
    pex_f(server, other_player);
    return 1;
}

void distribute_message(server_t *server, session_client_t *client,
    const char *message_text)
{
    char message_to_send[2048];
    int k = 0;
    const session_client_t *receiver = NULL;

    for (int i = 0; i < MAX_CLIENTS; i++) {
        receiver = &server->players[i];
        if (!receiver->active || receiver->is_gui || receiver->is_egg)
            continue;
        k = (receiver->idx == client->idx) ? 0 : 1;
        snprintf(message_to_send, sizeof(message_to_send),
            "message %d, %s\n", k, message_text);
        send(receiver->fd, message_to_send, strlen(message_to_send), 0);
    }
    dprintf(client->fd, "ok\n");
    pbc_f(server, client, message_text);
}
