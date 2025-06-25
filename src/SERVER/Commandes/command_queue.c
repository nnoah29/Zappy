/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** command_queue.c
*/

#include "command.h"
#include <stdlib.h>
#include <string.h>

#include "../Logger/logger.h"

static int find_best_index(int best_index, int index, command_queue_t *queue,
                           command_t *cmd)
{
    if (best_index == -1 ||
        timespec_cmp(&cmd->ready_at,
        &queue->commands[best_index].ready_at) < 0) {
        best_index = index;
    }
    return best_index;
}

void init_command_queue(command_queue_t *queue)
{
    queue->head = 0;
    queue->tail = 0;
    queue->size = 0;
}

int enqueue_command(command_queue_t *queue, const char *cmd, double duration,
    struct timespec *now)
{
    const int index = queue->tail;

    if (queue->size >= MAX_COMMANDS)
        return 0;
    setup_command(queue, cmd, index, duration);
    queue->commands[index].ready_at = *now;
    add_seconds_to_timespec(&queue->commands[index].ready_at, duration);
    queue->tail = (queue->tail + 1) % MAX_COMMANDS;
    queue->size++;
    return 1;
}

int get_next_ready_command(command_queue_t *queue, struct timespec *now)
{
    int best_index = -1;
    int index = 0;
    command_t *cmd = NULL;

    if (queue->size == 0)
        return -1;
    for (int i = 0; i < queue->size; ++i) {
        index = (queue->head + i) % MAX_COMMANDS;
        cmd = &queue->commands[index];
        if (is_command_ready(cmd, now))
            best_index = find_best_index(best_index, index, queue, cmd);
    }
    return best_index;
}

int remove_command_at(command_queue_t *queue, int index)
{
    int next = -1;

    if (queue->size == 0)
    {
    LOG(LOG_WARN, "Segfault");
        return 0;
    }
    free(queue->commands[index].raw_cmd);
    for (int i = 0; i < queue->commands[index].argc; ++i)
        free(queue->commands[index].args[i]);
    for (int i = index; i != queue->tail; i = (i + 1) % MAX_COMMANDS) {
        next = (i + 1) % MAX_COMMANDS;
        queue->commands[i] = queue->commands[next];
    }
    queue->tail = (queue->tail - 1 + MAX_COMMANDS) % MAX_COMMANDS;
    queue->size--;
    return 1;
}
