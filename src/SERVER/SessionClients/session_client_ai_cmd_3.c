/*
** EPITECH PROJECT, 2025
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** sessionClient.c
*/

#include "session_client.h"
#include <stdio.h>

int set_object_f(server_t *server, session_client_t *client,
    const command_t *cmd)
{
    resource_t res_type = -1;
    tile_t *tile = NULL;

    if (cmd->argc < 1)
        return fail_cmd(client->fd);
    res_type = string_to_resource(cmd->args[0]);
    if (res_type >= NB_RESOURCES)
        return fail_cmd(client->fd);
    if (client->inventory[res_type] > 0) {
        client->inventory[res_type]--;
        tile = &server->map[client->y][client->x];
        tile->resources[res_type]++;
        dprintf(client->fd, "ok\n");
        pdr_f(server, client, res_type);
        bct_f(server, client->x, client->y);
    } else
        dprintf(client->fd, "ko\n");
    LOG(LOG_DEBUG, "Player %d set %s", client->idx, cmd->args[0]);
    return 0;
}

int incantation_f(server_t *server, session_client_t *client,
    const command_t *cmd)
{
    const int incantation_idx = find_slot_incantation(server);
    incantation_t *inc = NULL;

    (void)cmd;
    if (!check_incantation_prerequisites(server, client->x, client->y,
        client->level))
        return fail_cmd(client->fd);
    if (incantation_idx == -1)
        return fail_cmd(client->fd);
    inc = &server->incantations[incantation_idx];
    inc->active = true;
    inc->x = client->x;
    inc->y = client->y;
    inc->level = client->level;
    get_current_time(&inc->end_time);
    add_seconds_to_timespec(&inc->end_time, 300.0 / server->config->freq);
    dprintf(client->fd, "Elevation underway\n");
    collect_elevating_players(server, client);
    return 0;
}
