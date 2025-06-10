/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** server_4.c
*/

#include "server.h"
#include <signal.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../my.h"

void connec_t(server_t *server, session_client_t *client, char *cmd)
{
}

void handle_command_gui(server_t *server, session_client_t *client, char *cmd)
{
}

void spawn_ressources(server_t *server)
{
}

void exec_cmd(server_t *server, int i)
{
    session_client_t *client = &server->clients[i];
    struct timespec now;
    int cmdIdx = 0;
    const command_t *cmd = NULL;

    get_current_time(&now);
    cmdIdx = get_next_ready_command(client->queue, &now);
    if (cmdIdx < 0)
        return;
    cmd = &client->queue->commands[cmdIdx];
    handle_command(server, client, cmd->raw_cmd);
    remove_command_at(client->queue, cmdIdx);
}

void check_life(server_t *server, int i)
{
    session_client_t *client = &server->clients[i];
    const long now_tick = get_elapsed_ticks(server->clock);

    if (now_tick - client->last_food_tick >= 126) {
        client->inventory[FOOD] -= 1;
        client->last_food_tick = now_tick;
        if (client->inventory[FOOD] < 0)
            close_client_connection(server, i);
    }
}
