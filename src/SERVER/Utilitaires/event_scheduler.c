/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** event_scheduler.c
*/

#include "../my.h"

static long timespec_diff_ms(const struct timespec *start, const struct timespec *end)
{
    if (end->tv_sec < start->tv_sec ||
       (end->tv_sec == start->tv_sec && end->tv_nsec <= start->tv_nsec)) {
        return 0;
    }
    return (end->tv_sec - start->tv_sec) * 1000L +
           (end->tv_nsec - start->tv_nsec) / 1000000L;
}

static const command_t *find_soonest_command_in_queue(command_queue_t *queue)
{
    int index = 0;
    command_t *soonest_cmd = 0;

    if (queue->size == 0)
        return NULL;
    soonest_cmd = &queue->commands[queue->head];
    for (int i = 1; i < queue->size; ++i) {
        index = (queue->head + i) % MAX_COMMANDS;
        if (timespec_cmp(&queue->commands[index].ready_at, &soonest_cmd->ready_at) < 0) {
            soonest_cmd = &queue->commands[index];
        }
    }
    return soonest_cmd;
}

static long calculate_next_event_cmd(command_queue_t *queue, struct timespec now, long min_timeout)
{
    const command_t *soonest_cmd = find_soonest_command_in_queue(queue);
    long cmd_timeout = 0;

    if (soonest_cmd) {
        cmd_timeout = timespec_diff_ms(&now, &soonest_cmd->ready_at);
        if (min_timeout == -1 || cmd_timeout < min_timeout)
            min_timeout = cmd_timeout;
    }
    return min_timeout;
}

void re_spawn_ressources_duration(server_t *server)
{
    const double respawn_duration = 20.0 / server->config->freq;
    get_current_time(&server->next_respawn_time);
    add_seconds_to_timespec(&server->next_respawn_time, respawn_duration);
}

void get_next_food_consumption(session_client_t *client, server_t *server)
{
    const double food_duration = 126.0 / server->config->freq;
    add_seconds_to_timespec(&client->next_food_time, food_duration);
}

int calculate_next_event_timeout(server_t *server)
{
    struct timespec now;
    get_current_time(&now);
    const session_client_t *client = NULL;
    long food_timeout = 0;
    long min_timeout = timespec_diff_ms(&now, &server->next_respawn_time);

    for (int i = 0; i < MAX_CLIENTS; ++i) {
        client = &server->clients[i];
        if (client->fd < 0 || !client->active || client->is_gui)
            continue;
        food_timeout = timespec_diff_ms(&now, &client->next_food_time);
        if (min_timeout == -1 || food_timeout < min_timeout)
            min_timeout = food_timeout;
        if (client->queue->size > 0)
            min_timeout = calculate_next_event_cmd(client->queue, now, min_timeout);
    }
    if (min_timeout == -1)
        return 1000;
    return (int)min_timeout;
}