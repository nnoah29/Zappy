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
    session_client_t *client = &server->players[client_idx];
    struct timespec now;

    if (client->is_egg || !client->active || client->is_gui)
        return;
    get_current_time(&now);
    if (timespec_cmp(&now, &client->next_food_time) >= 0) {
        if (client->inventory[FOOD] > 0) {
            client->inventory[FOOD]--;
            get_next_food_consumption(client, server);
        } else {
            LOG(LOG_INFO, "Le joueur %d est mort.", client_idx);
            send(client->fd, "dead\n", 5, 0);
            pdi_f(server, client);
            map_detach_entity(&server->map[client->y][client->x], client);
            close_client_connection(server, client_idx);
        }
    }
}

void handle_game_logic(server_t *server)
{
    spawn_ressources(server);
    check_and_finish_incantations(server);
    for (int i = 0; i < MAX_CLIENTS; i++) {
        if (server->players[i].fd == -1 || server->players[i].is_egg)
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
            perror("poll");
            continue;
        }
        if (ready > 0)
            handle_network_events(server);
        handle_game_logic(server);
    }
}
