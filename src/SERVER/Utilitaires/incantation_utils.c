/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** server.h
*/

#include <stdio.h>
#include "../Server/server.h"
#include <string.h>

static const incantation_req_t G_REQ_TABLE[] = {
    {1, 1, {0, 1, 0, 0, 0, 0, 0}},
    {2, 2, {0, 1, 1, 1, 0, 0, 0}},
    {3, 2, {0, 2, 0, 1, 0, 2, 0}},
    {4, 4, {0, 1, 1, 2, 0, 1, 0}},
    {5, 4, {0, 1, 2, 1, 3, 0, 0}},
    {6, 6, {0, 1, 2, 3, 0, 1, 0}},
    {7, 6, {0, 2, 2, 2, 2, 2, 1}},
};

bool check_incantation_prerequisites(server_t *server, int x, int y,
    int level)
{
    int players_on_tile_at_level = 0;
    const tile_t *tile = &server->map[y][x];
    const entity_on_tile_t *current = tile->entities;
    const incantation_req_t *req = NULL;

    if (level > 7)
        return false;
    req = &G_REQ_TABLE[level - 1];
    for (int i = 1; i < NB_RESOURCES; i++)
        if (tile->resources[i] < req->res[i])
            return false;
    while (current) {
        if (!current->entity->is_egg && current->entity->level == level)
            players_on_tile_at_level++;
        current = current->next;
    }
    return players_on_tile_at_level >= req->players;
}

int find_slot_incantation(server_t *server)
{
    for (int i = 0; i < MAX_INCANTATIONS; i++) {
        if (!server->incantations[i].active) {
            return i;
        }
    }
    return -1;
}

void collect_elevating_players(server_t *server, session_client_t *client)
{
    char player_list_str[1024] = {0};
    char player_id_str[16];
    const entity_on_tile_t *current =
        server->map[client->y][client->x].entities;

    while (current) {
        if (!current->entity->is_egg &&
            current->entity->level == client->level) {
            current->entity->is_elevating = true;
            memset(player_id_str, 0, sizeof(player_id_str));
            snprintf(player_id_str, sizeof(player_id_str),
                " #%d", current->entity->idx);
            strcat(player_list_str, player_id_str);
        }
        current = current->next;
    }
    pic_f(server, client, player_list_str);
}

static void finish_incantation_success(server_t *server, incantation_t *inc)
{
    tile_t *tile = &server->map[inc->y][inc->x];
    const entity_on_tile_t *current = tile->entities;
    const incantation_req_t *req = &G_REQ_TABLE[inc->level - 1];

    LOG(LOG_INFO, "Incantation at (%d, %d) succeeded.", inc->x, inc->y);
    pie_f(server, inc->x, inc->y, 1);
    for (int i = 1; i < NB_RESOURCES; i++)
        tile->resources[i] -= req->res[i];
    bct_f(server, inc->x, inc->y);
    while (current) {
        if (current->entity->is_elevating &&
            current->entity->level == inc->level) {
            current->entity->level++;
            current->entity->is_elevating = false;
            dprintf(current->entity->fd, "Current level: %d\n",
                current->entity->level);
        }
        current = current->next;
    }
    check_win_condition(server);
}

static void finish_incantation_failure(server_t *server, incantation_t *inc)
{
    const entity_on_tile_t *current = server->map[inc->y][inc->x].entities;

    LOG(LOG_INFO, "Incantation at (%d, %d) failed.", inc->x, inc->y);
    pie_f(server, inc->x, inc->y, 0);
    while (current) {
        if (current->entity->is_elevating &&
            current->entity->level == inc->level) {
            current->entity->is_elevating = false;
            dprintf(current->entity->fd, "ko\n");
        }
        current = current->next;
    }
}

void check_and_finish_incantations(server_t *server)
{
    struct timespec now;
    incantation_t *inc = NULL;

    get_current_time(&now);
    for (int i = 0; i < MAX_INCANTATIONS; i++) {
        inc = &server->incantations[i];
        if (!inc->active || timespec_cmp(&now, &inc->end_time) < 0) {
            continue;
        }
        if (check_incantation_prerequisites(server, inc->x, inc->y,
            inc->level)) {
            finish_incantation_success(server, inc);
        } else {
            finish_incantation_failure(server, inc);
        }
        inc->active = false;
    }
}
