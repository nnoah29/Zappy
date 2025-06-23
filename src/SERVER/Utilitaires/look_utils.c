/*
** EPITECH PROJECT, 2025
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** look.c
*/

#include "../SessionClients/session_client.h"
#include <string.h>

// Remplit un buffer avec le contenu textuel d'une tuile.
// Les objets sont séparés par des espaces.
void append_tile_content(char *buffer, const tile_t *tile)
{
    const entity_on_tile_t *current_entity = tile->entities;
    bool needs_space = false;
    char *resource_string;

    while (current_entity) {
        add_space(buffer, needs_space);
        if (current_entity->entity->is_egg)
            strcat(buffer, "egg");
        else
            strcat(buffer, "player");
        needs_space = true;
        current_entity = current_entity->next;
    }
    for (int i = 0; i < NB_RESOURCES; i++) {
        for (int j = 0; j < tile->resources[i]; j++) {
            add_space(buffer, needs_space);
            strcat(buffer, resource_to_string((resource_t)i));
            needs_space = true;
        }
    }
}

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

void get_tile_content(server_t *server, session_client_t *client,
    int_pair_t rel, char *tile_buffer)
{
    int_pair_t pos = {0, 0};

    get_absolute_position(server, client, rel, &pos);
    append_tile_content(tile_buffer, &server->map[pos.y][pos.x]);
}
