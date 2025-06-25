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
    printf("set_object\n");
    return 0;
}
