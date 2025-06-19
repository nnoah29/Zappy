/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** commandes.c
*/

#include "commandes.h"
#include <stdlib.h>
#include <string.h>

int dequeue_command(command_queue_t *queue)
{
    if (queue->size == 0)
        return 0;
    free(queue->commands[queue->head].raw_cmd);
    queue->commands[queue->head].raw_cmd = NULL;
    queue->head = (queue->head + 1) % MAX_COMMANDS;
    queue->size--;
    return 1;
}

command_t *peek_command(command_queue_t *queue)
{
    if (queue->size == 0)
        return NULL;
    return &queue->commands[queue->head];
}

int is_command_ready(command_t *cmd, struct timespec *now)
{
    if (!cmd)
        return 0;
    if (now->tv_sec > cmd->ready_at.tv_sec)
        return 1;
    if (now->tv_sec == cmd->ready_at.tv_sec && now->tv_nsec >=
        cmd->ready_at.tv_nsec)
        return 1;
    return 0;
}

void setup_command(command_queue_t *queue, const char *cmd, int index, double duration)
{
    char *cmd_copy = strdup(cmd);
    char *token = strtok(cmd_copy, " ");
    int i = 0;

    if (!token) {
        free(cmd_copy);
        return;
    }
    queue->commands[index].raw_cmd = strdup(token);
    queue->commands[index].args = malloc(sizeof(char *) * (MAX_ARGS + 1));
    for (; i < MAX_ARGS; i++) {
        token = strtok(NULL, " ");
        if (!token)
            break;
        queue->commands[index].args[i] = strdup(token);
    }
    queue->commands[index].args[i] = NULL;
    queue->commands[index].duration = duration;
    free(cmd_copy);
}