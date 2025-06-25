/*
** EPITECH PROJECT, 2025
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** look.c
*/

#include <stdio.h>

#include "../SessionClients/session_client.h"
#include <string.h>

void calculate_direction_offset(int orientation, int *dx, int *dy,
    int_pair_t rel)
{
    switch (orientation) {
        case NORTH:
            *dx = rel.x;
            *dy = -rel.y;
            break;
        case EAST:
            *dx = rel.y;
            *dy = rel.x;
            break;
        case SOUTH:
            *dx = -rel.x;
            *dy = rel.y;
            break;
        case WEST:
            *dx = -rel.y;
            *dy = -rel.x;
            break;
        default:
            break;
    }
}

void get_absolute_position(server_t *s, session_client_t *c,
    int_pair_t rel, int_pair_t *pos)
{
    int dx = 0;
    int dy = 0;

    calculate_direction_offset(c->orientation, &dx, &dy, rel);
    pos->x = (c->x + dx + s->config->map_w) % s->config->map_w;
    pos->y = (c->y + dy + s->config->map_h) % s->config->map_h;
}

/**
 * @brief AJOUTE le contenu textuel d'une tuile à un buffer dynamique existant.
 */
void append_tile_content_to_buffer(dynamic_buffer_t *db, const tile_t *tile)
{
    const entity_on_tile_t *current_entity = tile->entities;
    bool needs_space = (db->len > 0 && db->buffer[db->len - 1] != ','
        && db->buffer[db->len - 1] != '[');

    while (current_entity) {
        buffer_append(db, needs_space ? " " : "");
        buffer_append(db, current_entity->entity->is_egg ? "egg" : "player");
        needs_space = true;
        current_entity = current_entity->next;
    }
    for (int i = 0; i < NB_RESOURCES; i++) {
        for (int j = 0; j < tile->resources[i]; j++) {
            buffer_append(db, needs_space ? " " : "");
            buffer_append(db, resource_to_string((resource_t)i));
            needs_space = true;
        }
    }
}

// Calcule la position d'une tuile relative et AJOUTE son contenu au buffer.
void get_and_append_tile_content(server_t *server, session_client_t *client,
    int_pair_t rel, dynamic_buffer_t *db)
{
    int_pair_t pos;

    get_absolute_position(server, client, rel, &pos);
    append_tile_content_to_buffer(db, &server->map[pos.y][pos.x]);
}

resource_t string_to_resource(const char *str)
{
    static const char *names[] = {"food", "linemate", "deraumere", "sibur",
        "mendiane", "phiras", "thystame"};

    for (int i = 0; i < NB_RESOURCES; i++) {
        if (strcmp(str, names[i]) == 0) {
            return (resource_t)i;
        }
    }
    return NB_RESOURCES;
}
