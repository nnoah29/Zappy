/*
** EPITECH PROJECT, 2024
** B-YEP-400-COT-4-1-zappy-noah.toffa
** File description:
** server_core.c
*/

#include <errno.h>
#include <stdio.h>
#include <signal.h>
#include "server.h"

volatile sig_atomic_t running = 1;

void handle_signal(int signal)
{
    (void)signal;
    running = 0;
    printf("\nSignal reçu, arrêt du serveur...\n");
}

void spawn_ressources(server_t *server)
{
    struct timespec now;

    get_current_time(&now);
    if (timespec_cmp(&now, &server->next_respawn_time) >= 0) {
        map_spawn_resources(server);
        re_spawn_ressources_duration(server);
    }
}

void check_life(server_t *server, int client_idx)
{
    session_client_t *client = &server->clients[client_idx];
    struct timespec now;

    get_current_time(&now);
    if (timespec_cmp(&now, &client->next_food_time) >= 0) {
        if (client->inventory[FOOD] > 0) {
            client->inventory[FOOD]--;
            get_next_food_consumption(client, server);
            // pin_f(server, client, NULL); // TODO: Notifier le GUI
        } else {
            send(client->fd, "dead\n", 5, 0);
            // pdi_f(server, client, NULL); // TODO: Notifier le GUI
            map_detach_entity(&server->map[client->y][client->x], client);
            close_client_connection(server, client_idx);
        }
    }
}

void handle_game_logic(server_t *server)
{
    spawn_ressources(server);
    for (int i = 0; i < MAX_CLIENTS; i++) {
        if (server->clients[i].fd == -1 || server->clients[i].is_egg || !server->clients[i].active)
            continue;
        exec_cmd(server, i);
        check_life(server, i);
    }
}

void run_server(server_t *server)
{
    int ready = 0;
    int timeout = 0;

    while (running) {
        timeout = calculate_next_event_timeout(server);
        ready = poll(server->fds, server->nfds, timeout);

        if (ready < 0) {
            if (errno == EINTR)
                continue;
            perror("poll");
            break;
        }
        if (ready > 0)
            handle_network_events(server);

        handle_game_logic(server);
    }
}