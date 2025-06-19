/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** Utilitaires_2.c
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../my.h"

void parse_freq(config_server_t *conf, char **argv, int *i)
{
    (*i)++;
    conf->freq = atoi(argv[*i]);
}

void parse_names(config_server_t *conf, char **argv, int *i)
{
    int j = 0;

    (*i)++;
    while (argv[*i] && argv[*i][0] != '-' && j < MAX_TEAMS) {
        conf->names[j] = strdup(argv[*i]);
        conf->names[j + 1] = NULL;
        j++;
        (*i)++;
    }
    conf->nb_teams = j;
    (*i)--;
}

void get_current_time(struct timespec *ts)
{
    clock_gettime(CLOCK_MONOTONIC, ts);
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

// Renvoie la différence entre deux timespec en millisecondes.
// Renvoie 0 si end est avant ou égal à start.
long timespec_diff_ms(const struct timespec *start, const struct timespec *end)
{
    if (end->tv_sec < start->tv_sec ||
       (end->tv_sec == start->tv_sec && end->tv_nsec <= start->tv_nsec)) {
        return 0;
    }
    return (end->tv_sec - start->tv_sec) * 1000L +
           (end->tv_nsec - start->tv_nsec) / 1000000L;
}

// Trouve la commande qui finira le plus tôt dans la file d'un client.
const command_t *find_soonest_command_in_queue(command_queue_t *queue)
{
    int index = 0;
    command_t *soonest_cmd = 0;

    if (queue->size == 0) {
        return NULL;
    }
    soonest_cmd = &queue->commands[queue->head];
    for (int i = 1; i < queue->size; ++i) {
        index = (queue->head + i) % MAX_COMMANDS;
        if (timespec_cmp(&queue->commands[index].ready_at, &soonest_cmd->ready_at) < 0) {
            soonest_cmd = &queue->commands[index];
        }
    }
    return soonest_cmd;
}

long calculate_next_event_cmd(command_queue_t *queue, struct timespec now, long min_timeout)
{
    const command_t *soonest_cmd = find_soonest_command_in_queue(queue);
    long cmd_timeout = 0;

    if (soonest_cmd) {
        cmd_timeout = timespec_diff_ms(&now, &soonest_cmd->ready_at);
        if (min_timeout == -1 || cmd_timeout < min_timeout) {
            min_timeout = cmd_timeout;
        }
    }
    return min_timeout;
}

/**
 * @brief Calcule le timeout pour poll() basé sur le prochain événement de jeu.
 *
 * @param server Le pointeur vers la structure du serveur.
 * @return Le nombre de millisecondes avant le prochain événement, ou un timeout par défaut s'il n'y a aucun événement planifié.
 */
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

int find_free_client_slot(server_t *server)
{
    for (int i = 0; i < MAX_CLIENTS; i++) {
        if (server->clients[i].fd == -1) {
            return i;
        }
    }
    return -1; // Plus de place
}


/**
 * @brief Trouve l'index d'un client dans le tableau server->clients basé sur son file descriptor.
 * @param server Le pointeur vers la structure du serveur.
 * @param fd Le file descriptor à rechercher.
 * @return L'index du client (0 à MAX_CLIENTS-1) si trouvé, sinon -1.
**/
int find_client_by_fd(server_t *server, int fd)
{
    for (int i = 0; i < MAX_CLIENTS; i++) {
        if (server->clients[i].fd == fd) {
            return i;
        }
    }
    return -1;
}