/*
** EPITECH PROJECT, 2025
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** sessionClient.c
*/

#include "session_client.h"
#include <stdio.h>

int broadcast_f(server_t *server, session_client_t *client,
    const command_t *cmd)
{
    printf("broadcast\n");
    return 0;
}

int connect_nbr_f(server_t *server, session_client_t *client,
    const command_t *cmd)
{
    const int team_idx = client->team_idx;
    int remaining_slots = 0;

    if (team_idx >= 0 && team_idx < server->config->nb_teams) {
        remaining_slots = server->teams[team_idx].nbMaxPlayers;
    }
    dprintf(client->fd, "%d\n", remaining_slots);
    printf("connect_nbr\n");
    (void)cmd;
    return 0;
}

int fork_f(server_t *server, session_client_t *client,
    const command_t *cmd)
{
    printf("fork\n");
    return 0;
}

int eject_f(server_t *server, session_client_t *client,
    const command_t *cmd)
{
    const tile_t *tile = &server->map[client->y][client->x];
    entity_on_tile_t *current = tile->entities;
    session_client_t *other_player = NULL;
    bool ejected_someone = false;
    int_pair_t pos;

    while (current) {
        if (process_ejection_on_entity(&current, server, client))
            ejected_someone = true;
    }
    printf("eject\n");
    dprintf(client->fd, ejected_someone ? "ok\n" : "ko\n");
    return 0;
}

int take_object_f(server_t *server, session_client_t *client,
    const command_t *cmd)
{
    resource_t res_type = -1;
    tile_t *tile = NULL;

    if (cmd->argc < 1)
        return fail_cmd(client->fd);
    res_type = string_to_resource(cmd->args[0]);
    if (res_type >= NB_RESOURCES)
        return fail_cmd(client->fd);
    tile = &server->map[client->y][client->x];
    if (tile->resources[res_type] > 0) {
        tile->resources[res_type]--;
        client->inventory[res_type]++;
        dprintf(client->fd, "ok\n");
        pgt_f(server, client, res_type);
        bct_f(server, client->x, client->y);
    } else
        dprintf(client->fd, "ko\n");
    printf("take_object\n");
    return 0;
}
