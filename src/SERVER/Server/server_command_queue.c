/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** server_command_queue.c
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "server.h"

// Définition de la table des commandes ici
const command_info_t command_table[] = {
    {"Forward", 7}, {"Right", 7}, {"Left", 7}, {"Look", 7},
    {"Inventory", 1}, {"Broadcast", 7}, {"Connect_nbr", 0},
    {"Fork", 42}, {"Eject", 7}, {"Take", 7}, {"Set", 7},
};
const size_t cmd_table_size = sizeof(command_table) / sizeof(command_info_t);

double get_exec_duration(const char *cmd, int freq)
{
    for (size_t i = 0; i < cmd_table_size; i++) {
        if (strncmp(cmd, command_table[i].name,
            strlen(command_table[i].name)) == 0) {
            return (double)command_table[i].units / freq;
        }
    }
    return 0.0;
}

void process_command(char *cmd, const session_client_t *client, int freq)
{
    char *cmd_cpy = strdup(cmd);
    const char *line = strtok(cmd_cpy, "\n");
    struct timespec now;
    double exec_duration = 1.0;

    while (line) {
        get_current_time(&now);
        exec_duration = get_exec_duration(line, freq);
        if (!enqueue_command(client->queue, line, exec_duration, &now))
            send(client->fd, "ko\n", 3, 0);
        line = strtok(NULL, "\n");
    }
    free(cmd_cpy);
}

void receive_client_data(server_t *server, int client_idx)
{
    char buffer[1024];
    const session_client_t *client = &server->players[client_idx];
    const long int len = read(client->fd, buffer, sizeof(buffer) - 1);

    if (len <= 0) {
        LOG(LOG_ERROR, "Client %d à été subitement déconnecté.", client_idx);
        close_client_connection(server, client_idx);
        return;
    }
    buffer[len] = '\0';
    LOG(LOG_DEBUG, "Client %d à envoyé : '%s'", client_idx, buffer);
    process_command(buffer, client, server->config->freq);
}

void exec_cmd(server_t *server, int client_idx)
{
    session_client_t *client = &server->players[client_idx];
    struct timespec now;
    int cmdIdx = 0;
    const command_t *cmd = NULL;

    get_current_time(&now);
    cmdIdx = get_next_ready_command(client->queue, &now);
    if (cmdIdx < 0)
        return;
    cmd = &client->queue->commands[cmdIdx];
    handle_command(server, client, cmd);
    if (client->fd != -1)
        remove_command_at(client->queue, cmdIdx);
}
